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
  parentId = IntField()

class SpatialDoc(EmbeddedDocument):
  country = EmbeddedDocumentField(CountryDoc, null=True)
  city = EmbeddedDocumentField(CityDoc, null=True)

class MainAddressDoc(EmbeddedDocument):
  fullAddress = StringField()
  postCode = StringField()
  country = EmbeddedDocumentField(CountryDoc)  
  city = EmbeddedDocumentField(CityDoc)

class SecondaryAddressesDoc(EmbeddedDocument):
  fullAddress = StringField()
  postCode = StringField()
  country = EmbeddedDocumentField(CountryDoc)  
  city = EmbeddedDocumentField(CityDoc)

class Units(EmbeddedDocument):
  code = StringField()
  organizationCode = StringField()
  preferredLabel = StringField()
  alternativeLabels = ListField(StringField(max_length=200))
  purpose = EmbeddedDocumentListField(PurposeDoc)
  description = StringField()
  unitType = EmbeddedDocumentField(UnitTypeDoc)
  supervisorUnitCode = EmbeddedDocumentField(supervisorUnitCodeDoc, null=True)
  spatial = EmbeddedDocumentListField(SpatialDoc)
  email = StringField()
  telephone = StringField()
  url = StringField()
  mainAddress = EmbeddedDocumentField(MainAddressDoc)
  secondaryAddresses = EmbeddedDocumentListField(SecondaryAddressesDoc)
 
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