import mongoengine as me
from models.sdad.organizations import Organizations
from models.sdad.organizational_units import Organizational_Units


class Apografi(me.EmbeddedDocument):
  foreas = me.ReferenceField(Organizations)
  foreas_preferredLabel = me.StringField()
  monada = me.ReferenceField(Organizational_Units)
  monada_preferredLabel = me.StringField()
  proistamenh_monada = me.ReferenceField(Organizational_Units)
  proistamenh_monada_preferredLabel = me.StringField()

class Sdad(me.EmbeddedDocument):
  organization = me.ReferenceField(Organizations)
  organization_preferredLabel = me.StringField()
  organizational_unit = me.ListField(me.ReferenceField(Organizational_Units))
  organizational_unit_preferredLabel = me.ListField(me.StringField())
  supervisor_unit = me.ReferenceField(Organizational_Units)
  supervisor_unit_preferredLabel = me.StringField()


class Monada(me.Document):
  meta = {"collection": "monades", "db_alias": "psped"}

  code = me.StringField(required=True, unique=True)
  # apografi = me.EmbeddedDocumentField(Apografi)
  sdad = me.EmbeddedDocumentField(Sdad)
  remitsFinalized = me.BooleanField()
  provisionText = me.StringField()

  def to_dict(self):
    data = {
      "code": self.code,
      "remitsFinalized": self.remitsFinalized,
      "provisionText": self.provisionText,
    }

    if self.sdad:
      data["sdad"] = {
        "organization": self.sdad.organization.to_mongo() if self.sdad.organization else None,
        "organization_preferredLabel": self.sdad.organization_preferredLabel if self.sdad.organization_preferredLabel else None,
        "organizational_unit": self.sdad.organizational_unit.to_mongo() if self.sdad.organizational_unit else None,
        "organizational_unit_preferredLabel": self.sdad.organizational_unit_preferredLabel if self.sdad.organizational_unit_preferredLabel else None,
        "supervisor_unit": self.sdad.supervisor_unit.to_mongo() if self.sdad.supervisor_unit else None,
        "supervisor_unit_preferredLabel": self.sdad.supervisor_unit_preferredLabel if self.sdad.supervisor_unit_preferredLabel else None,
      }

    return data