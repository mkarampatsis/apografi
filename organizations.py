#!/usr/bin/env python3
import requests
import json
from connection import get_database
from utils import url_get, send_email
from pprint import *
from deepdiff import DeepDiff
from datetime import datetime
from datetime import timedelta
import argparse
from alive_progress import alive_bar

from models.Organizations import Organizations
from models.synclog import SyncLog

dbname = get_database()

# api-endpoints
APOGRAFI = "https://hrms.gov.gr/api/public"
APOGRAFI_DICTS = f"{APOGRAFI}/metadata/dictionary"
APOGRAFI_ORGANIZATIONS = f"{APOGRAFI}/organizations/"

URL_UNITTYPES = f"{APOGRAFI_DICTS}/UnitTypes"
URL_SPECIALITES = f"{APOGRAFI_DICTS}/Specialities"
URL_SPECIALPOSITIONS  = f"{APOGRAFI_DICTS}/SpecialPositions"
URL_RANKS = f"{APOGRAFI_DICTS}/Ranks"
URL_PROFESSIONCATEGORIES = f"{APOGRAFI_DICTS}/ProfessionCategories"
URL_ORGANIZATIONTYPES = f"{APOGRAFI_DICTS}/OrganizationTypes"
URL_ORGANIZATIONCATEGORIES = f"{APOGRAFI_DICTS}/OrganizationCategories"
URL_FUNCTIONS = f"{APOGRAFI_DICTS}/Functions"
URL_FUNCTIONALAREAS = f"{APOGRAFI_DICTS}/FunctionalAreas"
URL_EMPLOYMENTTYPES  = f"{APOGRAFI_DICTS}/EmploymentTypes"
URL_EMPLOYEECATEGORIES = f"{APOGRAFI_DICTS}/EmployeeCategories"
URL_EDUCATIONTYPES = f"{APOGRAFI_DICTS}/EducationTypes"
URL_DUTYTYPES = f"{APOGRAFI_DICTS}/DutyTypes"
URL_COUNTRIES = f"{APOGRAFI_DICTS}/Countries"
URL_CITIES = f"{APOGRAFI_DICTS}/Cities"

API_URL = "https://hrms.gov.gr/api"
DICTIONARIES_URL = f"{API_URL}/public/metadata/dictionary/"

DICTIONARIES = {
  "UnitTypes": "Επιστρέφει όλες τους τύπους μονάδων που περιέχονται στο αντίστοιχο λεξικό του ΣΔΑΔ",
  "Specialities": "Επιστρέφει όλες τις ειδικότητες που περιέχονται στο αντίστοιχο λεξικό του ΣΔΑΔ",
  "SpecialPositions":"Επιστρέφει όλες τις ειδικές θέσεις που περιέχονται στο αντίστοιχο λεξικό του ΣΔΑΔ",
  "Ranks":"Επιστρέφει όλους τους βαθμούς που περιέχονται στο αντίστοιχο λεξικό του ΣΔΑΔ",
  "ProfessionCategories": "Επιστρέφει όλους τους κλάδους που περιέχονται στο αντίστοιχο λεξικό του ΣΔΑΔ",
  "OrganizationTypes": "Επιστρέφει όλες τους τύπους φορέων που περιέχονται στο αντίστοιχο λεξικό του ΣΔΑΔ",
  "OrganizationCategories": "Επιστρέφει όλες τις κατηγορίες φορέων που περιέχονται στο αντίστοιχο λεξικό του ΣΔΑΔ",
  "Functions": "Επιστρέφει όλες τις λειτουργίες που περιέχονται στο αντίστοιχο λεξικό του ΣΔΑΔ",
  "FunctionalAreas": "Επιστρέφει όλους τους τομείς πολιτικής που περιέχονται στο αντίστοιχο λεξικό του ΣΔΑΔ",
  "EmploymentTypes": "Επιστρέφει όλες τις εργασιακές σχέσεις που περιέχονται στο αντίστοιχο λεξικό του ΣΔΑΔ",
  "EmployeeCategories": "Επιστρέφει όλες τις κατηγορίες προσωπικού που περιέχονται στο αντίστοιχο λεξικό του ΣΔΑΔ",
  "EducationTypes": "Επιστρέφει όλες τις κατηγορίες εκπαίδευσης που περιέχονται στο αντίστοιχο λεξικό του ΣΔΑΔ",
  "DutyTypes": "Επιστρέφει όλα τα καθήκοντα θέσης απασχόλησης που περιέχονται στο αντίστοιχο λεξικό του ΣΔΑΔ",
  "Countries": "Επιστρέφει όλες τις χώρες που περιέχονται στο αντίστοιχο λεξικό του ΣΔΑΔ",
  "Cities": "Επιστρέφει όλους τους δήμους που περιέχονται στο αντίστοιχο λεξικό του ΣΔΑΔ"
}

