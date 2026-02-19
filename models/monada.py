import mongoengine as me
from models.organizations import Organizations as Organization
from models.organizational_units import Organizational_Units as OrganizationalUnit


class Apografi(me.EmbeddedDocument):
  foreas = me.ReferenceField(Organization)
  foreas_preferredLabel = me.StringField()
  monada = me.ReferenceField(OrganizationalUnit)
  monada_preferredLabel = me.StringField()
  proistamenh_monada = me.ReferenceField(OrganizationalUnit)
  proistamenh_monada_preferredLabel = me.StringField()


class Monada(me.Document):
  meta = {"collection": "monades", "db_alias": "psped"}

  code = me.StringField(required=True, unique=True)
  apografi = me.EmbeddedDocumentField(Apografi)
  remitsFinalized = me.BooleanField()
  provisionText = me.StringField()

  def to_dict(self):
    data = {
      "code": self.code,
      "remitsFinalized": self.remitsFinalized,
      "provisionText": self.provisionText,
    }

    if self.apografi:
      data["apografi"] = {
        "foreas": self.apografi.foreas.to_mongo() if self.apografi.foreas else None,
        "monada": self.apografi.monada.to_mongo() if self.apografi.monada else None,
        "proistamenh_monada": self.apografi.proistamenh_monada.to_mongo()
        if self.apografi.proistamenh_monada
        else None,
      }

    return data