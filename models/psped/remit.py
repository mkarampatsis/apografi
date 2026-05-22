import mongoengine as me

class orgData(me.EmbeddedDocument):
    code = me.StringField()
    preferredLabel = me.StringField()

class COFOG(me.EmbeddedDocument):
    cofog1 = me.StringField(required=True)
    cofog2 = me.StringField(required=True)
    cofog3 = me.StringField(required=True)

class Remit(me.Document):
    meta = {"collection": "remits", "db_alias": "psped", 'allow_inheritance': True}

    organization = me.EmbeddedDocumentField(orgData)
    organizational_unit = me.EmbeddedDocumentField(orgData)
    organizationalUnitCode = me.StringField(required=True)
    remitText = me.StringField(required=True)
    remitType = me.StringField(
        required=True,
        choices=[
            "ΕΠΙΤΕΛΙΚΗ",
            "ΕΚΤΕΛΕΣΤΙΚΗ",
            "ΥΠΟΣΤΗΡΙΚΤΙΚΗ",
            "ΕΛΕΓΚΤΙΚΗ",
            "ΠΑΡΑΚΟΛΟΥΘΗΣΗΣ ΑΠΟΤΕΛΕΣΜΑΤΙΚΗΣ ΠΟΛΙΤΙΚΗΣ ΚΑΙ ΑΞΙΟΛΟΓΗΣΗΣ ΑΠΟΤΕΛΕΣΜΑΤΩΝ",
        ],
    )
    cofog = me.EmbeddedDocumentField(COFOG, required=True)
    status = me.StringField(choices=["ΕΝΕΡΓΗ", "ΑΝΕΝΕΡΓΗ"], default="ΕΝΕΡΓΗ")
    legalProvisionRefs = me.ListField(me.ObjectIdField())
    