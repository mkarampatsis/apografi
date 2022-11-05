# importing the requests library
import requests
from models.Foreis import Foreis
from connection import get_database

dbname = get_database()

# api-endpoints
URL_ALL_FOREIS = "https://hr.apografi.gov.gr/api/public/organizations"
URL_MONADES = "https://hr.apografi.gov.gr/api/public/organizations"

URL_ORGANIZATIONTYPES="https://hr.apografi.gov.gr/api/public//metadata/dictionary/OrganizationTypes"
URL_UNITTYPES="https://hr.apografi.gov.gr/api/public//metadata/dictionary/UnitTypes"
URL_FUNCTIONALAREAS="https://hr.apografi.gov.gr/api/public//metadata/dictionary/FunctionalAreas"
URL_FUNCTIONS="https://hr.apografi.gov.gr/api/public//metadata/dictionary/Functions"
URL_DETAIL_FOREA ="https://hr.apografi.gov.gr/api/public/organizations/%s"

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
    print (forea_details)
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

    Foreis(**item).save()