#!/usr/bin/env python3
import json
import sys
from connection import get_database
from pprint import *

import argparse

from models.organizational_units import Organization_Units

dbname = get_database()

purpose = []

def processOrganizations(organization, f):
    code = organization['code']
    preferredLabel = organization['preferredLabel']

    print (code, preferredLabel)
    
    if organization['purpose']:
      for p in organization['purpose']:
        found = [x for x in purpose if x==p['id']]
        if not found: 
          print("Not Found", p['id'])
          purpose.append(p['id'])
          f.write("%s, %s" % (p['id'], p['description']))
          f.write('\n')
    
    for unit in organization['units']:
        if unit['purpose']:
          for p in unit['purpose']:
            found = [x for x in purpose if x==p['id']]
            if not found: 
              print("Not Found", p['id'])
              purpose.append(p['id'])
              f.write("%s, %s" % (p['id'], p['description']))
              f.write('\n')

def batch_iterator():
    organizations = Organization_Units.objects()
    for organization in organizations:
        yield organization

def batch_run():
    f = open("purposes.txt", "w",encoding='utf-8')
    
    for item in batch_iterator():
        organization = json.loads(item.to_json())
        processOrganizations(organization,f)
    
    f.close()

def organization_run(code):
    item = Organization_Units.objects.get(code=code)
    organization = json.loads(item.to_json())
    
    processOrganizations(organization)
    print (purpose) 
    
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
