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
  

class Foreis(Document):
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
  
  meta = {"db_alias": "ministryDB"}
  
  # try:
  #   foreis = {
  #     # "email": "username@somewhere.com",
  #     "first_name": "It's supercalifragilisticexpialidocious even though the sound of it",
  #     "last_name": "is something quite atrocious if you say it loud enough you'll always sound precocious",
  #   }
  #   User(**user).save()
  # except ValidationError as exc:
  #   print("Εντοπίστηκαν λάθη ορθότητας στα πεδία:")
  
  # for field, message in exc.errors.items():
  #   print("{}: {}".format(field, message))
