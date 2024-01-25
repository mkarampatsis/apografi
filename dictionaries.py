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
from mongoengine.queryset.visitor import Q

from models.Dictionaries import Dictionaries
from models.Logs import Logs

dbname = get_database()
# api-endpoints
APOGRAFI = "https://hr.apografi.gov.gr/api/public"
APOGRAFI_DICTS = f"{APOGRAFI}/metadata/dictionary"

URL_ORGANIZATIONTYPES = f"{APOGRAFI_DICTS}/OrganizationTypes"
URL_ORGANIZATIONCATEGORIES = f"{APOGRAFI_DICTS}/OrganizationCategories"
URL_EMPLOYMENTTYPES  = f"{APOGRAFI_DICTS}/EmploymentTypes"
URL_SUPERVISORPOSITIONS  = f"{APOGRAFI_DICTS}/SupervisorPositions"
URL_UNITTYPES = f"{APOGRAFI_DICTS}/UnitTypes"
URL_FUNCTIONS = f"{APOGRAFI_DICTS}/Functions"
URL_FUNCTIONALAREAS = f"{APOGRAFI_DICTS}/FunctionalAreas"
URL_PROFESSIONCATEGORIES = f"{APOGRAFI_DICTS}/ProfessionCategories"
URL_SPECIALITES = f"{APOGRAFI_DICTS}/Specialities"
URL_EDUCATIONTYPES = f"{APOGRAFI_DICTS}/EducationTypes"
URL_COUNTRIES = f"{APOGRAFI_DICTS}/Countries"
URL_CITIES = f"{APOGRAFI_DICTS}/Cities"

dictionaries = [ 
  URL_ORGANIZATIONTYPES, 
  URL_ORGANIZATIONCATEGORIES,
  URL_EMPLOYMENTTYPES,
  URL_SUPERVISORPOSITIONS,
  URL_UNITTYPES,
  URL_FUNCTIONS,
  URL_FUNCTIONALAREAS, 
  URL_PROFESSIONCATEGORIES,
  URL_SPECIALITES,
  URL_EDUCATIONTYPES,
  URL_COUNTRIES,
  URL_CITIES
]

def processDictionaries(dictionary):
  print(">>",dictionary)
  data = requests.get(url=dictionary).json()['data']

  for item in data:

    obj = {
      "id" : item['id'],
      "description" : item['description'],
      "parentId" : item['parentId'] if 'parentId' in item else '',
      "dictionary" : dictionary.split('/')[-1],
    }

    if obj['parentId'] == '':
      del obj["parentId"]
    
    print("1>>",obj)
  
    try:
      lexicon = Dictionaries.objects.get(Q(id = obj['id']) & Q(dictionary = obj['dictionary']))
      print ("Check if id %s exists" % obj['id'])
      
      lexicon = json.loads(lexicon.to_json())
      del lexicon["_id"]

      diff = DeepDiff(lexicon, obj).to_json()
      print ("Diff >>",diff)
      if diff:
        Logs(data=diff).save()
        print("DIFF Update")
        # sys.exit()
        Dictionaries.objects(Q(id = obj['id']) & Q(dictionary = obj['dictionary'])).update_one(**obj)
    except Dictionaries.DoesNotExist:
      print("Dictionary %s is new" %obj['id'])
      Dictionaries(**obj).save()

def batch_run():

  log = {}
  log['start'] = datetime.now()
  log['application'] = "organizations"

  for dictionary in dictionaries:
    processDictionaries(dictionary)
  
  log['end'] = datetime.now()
  Logs(data=log).save()

def organization_run(code):
  unitTypes = requests.get(url=URL_UNITTYPES).json()['data']
  functionalAreas = requests.get(url=URL_FUNCTIONALAREAS).json()['data']
  functions = requests.get(url=URL_FUNCTIONS).json()['data']
  countries = requests.get(url=URL_COUNTRIES).json()['data']
  cities = requests.get(url=URL_CITIES).json()['data']

  # organizations = requests.get(url = URL_ALL_ORGANIZATIONS).json()['data']
  
  # processOrganizations(code, organizationTypes, unitTypes, functionalAreas, functions, organizations, countries, cities)
    
my_parser = argparse.ArgumentParser(
  prog="dictionaries.py",
  usage="%(prog)s [--all] | [--code] code",
  description="Get all dictionaries if run in batch else specific dictionaries")

my_parser.add_argument("--all", action="store_true")
my_parser.add_argument("--code", type=str, help="give a dictionary to process")
my_parser.add_argument("--version", action='version', version='%(prog)s 1.0')
args = my_parser.parse_args()

if args.all:
  print ("Process all")
  batch_run()
else:
  print("Process code: ", args.code)
  organization_run(args.code)
