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
  number = StringField(null=True)
  issue = StringField(null=True)

class ContactDoc(EmbeddedDocument):
  email = StringField(null=True)
  telephone = StringField(null=True)
 
class MainAddressDoc(EmbeddedDocument):
  fullAddress = StringField()
  postCode = StringField()
  country = EmbeddedDocumentField(CountryDoc, null=True)  
  city = EmbeddedDocumentField(CityDoc, null=True)

class Organizations(Document):
  code = StringField(required=True, unique=True)
  preferredLabel = StringField()
  subOrganizationOf = EmbeddedDocumentField(SubOrganizationDoc, null=True)
  organizationType  = EmbeddedDocumentField(OrganizationDoc)
  description = StringField()
  url = StringField()
  contactPoint = EmbeddedDocumentField(ContactDoc, null=True)
  vatId = StringField()
  status = StringField()
  foundationDate = DateTimeField(null=True)
  terminationDate = DateTimeField(null=True)
  mainDataUpdateDate = DateTimeField(null=True)
  organizationStructureUpdateDate = DateTimeField(null=True)
  foundationFek = EmbeddedDocumentField(FekDoc, null=True)
  mainAddress = EmbeddedDocumentField(MainAddressDoc)
  
  meta = {
    "collection": "organizations",
    "db_alias": "sdad",
    "indexes": ["preferredLabel"],
  }