def processOrganizations(code, organizationTypes, unitTypes, functionalAreas, functions, organizations, countries, cities):
  
  print(f"  - Συγχρονισμός οργανισμού: {code}...")
  response = url_get(f"{APOGRAFI_ORGANIZATIONS}{code}")
  organization_details = requests.get(url=URL_DETAIL_ORGANIZATION %code).json()['data']

  # print ("1>>",organization_details)
      
  organizationType = [x for x in organizationTypes if x['id'] == organization_details['organizationType']]
  organization_details['organizationType']=organizationType[0]

  if organization_details.get('subOrganizationOf'):
    subOrganizationOf = [x for x in organizations if x['code'] == organization_details['subOrganizationOf']]
    if not subOrganizationOf:
      subOrganizationOf = requests.get(url=URL_DETAIL_ORGANIZATION %organization_details['subOrganizationOf']).json()['data']
      organization_details['subOrganizationOf']={'code': subOrganizationOf['code'], 'preferredLabel': subOrganizationOf['preferredLabel']}
    else:
      organization_details['subOrganizationOf']={'code': subOrganizationOf[0]['code'], 'preferredLabel': subOrganizationOf[0]['preferredLabel']}
      # print (organization_details)
      # sys.exit()
      
  purposeArray = []
  if organization_details.get('purpose'):
    purpose = [x for x in functions if x['id'] in organization_details['purpose']]
    purposeArray.append(purpose[0])
  organization_details['purpose']=purposeArray

  organization_units = requests.get(url=URL_ORGANIZATIONS_UNITS %code).json()
  if organization_units.get('data'):
    organization_units = len(organization_units['data'])
  else:
    organization_units=0

  spatialArray = []
  if organization_details.get('spatial'):
    for s in organization_details.get('spatial'):
      country = [x for x in countries if x['id'] == s['countryId']]
      city = [x for x in cities if x['id'] == s['countryId']]
      spatialArray.append({ 
        'country': country[0] if country else None, 
        'city': city[0] if city else None 
      })
  organization_details['spatial']=spatialArray

  if organization_details.get('mainAddress'):
    if organization_details['mainAddress'].get('adminUnitLevel1'):
      mainCountry = [x for x in countries if x['id'] == organization_details['mainAddress']['adminUnitLevel1']]
    else: 
      mainCountry = None  
    if organization_details['mainAddress'].get('adminUnitLevel2'):
      mainCity = [x for x in cities if x['id'] == organization_details['mainAddress']['adminUnitLevel2']]
    else:
      mainCity = None
    organization_details['mainAddress']={ 
      'fullAddress':organization_details['mainAddress']['fullAddress'] if organization_details['mainAddress'].get('fullAddress') else None, 
      'postCode':organization_details['mainAddress']['postCode'] if organization_details['mainAddress'].get('postCode') else None, 
      'country': mainCountry[0] if mainCountry else None, 
      'city': mainCity[0] if mainCity else None
    }

  secondaryAddressesArray = []    
  if organization_details.get('secondaryAddresses'):
    for s in organization_details.get('secondaryAddresses'):
      if s.get('adminUnitLevel1'):
        country = [x for x in countries if x['id'] == s['adminUnitLevel1']]
      else:
        country = None
      if s.get('adminUnitLevel2'):
        city = [x for x in cities if x['id'] == s['adminUnitLevel2']]
      else:
        city = None
      secondaryAddressesArray.append({ 
        'fullAddress':s['fullAddress'], 
        'postCode':s['postCode'], 
        'country': country[0] if country else None, 
        'city': city[0] if city else None
      })
  organization_details['secondaryAddresses']=secondaryAddressesArray      

  item = {
    "code" : organization_details['code'],
    "preferredLabel" : organization_details['preferredLabel'],
    "alternativeLabels" : organization_details['alternativeLabels'] if organization_details.get('alternativeLabels') else [],
    "purpose" : organization_details['purpose'],
    "identifier" : organization_details['identifier'] if organization_details.get('identifier') else '',
    "subOrganizationOf" : organization_details['subOrganizationOf'] if organization_details.get('subOrganizationOf') else None,
    "organizationType"  : organization_details['organizationType'],
    "description" : organization_details['description'] if organization_details.get('description') else '',
    "status" : organization_details['status'] if organization_details.get('status') else '',
    "foundationDate" : organization_details['foundationDate'] if organization_details.get('foundationDate') else None,
    "terminationDate" : organization_details['terminationDate'] if organization_details.get('terminationDate') else None,
    "foundationFek" : organization_details['foundationFek'] if organization_details.get('foundationFek') else None,
    "organization_units":organization_units, 
    "spatial": organization_details['spatial'],
    "contactPoint": organization_details['contactPoint'] if organization_details.get('contactPoint') else None,
    "mainAddress": organization_details['mainAddress'] if organization_details.get('mainAddress') else None,
    "secondaryAddresses": organization_details['secondaryAddresses']
  }
  
  try:
    organization = Organizations.objects.get(code=organization_details['code'])
    print ("Organization %s exist" %organization_details['code'])
    
    organization = json.loads(organization.to_json())
    del organization["_id"]

    if organization.get("foundationDate"):
      if organization["foundationDate"]["$date"]<0:
        date = (datetime(1970, 1, 1) + timedelta(seconds=(int(organization["foundationDate"]['$date'])/1000))).strftime('%Y-%m-%d')
      else:
        date = datetime.fromtimestamp(int(organization["foundationDate"]['$date'])/1000).strftime('%Y-%m-%d')
      organization['foundationDate'] = date
    
    if organization.get("terminationDate"):
      date = datetime.fromtimestamp(int(organization["terminationDate"]['$date'])/1000).strftime('%Y-%m-%d')
      organization['terminationDate'] = date

    #diff = DeepDiff(organization, item, exclude_paths=["root['foundationDate']", "root['terminationDate']", "root['foundationFek']"])
    diff = DeepDiff(organization, item).to_json()
    # print (">>",diff)
    if diff:
      Logs(data=diff).save()
      #print(diff)
      # sys.exit()
      Organizations.objects(code=organization_details['code']).update_one(**item)
  except Organizations.DoesNotExist:
    print("Organization %s is new" %organization_details['code'])
    Organizations(**item).save()

