#!venv/bin/python
import argparse
from alive_progress import alive_bar
from utils import send_email
from datetime import datetime

from models.sdad.organizations import Organizations
from models.sdad.organizational_units import Organizational_Units
from models.psped.foreas import Foreas,Sdad

from connection import get_database
dbname = get_database()

def processOrganization(organization):
  code = organization.code
  print(f"Processing organization with code: {organization.code}")
  # print(organization.to_json())
  
  organizationalUnits = list( Organizational_Units.objects(organizationCode__code=organization.code))
  organizationalUnits_preferredLabel = [u.preferredLabel for u in organizationalUnits]
  
  if organization.subOrganizationOf:
    subOrganizationOf = Organizations.objects(code=organization.subOrganizationOf.code).first()
  else:
    subOrganizationOf = None

  sdad = Sdad(
    organization = organization,
    organization_preferredLabel = organization.preferredLabel, 
    organizational_unit = organizationalUnits if organizationalUnits else None,
    organizational_unit_preferredLabel = organizationalUnits_preferredLabel if organizationalUnits else None,
    subOrganizationOf = subOrganizationOf if subOrganizationOf else None,
    subOrganizationOf_preferredLabel = subOrganizationOf.preferredLabel if subOrganizationOf else None
  )
  # Save foreas to psped
  Foreas.objects(code=code).update_one(set__sdad=sdad, upsert=True)
  # Mark organization as synced
  organization.pspedSync = True
  organization.save()

def batch_iterator(changed=False):
  if changed:
    organizations = Organizations.objects(pspedSync=False)
  else:  
    organizations = Organizations.objects()
  
  if not organizations:
    return
  
  with alive_bar(len(organizations)) as bar:
    for organization in organizations:
      yield organization
      bar()
  
def batch_run(changed=False):
  print("Ενημέρωση οργανισμών psped από το sdad")

  start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
  if changed:
    print("Processing only changed organizations")
  else:
    print("Processing all organizations")  
  for item in batch_iterator(changed):
    processOrganization(item)
  
  end_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  send_email("sync_organizations_sdad_with_psped", start_time, end_time)
  print("Τέλος ενημέρωσης οργανισμών psped από το sdad")

def organization_run(code):
  print("Ενημέρωση οργανισμών psped από το sdad")
  organization= Organizations.objects(code=code).first()
  start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  processOrganization(organization)
  end_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  # send_email("sync_organizations_sdad_with_psped", start_time, end_time)
  print("Τέλος ενημέρωσης οργανισμών psped από το sdad")
    
my_parser = argparse.ArgumentParser(
  prog="psped_sync_organizations.py",
  usage="%(prog)s [--all] | [--changed] | [--code] code",
  description="Get all organizations if run in batch else specific oranizations")

my_parser.add_argument("--all", action="store_true")
my_parser.add_argument("--code", type=str, help="give an organization code to process")
my_parser.add_argument("--changed", action="store_true", help="process only changed organizations")
my_parser.add_argument("--version", action='version', version='%(prog)s 1.0')
args = my_parser.parse_args()

if args.all:
  print ("Process all")
  batch_run()
elif args.changed:
  print("Process changed")
  batch_run(changed=True)
else:
  print("Process code: ", args.code)
  organization_run(args.code)