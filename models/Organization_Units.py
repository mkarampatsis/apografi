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

class UnitTypeDoc(EmbeddedDocument):
  id = IntField()
  description = StringField()

class supervisorUnitCodeDoc(EmbeddedDocument):
  code = StringField()
  preferredLabel = StringField()

class Units(EmbeddedDocument):
  code = StringField()
  organizationCode = StringField()
  preferredLabel = StringField()
  alternativeLabels = ListField(StringField(max_length=200))
  purpose = EmbeddedDocumentListField(PurposeDoc)
  description = StringField()
  unitType = EmbeddedDocumentField(UnitTypeDoc)
  supervisorUnitCode = EmbeddedDocumentField(supervisorUnitCodeDoc, null=True)
 
class Organization_Units(Document):
  code = StringField(required=True, unique=True)
  preferredLabel = StringField()
  alternativeLabels = ListField(StringField(max_length=200))
  purpose = EmbeddedDocumentListField(PurposeDoc)
  subOrganizationOf = EmbeddedDocumentField(SubOrganizationDoc)
  organizationType  = EmbeddedDocumentField(OrganizationDoc)
  description = StringField()
  units = EmbeddedDocumentListField(Units)

  meta = {"db_alias": "ministryDB"}