def batch_run():
  organizationTypes = requests.get(url=URL_ORGANIZATIONTYPES).json()['data']
  unitTypes = requests.get(url=URL_UNITTYPES).json()['data']
  functionalAreas = requests.get(url=URL_FUNCTIONALAREAS).json()['data']
  functions = requests.get(url=URL_FUNCTIONS).json()['data']
  countries = requests.get(url=URL_COUNTRIES).json()['data']
  cities = requests.get(url=URL_CITIES).json()['data']

  organizations = requests.get(url = URL_ALL_ORGANIZATIONS).json()['data']

  log = {}
  log['start'] = datetime.now()
  log['application'] = "organizations"

  for organization in organizations:
    code = organization['code']
    print(code)
    processOrganizations(code, organizationTypes, unitTypes, functionalAreas, functions, organizations, countries, cities)
  
  log['end'] = datetime.now()
  Logs(data=log).save()

def organization_run(code):
  print("Συγχρονισμός οργανισμού από το ΣΔΑΔ...")
  organizationTypes = requests.get(url=URL_ORGANIZATIONTYPES).json()['data']
  unitTypes = requests.get(url=URL_UNITTYPES).json()['data']
  functionalAreas = requests.get(url=URL_FUNCTIONALAREAS).json()['data']
  functions = requests.get(url=URL_FUNCTIONS).json()['data']
  countries = requests.get(url=URL_COUNTRIES).json()['data']
  cities = requests.get(url=URL_CITIES).json()['data']

  organizations = requests.get(url = URL_ALL_ORGANIZATIONS).json()['data']
  start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  processOrganizations(code, organizationTypes, unitTypes, functionalAreas, functions, organizations, countries, cities)
  end_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  send_email("dictionaries", start_time, end_time)
  print("Τέλος συγχρονισμού οργανισμού από το ΣΔΑΔ.")
    
my_parser = argparse.ArgumentParser(
  prog="organizations.py",
  usage="%(prog)s [--all] | [--code] code",
  description="Get all organization unit if run in batch else specific oranization unit")

my_parser.add_argument("--all", action="store_true")
my_parser.add_argument("--code", type=str, help="give an organization unit code to process")
my_parser.add_argument("--version", action='version', version='%(prog)s 1.0')
args = my_parser.parse_args()

if args.all:
  print ("Process all")
  batch_run()
else:
  print("Process code: ", args.code)
  organization_run(args.code)
