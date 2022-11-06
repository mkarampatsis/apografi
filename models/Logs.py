from mongoengine import *

class PurposeDoc(EmbeddedDocument):
  id = IntField()
  description = StringField()

class OrganizationDoc(EmbeddedDocument):
  id = IntField()
  description = StringField()

class SubOrganizationDoc(EmbeddedDocument):
  code = StringField()
  preferredLabel = StringField()  

class FekDoc(EmbeddedDocument):
  year = IntField()
  number = StringField()
  issue = StringField()
  

class Logs(Document):
  code = StringField(required=True, unique=True)

  meta = {"db_alias": "ministryDB"}