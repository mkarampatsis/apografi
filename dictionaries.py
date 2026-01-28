#!/usr/bin/env python3
import requests
import json
from connection import get_database
from utils import url_get, send_email
from pprint import *
from deepdiff import DeepDiff
from datetime import datetime
import argparse
# from mongoengine.queryset.visitor import Q
from alive_progress import alive_bar

from models.dictionary import Dictionary
from models.synclog import SyncLog

dbname = get_database()

# api-endpoints
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

def processDictionaries(dictionary, bar=None):
  print(f"  - Συγχρονισμός λεξικού: {dictionary}...")
  response = url_get(f"{DICTIONARIES_URL}{dictionary}")
  
  for item in response.json()["data"]:
    doc = {
      "code": dictionary,
      "code_el": DICTIONARIES[dictionary],
      "sdad_id": item["id"],
      "description": item["description"],
    }

    if "parentId" in item:
      doc["parentId"] = item["parentId"]
    
    doc_id = f"{dictionary}:{item['id']}:{item['description']}"

    existing = Dictionary.objects(
      code=dictionary,
      sdad_id=item["id"],
      description=item["description"],
    ).first()

    if existing:
      existing_dict = existing.to_mongo().to_dict()
      existing_dict.pop("_id")
      diff = DeepDiff(existing_dict, doc, view='tree').to_json() 
      diff = json.loads(diff)
      if diff:
        for key, value in doc.items():
          setattr(existing, key, value)
        existing.save()
        SyncLog(
          entity="dictionary",
          action="update",
          doc_id=doc_id,
          value=diff,
        ).save()
    else:
      Dictionary(**doc).save()
      SyncLog(
        entity="dictionary", action="insert", doc_id=doc_id, value=doc
      ).save()
  if bar:
    bar()

def batch_run():
  print("Συγχρονισμός λεξικών από το ΣΔΑΔ...")
  with alive_bar(len(DICTIONARIES)) as bar:
    start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    for dictionary in DICTIONARIES.keys():
      processDictionaries(dictionary, bar())
    end_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    send_email("dictionaries", start_time, end_time)
  print("Τέλος συγχρονισμού λεξικών από το ΣΔΑΔ.")

def dictionary_run(dictionary):
  print("Συγχρονισμός λεξικού από το ΣΔΑΔ...")
  for dict in DICTIONARIES.keys():
    if dict == dictionary:
      start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
      processDictionaries(dict)
      end_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
      send_email("dictionaries", start_time, end_time)
  print("Τέλος συγχρονισμού λεξικού από το ΣΔΑΔ.")
    
my_parser = argparse.ArgumentParser(
  prog="dictionaries.py",
  usage="%(prog)s [--all] | [--dictionary] dictionary",
  description="Get all dictionaries if run in batch else specific dictionaries")

my_parser.add_argument("--all", action="store_true")
my_parser.add_argument("--dictionary", type=str, help="give a dictionary to process")
my_parser.add_argument("--version", action='version', version='%(prog)s 1.0')
args = my_parser.parse_args()

if args.all:
  print ("Process all")
  batch_run()
else:
  print("Process dictionary: ", args.dictionary)
  dictionary_run(args.dictionary)
