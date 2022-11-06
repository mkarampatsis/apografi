# importing the requests library
import requests
import json
import sys
from connection import get_database
from pprint import *
from deepdiff import DeepDiff
from datetime import datetime

from models.Foreis import Foreis
from models.Logs import Logs

dbname = get_database()

# api-endpoints
APOGRAFI = "https://hr.apografi.gov.gr/api/public"
URL_ALL_FOREIS = f"{APOGRAFI}/organizations"
URL_MONADES = f"{APOGRAFI}/organizations"

URL_ORGANIZATIONTYPES = f"{APOGRAFI}/metadata/dictionary/OrganizationTypes"
URL_UNITTYPES = f"{APOGRAFI}/metadata/dictionary/UnitTypes"
URL_FUNCTIONALAREAS = f"{APOGRAFI}/metadata/dictionary/FunctionalAreas"
URL_FUNCTIONS = f"{APOGRAFI}/metadata/dictionary/Functions"
URL_DETAIL_FOREA  = f"{APOGRAFI}/organizations/%s"

organizationTypes = requests.get(url=URL_ORGANIZATIONTYPES).json()['data']
unitTypes = requests.get(url=URL_UNITTYPES).json()['data']
functionalAreas = requests.get(url=URL_FUNCTIONALAREAS).json()['data']
functions = requests.get(url=URL_FUNCTIONS).json()['data']

foreis = requests.get(url = URL_ALL_FOREIS).json()['data']

for forea in foreis:

    print(forea['code'])

    forea_details = requests.get(url=URL_DETAIL_FOREA %forea['code']).json()['data']
    
    organizationType = [x for x in organizationTypes if x['id'] == forea_details['organizationType']]
    forea_details['organizationType']=organizationType[0]

    if forea_details.get('subOrganizationOf'):
        subOrganizationOf = [x for x in foreis if x['code'] == forea_details['subOrganizationOf']]
        forea_details['subOrganizationOf']={'code': subOrganizationOf[0]['code'], 'preferredLabel': subOrganizationOf[0]['preferredLabel']}

    purposeArray = []
    if forea_details.get('purpose'):
        purpose = [x for x in functions if x['id'] in forea_details['purpose']]
        purposeArray.append(purpose[0])
        
    forea_details['purpose']=purposeArray
    item = {
        "code" : forea_details['code'],
        "preferredLabel" : forea_details['preferredLabel'],
        "alternativeLabels" : forea_details['alternativeLabels'] if forea_details.get('alternativeLabels') else [],
        "purpose" : forea_details['purpose'],
        "identifier" : forea_details['identifier'] if forea_details.get('identifier') else '',
        "subOrganizationOf" : forea_details['subOrganizationOf'] if forea_details.get('subOrganizationOf') else {},
        "organizationType"  : forea_details['organizationType'],
        "description" : forea_details['description'] if forea_details.get('description') else '',
        "status" : forea_details['status'] if forea_details.get('status') else '',
        "foundationDate" : forea_details['foundationDate'] if forea_details.get('foundationDate') else None,
        "terminationDate" : forea_details['terminationDate'] if forea_details.get('terminationDate') else None,
        "foundationFek" : forea_details['foundationFek'] if forea_details.get('foundationFek') else {}
    }

    try:
        foreas = Foreis.objects.get(code=forea_details['code'])
        print ("Foreas %s exist" %forea_details['code'])
        
        foreas = json.loads(foreas.to_json())
        del foreas["_id"]
        date = datetime.fromtimestamp(int(foreas["foundationDate"]['$date'])/1000).strftime('%Y-%m-%d')
        foreas['foundationDate'] = date
        
        if foreas.get("terminationDate"):
            date = datetime.fromtimestamp(int(foreas["terminationDate"]['$date'])/1000).strftime('%Y-%m-%d')
            foreas['terminationDate'] = date

        #diff = DeepDiff(foreas, item, exclude_paths=["root['foundationDate']", "root['terminationDate']"])
        diff = DeepDiff(foreas, item)
        if diff:
            # Logs(**diff).save()
            print(diff)
        
        # sys.exit()
        Foreis.objects(code=forea_details['code']).update_one(**item)
    except Foreis.DoesNotExist:
        print("Foreas %s is new" %forea_details['code'])
        Foreis(**item).save()
