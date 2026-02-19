#!venv/bin/python
from src.models.apografi.organization import Organization
from src.models.apografi.organizational_unit import OrganizationalUnit
from src.models.psped import Apografi, Foreas

for organization in Organization.objects():
    code = organization.code
    monades = OrganizationalUnit.objects(organizationCode=organization.code)
    apografi = Apografi(foreas=organization, monades=monades)
    foreas = Foreas(code=code, apografi=apografi)
    Foreas.objects(code=organization.code).update_one(**foreas.to_mongo(), upsert=True)
