from mongoengine import *
from models.embedded import (
  supervisorUnitCodeDoc, PurposeDoc, SpatialDoc,
  UnitTypeDoc, MainAddressDoc, SecondaryAddressesDoc
)

class Organizational_Units(Document):
  code = StringField()
  organizationCode = StringField()
  supervisorUnitCode = EmbeddedDocumentField(supervisorUnitCodeDoc, null=True)
  preferredLabel = StringField()
  alternativeLabels = ListField(StringField(max_length=200))
  purpose = EmbeddedDocumentListField(PurposeDoc)
  spatial = EmbeddedDocumentListField(SpatialDoc)
  identifier = StringField(null=True)
  unitType = EmbeddedDocumentField(UnitTypeDoc)
  description = StringField(null=True)
  email = StringField(null=True)
  telephone = StringField(null=True)
  url = StringField(null=True)
  mainAddress = EmbeddedDocumentField(MainAddressDoc,null=True)
  secondaryAddresses = EmbeddedDocumentListField(SecondaryAddressesDoc, null=True)
 
  meta = {
    "collection": "organizational-units",
    "db_alias": "sdad",
    "indexes": ["organizationCode", "supervisorUnitCode", "preferredLabel"],
    }