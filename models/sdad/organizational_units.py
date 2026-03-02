from mongoengine import *
from models.sdad.embedded import (
  organizationCodeDoc, supervisorUnitCodeDoc, PurposeDoc, SpatialDoc,
  UnitTypeDoc, MainAddressDoc, SecondaryAddressesDoc
)
from models.sdad.timestamp import TimeStampedModel

class Organizational_Units(TimeStampedModel):
  code = StringField()
  organizationCode = EmbeddedDocumentField(organizationCodeDoc, null=True)
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
  remitsFinalized = BooleanField(default=False)
  elasticSync = BooleanField(default=False)
  pspedSync = BooleanField(default=False)
 
  meta = {
    "collection": "organizational-units",
    "db_alias": "sdad",
    "indexes": [
      "organizationCode.code", "supervisorUnitCode.code", "preferredLabel",
      {"fields": ["code"], "unique": True}
    ],
  }