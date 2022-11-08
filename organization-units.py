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

def processOrganizations(organization, unitTypes, functions):
    code = organization['code']
    organization_units = requests.get(url=URL_ORGANIZATION_UNITS %code).json()['data']

    for unit in organization_units:
        # print(unit)
        unitType = [x for x in unitTypes if x['id'] == unit['unitType']]
        # print (unitType)
        unit['unitType']={'id': unitType[0]['id'], 'description': unitType[0]['description']}

        purposeArray = []
        if unit.get('purpose'):
            purpose = [x for x in functions if x['id'] in unit['purpose']]
            purposeArray.append(purpose[0])
        unit['purpose']=purposeArray

        if unit.get('supervisorUnitCode'):
            supervisorUnitCode = [x for x in organization_units if x['code'] in unit['supervisorUnitCode']]
            unit['supervisorUnitCode']={'code': supervisorUnitCode[0]['code'], 'preferredLabel': supervisorUnitCode[0]['preferredLabel']}
       
        unit.pop('spatial', None)
        unit.pop('identifier', None)
        unit.pop('email', None)
        unit.pop('telephone', None)
        unit.pop('url', None)
        unit.pop('mainAddress', None)

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
    print(item)
    try:
        organization = Organization_Units.objects.get(code=code)
        print ("Organization %s exist" %code)
        
        organization = json.loads(organization.to_json())
        del organization["_id"]

        #diff = DeepDiff(organization, item, exclude_paths=["root['foundationDate']", "root['terminationDate']"])
        diff = DeepDiff(organization, item)
        # print (diff)
        if diff:
            Logs(data=str(diff)).save()
            #print(diff)
        
        # sys.exit()
        Organization_Units.objects(code=code).update_one(**item)
    except Organization_Units.DoesNotExist:
        print("Organization %s is new" %code)
        Organization_Units(**item).save()

def batch_iterator():
    organizations = Organization_Units.objects(organization_units__gt=1)
    organizations=json.loads(organizations.to_json())
    for organization in organizations:
        yield organization

def batch_run():
    unitTypes = requests.get(url=URL_UNITTYPES).json()['data']
    functions = requests.get(url=URL_FUNCTIONS).json()['data']
   
    log = {}
    log['start'] = datetime.now()
    log['application'] = "organizations"

    for item in batch_iterator():
        organization = json.loads(item.to_json())
        code = organization['code']
        print(code)
        processOrganizations(organization, unitTypes, functions)
    
    log['end'] = datetime.now()
    Logs(data=log).save()

def organization_run(code):
    item = Organizations.objects.get(code=code)
    organization = json.loads(item.to_json())
    
    unitTypes = requests.get(url=URL_UNITTYPES).json()['data']
    functions = requests.get(url=URL_FUNCTIONS).json()['data']
    
    processOrganizations(organization, unitTypes, functions)
    
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
