import mongoengine as me

class Dictionary(me.Document):
  meta = {
    "collection": "dictionaries",
    "db_alias": "sdad",
    "indexes": [
        {"fields": ["sdad_id", "code", "description"], "unique": True},
        "sdad_id",
        "code",
        "description",
    ],
  }

  sdad_id = me.IntField(required=True)
  parentId = me.IntField()
  code = me.StringField(required=True)
  code_el = me.StringField(required=True)
  description = me.StringField(required=True)