from mongoengine import *

class Logs(DynamicDocument):
  data = DynamicField()

  meta = {"db_alias": "ministryDB"}