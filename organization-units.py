#!/usr/bin/env python3
import requests
import json
import sys
from connection import get_database
from pprint import *
from deepdiff import DeepDiff
from datetime import datetime
from datetime import timedelta
import argparse

from models.Organizations import Organizations
from models.Organization_Units import Organization_Units
from models.Logs import Logs

dbname = get_database()
# api-endpoints
APOGRAFI = "https://hr.apografi.gov.gr/api/public"
APOGRAFI_DICTS = f"{APOGRAFI}/metadata/dictionary"

URL_ORGANIZATION_UNITS = f"{APOGRAFI}/organizational-units?organizationCode=%s"
URL_ORGANIZATION_TREE = f"{APOGRAFI}/organization-tree?organizationCode=%s"

URL_UNITTYPES = f"{APOGRAFI_DICTS}/UnitTypes"
URL_FUNCTIONS = f"{APOGRAFI_DICTS}/Functions"
URL_COUNTRIES = f"{APOGRAFI_DICTS}/Countries"
URL_CITIES = f"{APOGRAFI_DICTS}/Cities"

def processOrganizations(organization, unitTypes, functions, countries, cities):
  code = organization['code']
  organization_units = requests.get(url=URL_ORGANIZATION_UNITS %code).json()['data']

  # print(">>>",organization)

  for unit in organization_units:
    # print(unit)
    unitType = [x for x in unitTypes if x['id'] == unit['unitType']]
    # print (unitType)
    unit['unitType']={'id': unitType[0]['id'], 'description': unitType[0]['description']}

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
      supervisorUnitCode = [x for x in organization_units if x['code'] in unit['supervisorUnitCode']]
      unit['supervisorUnitCode'] = {'code': supervisorUnitCode[0]['code'], 'preferredLabel': supervisorUnitCode[0]['preferredLabel']}
    
    unit['email'] = unit['email'] if unit.get('email') else None
    unit['telephone'] = unit['telephone'] if unit.get('telephone') else None
    unit['url'] = unit['url'] if unit.get('url') else None

    spatialArray = []
    if unit.get('spatial'):
      for s in unit.get('spatial'):
        spatialCountry = [x for x in countries if x['id'] == s['countryId']]
        spatialCity = [x for x in cities if x['id'] == s['countryId']]
        if not spatialCountry or not spatialCity:
          spatialArray.append({ 'country': {'id': 0, 'description':'NotExist'}, 'city': {'id': 0, 'description':'NotExist', 'parentId':17238} })
        else:
          spatialArray.append({ 'country': spatialCountry[0], 'city': spatialCity[0] })
    unit['spatial']=spatialArray

    if unit.get('mainAddress'):
      if unit['mainAddress'].get('adminUnitLevel1'):
        mainCountry = [x for x in countries if x['id'] == unit['mainAddress']['adminUnitLevel1']]
      else: 
        mainCountry = None  
      if unit['mainAddress'].get('adminUnitLevel2'):
        mainCity = [x for x in cities if x['id'] == unit['mainAddress']['adminUnitLevel2']]
      else:
        mainCity = None
      unit['mainAddress']={ 
        'fullAddress':unit['mainAddress']['fullAddress'] if unit['mainAddress'].get('fullAddress') else None, 
        'postCode':unit['mainAddress']['postCode'] if unit['mainAddress'].get('postCode') else None, 
        'country': mainCountry[0] if mainCountry else None, 
        'city': mainCity[0] if mainCity else None
      }
    else:
      unit['mainAddress'] = None

    secondaryAddressesArray = []    
    if unit.get('secondaryAddresses'):
      for s in unit.get('secondaryAddresses'):
        mainCountry = [x for x in countries if x['id'] == s['adminUnitLevel1']]
        mainCity = [x for x in cities if x['id'] == s['adminUnitLevel2']]
        if not mainCountry or not mainCity:
          secondaryAddressesArray.append({ 
            'fullAddress':s['fullAddress'], 
            'postCode':s['postCode'], 
            'country': 'NotExist', 
            'city': 'NotExist'
          })
        else:
          secondaryAddressesArray.append({ 
            'fullAddress':s['fullAddress'], 
            'postCode':s['postCode'], 
            'country': mainCountry[0], 
            'city': mainCity[0]
          })
    unit['secondaryAddresses']=secondaryAddressesArray

    unit.pop('identifier', None)
    
    # print(unit)   
  
  item = {
    "code" : organization['code'],
    "preferredLabel" : organization['preferredLabel'],
    "alternativeLabels" : organization['alternativeLabels'],
    "purpose" : organization['purpose'],
    "subOrganizationOf" : organization['subOrganizationOf'],
    "organizationType"  : organization['organizationType'],
    "description" : organization['description'],
    "units":organization_units
  }
  # print(item)
  # sys.exit()
  try:
    organization = Organization_Units.objects.get(code=code)
    print ("Organization %s exist" %code)
    
    organization = json.loads(organization.to_json())
    del organization["_id"]

    #diff = DeepDiff(organization, item, exclude_paths=["root['foundationDate']", "root['terminationDate']"])
    diff = DeepDiff(organization, item).to_json()
    # print (diff)
    if diff:
      Logs(data=diff).save()
      #print(diff)
      # sys.exit()
      Organization_Units.objects(code=code).update_one(**item)
      
  except Organization_Units.DoesNotExist:
    print("Organization %s is new" %code)
    Organization_Units(**item).save()

def batch_iterator():
  organizations = Organizations.objects(organization_units__gte=1)
  for organization in organizations:
    yield organization

def batch_run():
  unitTypes = requests.get(url=URL_UNITTYPES).json()['data']
  functions = requests.get(url=URL_FUNCTIONS).json()['data']
  countries = requests.get(url=URL_COUNTRIES).json()['data']
  cities = requests.get(url=URL_CITIES).json()['data']
  
  log = {}
  log['start'] = datetime.now()
  log['application'] = "organizations"

  for item in batch_iterator():
    organization = json.loads(item.to_json())
    # print (item)
    code = organization['code']
    print(code)
    processOrganizations(organization, unitTypes, functions, countries, cities)
  
  log['end'] = datetime.now()
  Logs(data=log).save()

def organization_run(code):
  item = Organizations.objects.get(code=code)
  organization = json.loads(item.to_json())
  
  unitTypes = requests.get(url=URL_UNITTYPES).json()['data']
  functions = requests.get(url=URL_FUNCTIONS).json()['data']
  countries = requests.get(url=URL_COUNTRIES).json()['data']
  cities = requests.get(url=URL_CITIES).json()['data']
  
  processOrganizations(organization, unitTypes, functions, countries, cities)
    
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
