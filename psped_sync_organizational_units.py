#!venv/vin/python
import argparse
from alive_progress import alive_bar
from utils import send_email
from datetime import datetime

from models.sdad.organizations import Organizations
from models.sdad.organizational_units import Organizational_Units
from models.sdad.dictionary import Dictionary
from models.psped.monada import Monada, Sdad

from connection import get_database
dbname = get_database()

def processOrganizationalUnit(organizationCode):
  print(f"Processing organization with code: {organizationCode}") 
  
  organization = Organizations.objects(code=organizationCode).first()
  organizationalUnits = Organizational_Units.objects(organizationCode__code=organizationCode)
  
  with alive_bar(len(organizationalUnits)) as bar:
    for ou in organizationalUnits:
      print(f"Processing organizational unit with code: {ou.code}")
      organizational_unit_code = ou.code
      supervisor_unit_code = ou.supervisorUnitCode.code if ou.supervisorUnitCode else None

      if supervisor_unit_code:
        supervisor_unit = Organizational_Units.objects(code=supervisor_unit_code).first()
      
      sdad = Sdad(
        organization=organization,
        organization_preferredLabel=organization.preferredLabel, 
        organizational_unit=ou,
        organizational_unit_preferredLabel=ou.preferredLabel ,
        supervisor_unit=supervisor_unit if supervisor_unit_code else None,
        supervisor_unit_preferredLabel=supervisor_unit.preferredLabel if supervisor_unit_code else None       
      )

      monada = Monada.objects(code=organizational_unit_code).first()
      if monada:
          monada.sdad = sdad
          monada.save(upsert=True)
      else:
          monada = Monada(code=organizational_unit_code, sdad=sdad, remitsFinalized=False, provisionText=None)
          monada.save()
      
      bar()

def batch_iterator(batch_size=200):
  skip = 0
  while True:
    organizations = list(Organizations.objects.skip(skip).limit(batch_size))
    if not organizations:
      break
    # try: 
    for organization in organizations: 
      yield organization
    # finally: organizations.close()
    skip += batch_size

def batch_run():
  print("Ενημέρωση μονάδων psped από το sdad")

  start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
  for organization in batch_iterator():
    processOrganizationalUnit(organization.code)
  
  end_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  send_email("sync_organizations_sdad_with_psped", start_time, end_time)
  print("Τέλος ενημέρωσης μονάδων psped από το sdad")

def organization_run(organizationCode):
  print("Ενημέρωση μονάδων psped από το sdad")

  start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  
  processOrganizationalUnit(organizationCode)
  
  end_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  send_email("sync_organizations_sdad_with_psped", start_time, end_time)
  print("Τέλος ενημέρωσης μονάδων psped από το sdad")
    
my_parser = argparse.ArgumentParser(
  prog="psped_sync_organizational_units.py",
  usage="%(prog)s [--all] | [--code] code",
  description="Get all organizational units if run in batch else specific organizational units")

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