import mongoengine as me
from datetime import datetime

class SyncLog(me.Document):
  meta = {"collection": "synclog", "db_alias": "sdad"}

  date = me.DateTimeField(default=datetime.now())
  entity = me.StringField(required=True, choices=["dictionary", "organization", "organizational-unit"])
  action = me.StringField(required=True, choices=["insert", "update"])
  doc_id = me.StringField(required=True)
  value = me.DictField(required=True)