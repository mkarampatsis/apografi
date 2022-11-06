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
  

class Organizations(Document):
  code = StringField(required=True, unique=True)
  preferredLabel = StringField()
  alternativeLabels = ListField(StringField(max_length=200))
  purpose = EmbeddedDocumentListField(PurposeDoc)
  identifier = StringField()
  subOrganizationOf = EmbeddedDocumentField(SubOrganizationDoc)
  organizationType  = EmbeddedDocumentField(OrganizationDoc)
  description = StringField()
  status = StringField()
  foundationDate = DateTimeField(null=True)
  terminationDate = DateTimeField(null=True)
  foundationFek = EmbeddedDocumentField(FekDoc)
  organization_units = IntField()
  
  meta = {"db_alias": "ministryDB"}