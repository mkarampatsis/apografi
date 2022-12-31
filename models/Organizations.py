from mongoengine import *

class PurposeDoc(EmbeddedDocument):
  id = IntField()
  description = StringField()

class CountryDoc(EmbeddedDocument):
  id = IntField()
  description = StringField()
  
class CityDoc(EmbeddedDocument):
  id = IntField()
  description = StringField()
  parentId = IntField()

class SpatialDoc(EmbeddedDocument):
  country = EmbeddedDocumentField(CountryDoc)
  city = EmbeddedDocumentField(CityDoc)

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

class FekDoc(EmbeddedDocument):
  year = IntField()
  number = StringField()
  issue = StringField()

class ContactDoc(EmbeddedDocument):
  email = StringField()
  telephone = StringField()
 
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

class Organizations(Document):
  code = StringField(required=True, unique=True)
  preferredLabel = StringField()
  alternativeLabels = ListField(StringField(max_length=200))
  purpose = EmbeddedDocumentListField(PurposeDoc)
  spatial = EmbeddedDocumentListField(SpatialDoc)
  identifier = StringField()
  subOrganizationOf = EmbeddedDocumentField(SubOrganizationDoc, null=True)
  organizationType  = EmbeddedDocumentField(OrganizationDoc)
  description = StringField()
  status = StringField()
  foundationDate = DateTimeField(null=True)
  terminationDate = DateTimeField(null=True)
  foundationFek = EmbeddedDocumentField(FekDoc)
  organization_units = IntField()
  contactPoint = EmbeddedDocumentField(ContactDoc)
  mainAddress = EmbeddedDocumentField(MainAddressDoc)
  secondaryAddresses = EmbeddedDocumentListField(SecondaryAddressesDoc)
  
  meta = {"db_alias": "ministryDB"}