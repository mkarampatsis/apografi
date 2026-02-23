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

  foreas = Foreas(code=code, sdad=sdad)
  Foreas.objects(code=organization.code).update_one(**foreas.to_mongo(), upsert=True)

def batch_iterator():
  organizations = Organizations.objects()
  with alive_bar(len(organizations)) as bar:
    for organization in organizations:
      yield organization
      bar()
  
def batch_run():
  print("Ενημέρωση οργανισμών psped από το sdad")

  start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
  for item in batch_iterator():
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
  send_email("sync_organizations_sdad_with_psped", start_time, end_time)
  print("Τέλος ενημέρωσης οργανισμών psped από το sdad")
    
my_parser = argparse.ArgumentParser(
  prog="psped_sync_organizations.py",
  usage="%(prog)s [--all] | [--code] code",
  description="Get all organizations if run in batch else specific oranizations")

my_parser.add_argument("--all", action="store_true")
my_parser.add_argument("--code", type=str, help="give an organization code to process")
my_parser.add_argument("--version", action='version', version='%(prog)s 1.0')
args = my_parser.parse_args()

if args.all:
  print ("Process all")
  batch_run()
else:
  print("Process code: ", args.code)
  organization_run(args.code)