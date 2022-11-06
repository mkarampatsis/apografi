from mongoengine import *
from datetime import datetime

class Logs(DynamicDocument):
  data = DynamicField()
  timestamp = DateTimeField(required=True, default=datetime.utcnow)

  meta = {"db_alias": "ministryDB"}