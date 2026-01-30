#!/usr/bin/env python3
import json
from connection import get_database
from utils import url_get, send_email
from deepdiff import DeepDiff
from datetime import datetime
import argparse
from alive_progress import alive_bar

from models.Organizations import Organizations
from models.Organizational_Units import Organizational_Units
from models.synclog import SyncLog

dbname = get_database()
# api-endpoints
# api-endpoints
API_URL = "https://hrms.gov.gr/api"
DICTIONARIES_URL = f"{API_URL}/public/metadata/dictionary/"
ORGANIZATIONS_URL = f"{API_URL}/public/organizations"
ORGANIZATION_UNITS_URL = f"{API_URL}/public/organizational-units?organizationCode=%s"
ORGANIZATION_TREE_URL = f"{API_URL}/public/organization-tree?organizationCode=%s"


def processOrganizationUnits(code, unitTypes, functions, countries, cities):
  print(f"  - Συγχρονισμός μονάδων οργανισμού: {code}...")
  # response = requests.get(url=URL_ORGANIZATION_UNITS %code).json()['data']
  response = url_get(f"{ORGANIZATION_UNITS_URL %code}").json()['data']

  with alive_bar(len(response)) as bar:
    for unit in response:
      
      unitType = [x for x in unitTypes if x['id'] == unit['unitType']]
      unit['unitType'] = unitType[0]

      purposeArray = []
      if unit.get('purpose'):
        for u in unit['purpose']:
          purpose = [x for x in functions if x['id'] == u]
          if purpose:
            purposeArray.append(purpose[0])
          else:
            purposeArray.append({'id': u, 'description': 'NotExist'})
                          
      unit['purpose']=purposeArray

      if unit.get('supervisorUnitCode'):
        supervisorUnitCode = [x for x in response if x['code'] in unit['supervisorUnitCode']]
        unit['supervisorUnitCode'] = {'code': supervisorUnitCode[0]['code'], 'preferredLabel': supervisorUnitCode[0]['preferredLabel']}
      
      unit['email'] = unit['email'] if unit.get('email') else None
      unit['telephone'] = unit['telephone'] if unit.get('telephone') else None
      unit['url'] = unit['url'] if unit.get('url') else None
      unit['identifier'] = unit['identifier'] if unit.get('identifier') else None

      spatialArray = []
      if unit.get('spatial'):
        for s in unit.get('spatial'):
          country = [x for x in countries if x['id'] == s['countryId']]
          city = [x for x in cities if x['id'] == s['countryId']]
          spatialArray.append({ 
            'country': country[0] if country else None, 
            'city': city[0] if city else None 
          })
      unit['spatial']=spatialArray

      if unit.get('mainAddress'):
        if unit['mainAddress'].get('adminUnitLevel1'):
          country = [x for x in countries if x['id'] == unit['mainAddress']['adminUnitLevel1']]
        else: 
          country = None  
        if unit['mainAddress'].get('adminUnitLevel2'):
          city = [x for x in cities if x['id'] == unit['mainAddress']['adminUnitLevel2']]
        else:
          city = None
        unit['mainAddress']={ 
          'fullAddress':unit['mainAddress']['fullAddress'] if unit['mainAddress'].get('fullAddress') else None, 
          'postCode':unit['mainAddress']['postCode'] if unit['mainAddress'].get('postCode') else None, 
          'country': country[0] if country else None, 
          'city': city[0] if city else None
        }
      else:
        unit['mainAddress'] = None

      secondaryAddressesArray = []    
      if unit.get('secondaryAddresses'):
        for s in unit.get('secondaryAddresses'):
          if s.get('adminUnitLevel1'):
            country = [x for x in countries if x['id'] == s['adminUnitLevel1']]
          else:
            country = None
          if s.get('adminUnitLevel2'):
            city = [x for x in cities if x['id'] == s['adminUnitLevel2']]
          else:
            city = None
          secondaryAddressesArray.append({ 
            'fullAddress':s['fullAddress'] if s.get('fullAddress') else None, 
            'postCode':s['postCode'] if s.get('postCode') else None, 
            'country': country[0] if country else None, 
            'city': city[0] if city else None
          })
      unit['secondaryAddresses']=secondaryAddressesArray

      # unit.pop('identifier', None)
      
      # print(unit)   
    
      item = {
        "code": unit["code"],
        "organizationCode": unit["organizationCode"],
        "supervisorUnitCode": unit["supervisorUnitCode"],
        "preferredLabel": unit["preferredLabel"],
        "alternativeLabels": unit["alternativeLabels"],
        "purpose": unit["purpose"],
        "spatial": unit["spatial"],
        "identifier": unit["identifier"],
        "unitType": unit["unitType"],
        "description": unit["description"],
        "email": unit["email"],
        "telephone": unit["telephone"],
        "url": unit["url"],
        "mainAddress": unit["mainAddress"],
        "secondaryAddresses": unit["secondaryAddresses"],
      }
      # print(item)
      # sys.exit()
      try:
        existing = Organizational_Units.objects.get(code=unit['code'])
        print ("Organization unit %s exist" %unit['code'])
        
        if existing:
          existing_dict = existing.to_mongo().to_dict()
          existing_dict.pop("_id")
          
          diff = DeepDiff(existing_dict, item, view='tree').to_json() 
          diff = json.loads(diff)
          # print (diff)
          if diff:
            print("DIFF TRUE", diff)
            for key, value in item.items():
              setattr(existing, key, value)
            # print("Existing>>",existing.to_json())
            existing.save()
            SyncLog(
                entity="organization",
                action="update",
                doc_id=item["code"],
                value=diff,
            ).save()
            # Organization_Units.objects(code=code).update_one(**item)
          
      except Organizational_Units.DoesNotExist:
        print("Organizational Unit %s is new" %unit['code'])
        Organizational_Units(**item).save()
    bar()

