#!/usr/bin/env python3
import json
from connection import get_database
from utils import url_get, send_email, normalize_embedded
from deepdiff import DeepDiff
from datetime import datetime
import argparse
from alive_progress import alive_bar

from models.sdad.organizational_units import Organizational_Units
from models.sdad.synclog import SyncLog
import redis

dbname = get_database()
dict_cache = redis.Redis(db=1)

# api-endpoints
API_URL = "https://hrms.gov.gr/api"
ORGANIZATIONS_URL = f"{API_URL}/public/organizations"
ORGANIZATION_URL = f"{API_URL}/public/organizations/"
ORGANIZATION_UNITS_URL = f"{API_URL}/public/organizational-units?organizationCode=%s"

units_with_problems = [
  { "code":"763976", "field":"email", 'problem':'email is tm.sint.td.akiklades@efka.gov.gr  / tm.par.td.akiklades@efka.gov.gr' }
]

def processOrganizationUnits(code):  
  print(f"  - Συγχρονισμός μονάδων οργανισμού: {code}...")
  response = url_get(f"{ORGANIZATION_UNITS_URL %code}").json()['data']
  if response:
    with alive_bar(len(response)) as bar:
      for unit in response:
        print ("Processing organization unit %s" %unit['code'])
        

        if unit.get('organizationCode'):
          organizationOf = url_get(f"{ORGANIZATION_URL}{unit['organizationCode']}").json()['data']
          unit['organizationCode']={'code': organizationOf['code'], 'preferredLabel': organizationOf['preferredLabel']}
        
        unitType = dict_cache.get(f"UnitTypes:{unit['unitType']}").decode("utf-8")
        unit['unitType'] = { 'id': unit['unitType'], 'description': unitType } 

        purposeArray = []
        if unit.get('purpose'):
          for u in unit['purpose']:
            purpose = {'id': u, 'description': dict_cache.get(f"Functions:{u}").decode("utf-8")}
            if purpose:
              purposeArray.append(purpose)
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
        unit["remitsFinalized"] = unit["remitsFinalized"] if unit.get("remitsFinalized") else False

        spatialArray = []
        if unit.get('spatial'):
          for s in unit.get('spatial'):
            country = {'id': s['countryId'], "description": dict_cache.get(f"Countries:{s['countryId']}").decode("utf-8") if s['countryId'] else None }  
            city = {'id': s['dimosId'], "description": dict_cache.get(f"Cities:{s['dimosId']}").decode("utf-8") if s['dimosId'] else None , "parentId":None} 
            spatialArray.append({ 
              'country': country if country else None, 
              'city': city if city else None 
            })
        unit['spatial']=spatialArray

        if unit.get('mainAddress'):
          if unit['mainAddress'].get('adminUnitLevel1'):
            name = dict_cache.get(f"Countries:{unit['mainAddress']['adminUnitLevel1']}").decode("utf-8")
            country = {'id': unit['mainAddress']['adminUnitLevel1'], "description": name }
          else: 
            country = None  
          if unit['mainAddress'].get('adminUnitLevel2'):
            name  = dict_cache.get(f"Cities:{unit['mainAddress']['adminUnitLevel2']}").decode("utf-8")
            city = {'id': unit['mainAddress']['adminUnitLevel2'], "description": name, 'parentId':None }
          else:
            city = None
          unit['mainAddress']={ 
            'fullAddress':unit['mainAddress']['fullAddress'] if unit['mainAddress'].get('fullAddress') else None, 
            'postCode':unit['mainAddress']['postCode'] if unit['mainAddress'].get('postCode') else None, 
            'country': country if country else None, 
            'city': city if city else None
          }
        else:
          unit['mainAddress'] = None

        secondaryAddressesArray = []    
        if unit.get('secondaryAddresses'):
          for s in unit.get('secondaryAddresses'):
            if s.get('adminUnitLevel1'):
              name = dict_cache.get(f"Countries:{s['adminUnitLevel1']}").decode("utf-8")
              country = {'id': s['adminUnitLevel1'], "description": name }
            else:
              country = None
            if s.get('adminUnitLevel2'):
              name  = dict_cache.get(f"Cities:{s['adminUnitLevel2']}").decode("utf-8")
              city = {'id': s['adminUnitLevel2'], "description": name, 'parentId':None }
            else:
              city = None
            secondaryAddressesArray.append({ 
              'fullAddress':s['fullAddress'] if s.get('fullAddress') else None, 
              'postCode':s['postCode'] if s.get('postCode') else None, 
              'country': country if country else None, 
              'city': city if city else None
            })
        unit['secondaryAddresses']=secondaryAddressesArray

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
          "remitsFinalized": unit["remitsFinalized"],
          "elasticSync": unit["elasticSync"] if unit.get("elasticSync") else False
        }

        try:
          existing = Organizational_Units.objects.get(code=unit['code'])
          # print ("Organization unit %s exist" %unit['code'])
          
          if existing:
            existing_dict = existing.to_mongo().to_dict()
            existing_dict.pop("_id")
            existing_dict.pop("createdAt")
            existing_dict.pop("updatedAt")
                        
            diff = DeepDiff(existing_dict, item, ignore_order=True, view='tree').to_json() 
            diff = json.loads(diff)
            # print (diff)
            if diff:
              print("DIFF TRUE", diff)
              item = normalize_embedded(item)
              for key, value in item.items():
                setattr(existing, key, value)
              print("Existing>>",existing.to_json())
              existing.save()
              SyncLog(
                entity="organizational_unit",
                action="update",
                doc_id=item["code"],
                value=diff,
              ).save()
            
        except Organizational_Units.DoesNotExist:
          print("Organizational Unit %s is new" %unit['code'])
          Organizational_Units(**item).save()
          SyncLog( 
            entity="organizational_unit", 
            action="insert", 
            doc_id=item["code"], 
            value=item 
          ).save() 
      bar()

def batch_iterator():
  organizations = url_get(f"{ORGANIZATIONS_URL}").json()["data"]
  for organization in organizations:
    yield organization
  
def batch_run():
  print("Συγχρονισμός μονάδων οργανισμού από το ΣΔΑΔ...")

  start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
  for item in batch_iterator():
    code = item['code']
    processOrganizationUnits(code)
  
  end_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  send_email("organizational_units", start_time, end_time)
  print("Τέλος συγχρονισμού μονάδων οργανισμού από το ΣΔΑΔ.")

def organization_unit_run(code):
  print("Συγχρονισμός μονάδων οργανισμού από το ΣΔΑΔ...")
 
  start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  processOrganizationUnits(code)
  end_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  send_email("organizational_units", start_time, end_time)
  print("Τέλος συγχρονισμού μονάδων οργανισμού από το ΣΔΑΔ.")
    
my_parser = argparse.ArgumentParser(
  prog="sdad_sync_organizational-units.py",
  usage="%(prog)s [--all] | [--code] code",
  description="Get all organization units if run in batch else specific oranization unit")

my_parser.add_argument("--all", action="store_true")
my_parser.add_argument("--code", type=str, help="give an organization code to process")
my_parser.add_argument("--version", action='version', version='%(prog)s 1.0')
args = my_parser.parse_args()

if args.all:
  print ("Process all")
  batch_run()
else:
  print("Process code: ", args.code)
  organization_unit_run(args.code)