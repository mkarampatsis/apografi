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
API_URL = "https://hrms.gov.gr/api"
DICTIONARIES_URL = f"{API_URL}/public/metadata/dictionary/"
ORGANIZATIONS_URL = f"{API_URL}/organizations/"

def processOrganizations(code, organizationTypes, countries, cities):
  
  print(f"  - Συγχρονισμός οργανισμού: {code}...")
  response = url_get(f"{ORGANIZATIONS_URL}{code}").json()['data']
  
  print ("1>>",response)
      
  organizationType = [x for x in organizationTypes if x['id'] == response['organizationType']]
  response['organizationType']={'id': organizationType['id'], 'description': organizationType['description']}

  if response.get('subOrganizationOf'):
    subOrganizationOf = url_get(f"{ORGANIZATIONS_URL}{response['subOrganizationOf']}").json()['data']
    if not subOrganizationOf:
      response['subOrganizationOf']={'code': subOrganizationOf['code'], 'preferredLabel': subOrganizationOf['preferredLabel']}
    else:
      response['subOrganizationOf']={'code': subOrganizationOf[0]['code'], 'preferredLabel': subOrganizationOf[0]['preferredLabel']}
      # print (response)
      # sys.exit()
      
  if response.get('mainAddress'):
    if response['mainAddress'].get('adminUnitLevel1'):
      mainCountry = [x for x in cities if x['id'] == response['mainAddress']['adminUnitLevel1']]
    else: 
      mainCountry = None  
    if response['mainAddress'].get('adminUnitLevel2'):
      mainCity = [x for x in cities if x['id'] == response['mainAddress']['adminUnitLevel2']]
    else:
      mainCity = None
    response['mainAddress']={ 
      'fullAddress':response['mainAddress']['fullAddress'] if response['mainAddress'].get('fullAddress') else None, 
      'postCode':response['mainAddress']['postCode'] if response['mainAddress'].get('postCode') else None, 
      'country': mainCountry[0] if mainCountry else None, 
      'city': mainCity[0] if mainCity else None
    }

  item = {
    "code" : response['code'],
    "preferredLabel" : response['preferredLabel'],
    "subOrganizationOf" : response['subOrganizationOf'] if response.get('subOrganizationOf') else None,
    "organizationType"  : response['organizationType'],
    "description" : response['description'] if response.get('description') else '',
    "url": response['url'] if response.get('url') else '',
    "contactPoint": response['contactPoint'] if response.get('contactPoint') else '',
    "vatId": response['vatId'] if response.get('vatId') else '',
    "status" : response['status'] if response.get('status') else '',
    "foundationDate" : response['foundationDate'] if response.get('foundationDate') else None,
    "terminationDate" : response['terminationDate'] if response.get('terminationDate') else None,
    "mainDataUpdateDate" : response['mainDataUpdateDate'] if response.get('mainDataUpdateDate') else None,
    "organizationStructureUpdateDate" : response['organizationStructureUpdateDate'] if response.get('mainDaorganizationStructureUpdateDatetaUpdateDate') else None,
    "foundationFek" : response['foundationFek'] if response.get('foundationFek') else None,
    "mainAddress": response['mainAddress'] if response.get('mainAddress') else None,
  }

  try:
    existing = Organizations.objects.get(code=response['code'])
    print ("Organization %s exist" %response['code'])
    
    if existing:
      existing_dict = existing.to_mongo().to_dict()
      existing_dict.pop("_id")
    # organization = json.loads(organization.to_json())
    # del organization["_id"]

    # if organization.get("foundationDate"):
    #   if organization["foundationDate"]["$date"]<0:
    #     date = (datetime(1970, 1, 1) + timedelta(seconds=(int(organization["foundationDate"]['$date'])/1000))).strftime('%Y-%m-%d')
    #   else:
    #     date = datetime.fromtimestamp(int(organization["foundationDate"]['$date'])/1000).strftime('%Y-%m-%d')
    #   organization['foundationDate'] = date
    
    # if organization.get("terminationDate"):
    #   date = datetime.fromtimestamp(int(organization["terminationDate"]['$date'])/1000).strftime('%Y-%m-%d')
    #   organization['terminationDate'] = date

    #diff = DeepDiff(organization, item, exclude_paths=["root['foundationDate']", "root['terminationDate']", "root['foundationFek']"])
    # diff = DeepDiff(organization, item).to_json()
    diff = DeepDiff(existing_dict, item, view='tree').to_json() 
    diff = json.loads(diff)
    # print (">>",diff)
    if diff:
      for key, value in item.items():
          setattr(existing, key, value)
      existing.save()
      SyncLog(
          entity="organization",
          action="update",
          doc_id=item["code"],
          value=diff,
      ).save()
      #print(diff)
      # sys.exit()
      Organizations.objects(code=response['code']).update_one(**item)
  except Organizations.DoesNotExist:
    print("Organization %s is new" %response['code'])
    Organizations(**item).save()
    SyncLog(
      entity="organization", action="insert", doc_id=item["code"], value=item
    ).save()

def batch_run():
  print("Συγχρονισμός οργανισμού από το ΣΔΑΔ...")
  organizationTypes = url_get(f"{DICTIONARIES_URL}OrganizationTypes").json()['data']
  countries = url_get(f"{DICTIONARIES_URL}Countries").json()['data']
  cities = url_get(f"{DICTIONARIES_URL}Cities").json()['data']

  organizations = url_get(f"{ORGANIZATIONS_URL}")
  with alive_bar(len(organizations)) as bar:
    for organization in organizations.json()["data"]:
      code = organization['code']
      start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
      processOrganizations(code, organizationTypes, countries, cities)
      bar()
  end_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  send_email("dictionaries", start_time, end_time)
  print("Τέλος συγχρονισμού οργανισμού από το ΣΔΑΔ.")
  
  

def organization_run(code):
  print("Συγχρονισμός οργανισμού από το ΣΔΑΔ...")
  organizationTypes = url_get(f"{DICTIONARIES_URL}OrganizationTypes").json()['data']
  countries = url_get(f"{DICTIONARIES_URL}Countries").json()['data']
  cities = url_get(f"{DICTIONARIES_URL}Cities").json()['data']

  start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  processOrganizations(code, organizationTypes, countries, cities)
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
