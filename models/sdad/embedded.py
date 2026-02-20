from mongoengine import *

class CountryDoc(EmbeddedDocument):
  id = IntField()
  description = StringField()

class CityDoc(EmbeddedDocument):
  id = IntField()
  description = StringField()
  parentId = IntField(null=True)

class OrganizationDoc(EmbeddedDocument):
  id = IntField()
  description = StringField()

class SubOrganizationDoc(EmbeddedDocument):
  code = StringField()
  preferredLabel = StringField()  
  
class FekDoc(EmbeddedDocument):
  year = IntField(null=True)
  number = IntField(null=True)
  issue = StringField(null=True)

class ContactDoc(EmbeddedDocument):
  email = StringField(null=True)
  telephone = StringField(null=True)
 
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

class PurposeDoc(EmbeddedDocument):
  id = IntField()
  description = StringField()

class UnitTypeDoc(EmbeddedDocument):
  id = IntField()
  description = StringField()

class supervisorUnitCodeDoc(EmbeddedDocument):
  code = StringField()
  preferredLabel = StringField()

class organizationCode(EmbeddedDocument):
  code = StringField()
  preferredLabel = StringField()
  
class SpatialDoc(EmbeddedDocument):
  country = EmbeddedDocumentField(CountryDoc, null=True)
  city = EmbeddedDocumentField(CityDoc, null=True)

