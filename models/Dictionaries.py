from mongoengine import *

class Dictionaries(Document):
  id = IntField(required=True)
  description = StringField(required=True)
  parentId = IntField(null=True)
  dictionary = StringField(required=True)
    
  meta = {
    "collection": "dictionaries",
    "db_alias": "ministryDB"
  }