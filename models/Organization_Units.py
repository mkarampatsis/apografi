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

class CountryDoc(EmbeddedDocument):
  id = IntField()
  description = StringField()
  
class CityDoc(EmbeddedDocument):
  id = IntField()
  description = StringField()
  parentId = IntField(null=True)

class SpatialDoc(EmbeddedDocument):
  country = EmbeddedDocumentField(CountryDoc, null=True)
  city = EmbeddedDocumentField(CityDoc, null=True)

class MainAddressDoc(EmbeddedDocument):
  fullAddress = StringField()
  postCode = StringField()
  country = EmbeddedDocumentField(CountryDoc, null=True)  
  city = EmbeddedDocumentField(CityDoc, null=True)

class SecondaryAddressesDoc(EmbeddedDocument):
  fullAddress = StringField()
  postCode = StringField()
  country = EmbeddedDocumentField(CountryDoc, null=True)  
  city = EmbeddedDocumentField(CityDoc, null=True)

class Organization_Units(Document):
  code = StringField()
  organizationCode = StringField()
  supervisorUnitCode = EmbeddedDocumentField(supervisorUnitCodeDoc, null=True)
  preferredLabel = StringField()
  alternativeLabels = ListField(StringField(max_length=200))
  purpose = EmbeddedDocumentListField(PurposeDoc)
  spatial = EmbeddedDocumentListField(SpatialDoc)
  identifier = StringField(null=True)
  unitType = EmbeddedDocumentField(UnitTypeDoc)
  description = StringField()
  email = StringField()
  telephone = StringField()
  url = StringField()
  mainAddress = EmbeddedDocumentField(MainAddressDoc)
  secondaryAddresses = EmbeddedDocumentListField(SecondaryAddressesDoc)
 
  meta = {
    "collection": "organizational-units",
    "db_alias": "sdad"
    }