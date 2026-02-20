from mongoengine import *

from models.sdad.embedded import (
  SubOrganizationDoc, OrganizationDoc, 
  ContactDoc, FekDoc, MainAddressDoc
)
from models.sdad.timestamp import TimeStampedModel

class Organizations(TimeStampedModel):
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
  mainAddress = EmbeddedDocumentField(MainAddressDoc, null=True)
  
  meta = {
    "collection": "organizations",
    "db_alias": "sdad",
    "indexes": ["preferredLabel"],
  }