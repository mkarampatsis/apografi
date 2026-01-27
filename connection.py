from mongoengine import connect
from dotenv import load_dotenv

import os

load_dotenv()

ATLAS_DB=os.getenv('ATLAS_DB')
MONGO_URI=os.getenv('MONGO_URI')

def get_database():
 
  connect(
    host=MONGO_URI,
    db=ATLAS_DB,
    alias=ATLAS_DB,
  )

  return connect
  
if __name__ == "__main__":   
  
   dbname = get_database()