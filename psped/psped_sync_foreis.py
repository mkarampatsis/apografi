#!venv/bin/python
from models.sdad.organizations import Organizations
from models.sdad.organizational_units import Organizational_Units
from models.psped.monada import Sdad
from models.psped.foreas import Foreas

for organization in Organizations.objects():
  code = organization.code
  monades = Organizational_Units.objects(organizationCode=organization.code)
  sdad = Sdad(foreas=organization, monades=monades)
  foreas = Foreas(code=code, sdad=sdad)
  Foreas.objects(code=organization.code).update_one(**foreas.to_mongo(), upsert=True)
