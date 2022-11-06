from mongoengine import *

class Logs(DynamicDocument):
  code = StringField()

  meta = {"db_alias": "ministryDB"}