def batch_iterator():
  organizations = url_get(f"{ORGANIZATIONS_URL}")
  with alive_bar(len(organizations.json()["data"])) as bar:
    for organization in organizations:
      yield organization
      bar()

def batch_run():
  print("Συγχρονισμός μονάδων οργανισμού από το ΣΔΑΔ...")
  unitTypes = url_get(f"{DICTIONARIES_URL}UnitTypes").json()['data']
  functions = url_get(f"{DICTIONARIES_URL}Functions").json()['data']
  countries = url_get(f"{DICTIONARIES_URL}Countries").json()['data']
  cities = url_get(f"{DICTIONARIES_URL}Cities").json()['data']

  for item in batch_iterator():
    organization = json.loads(item.to_json())
    code = organization['code']

    start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    processOrganizationUnits(code, unitTypes, functions, countries, cities)
    end_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    send_email("organizational_units", start_time, end_time)
    print("Τέλος συγχρονισμού μονάδων οργανισμού από το ΣΔΑΔ.")

def organization_unit_run(code):
  print("Συγχρονισμός μονάδων οργανισμού από το ΣΔΑΔ...")
 
  unitTypes = url_get(f"{DICTIONARIES_URL}UnitTypes").json()['data']
  functions = url_get(f"{DICTIONARIES_URL}Functions").json()['data']
  countries = url_get(f"{DICTIONARIES_URL}Countries").json()['data']
  cities = url_get(f"{DICTIONARIES_URL}Cities").json()['data']
  
  start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  processOrganizationUnits(code, unitTypes, functions, countries, cities)
  end_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  send_email("organizational_units", start_time, end_time)
  print("Τέλος συγχρονισμού μονάδων οργανισμού από το ΣΔΑΔ.")
    
my_parser = argparse.ArgumentParser(
  prog="organization-units.py",
  usage="%(prog)s [--all] | [--code] code",
  description="Get all organization units if run in batch else specific oranization unit")

my_parser.add_argument("--all", action="store_true")
my_parser.add_argument("--code", type=str, help="give an organization unit code to process")
my_parser.add_argument("--version", action='version', version='%(prog)s 1.0')
args = my_parser.parse_args()

if args.all:
  print ("Process all")
  batch_run()
else:
  print("Process code: ", args.code)
  organization_unit_run(args.code)
