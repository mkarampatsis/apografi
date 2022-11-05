from mongoengine import *
from dotenv import load_dotenv

import os

load_dotenv()

ATLAS_USERNAME=os.getenv('ATLAS_USERNAME')
ATLAS_PASSWORD=os.getenv('ATLAS_PASSWORD')
ATLAS_HOST=os.getenv('ATLAS_HOST')
ATLAS_DB=os.getenv('ATLAS_DB')

def get_database():
 
  connect(
    db=ATLAS_DB,
    username=ATLAS_USERNAME,
    password=ATLAS_PASSWORD,
    host=ATLAS_HOST,
    alias="ministryDB",
  )

  return connect
  
if __name__ == "__main__":   
  
   dbname = get_database()