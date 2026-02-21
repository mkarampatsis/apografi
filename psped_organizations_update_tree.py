import argparse
from alive_progress import alive_bar
from utils import send_email
from datetime import datetime

from connection import get_database
from models.psped.foreas import Foreas

dbname = get_database()

def build_tree(foreas):
  foreas.build_tree()

def batch_iterator():
  foreis = Foreas.objects()
  with alive_bar(len(foreis)) as bar:
    for foreas in foreis:
      yield foreas
      bar()
  
def batch_run():
  print("Ενημέρωση δεντρου psped")

  start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
  for item in batch_iterator():
    build_tree(item)
  
  end_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  send_email("build_tree", start_time, end_time)
  print("Τέλος ενημέρωσης δεντρου psped")

def organization_run(code):
  print("Ενημέρωση δεντρου psped")
  foreas = Foreas.objects(code=code).first()
  start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  build_tree(foreas)
  end_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
  send_email("build_tree", start_time, end_time)
  print("Τέλος ενημέρωσης δεντρου psped")
    
my_parser = argparse.ArgumentParser(
  prog="psped_organizations_update_tree.py",
  usage="%(prog)s [--all] | [--code] code",
  description="Create the tree structure of organizations in psped")

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