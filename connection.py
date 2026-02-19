from mongoengine import connect
from dotenv import load_dotenv

import os

load_dotenv()

ATLAS_DB_SDAD=os.getenv('ATLAS_DB_SDAD')
ATLAS_DB_PSPED=os.getenv('ATLAS_DB_PSPED')
MONGO_URI=os.getenv('MONGO_URI')

def get_database():
 
  connect(
    host=MONGO_URI,
    db=ATLAS_DB_SDAD,
    alias=ATLAS_DB_SDAD,
  )

  connect(
    host=MONGO_URI,
    db=ATLAS_DB_PSPED,
    alias=ATLAS_DB_PSPED,
  )
  
  return connect
  
if __name__ == "__main__":   
  dbname = get_database()