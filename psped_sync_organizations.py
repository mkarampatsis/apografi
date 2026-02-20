#!venv/bin/python
from models.sdad.organizations import Organizations
from models.sdad.organizational_units import Organizational_Units
from models.psped.monada import Sdad
from models.psped.foreas import Foreas

from connection import get_database
dbname = get_database()

for organization in Organizations.objects():
  code = organization.code
  print(f"Processing organization with code: {code}")
  print(f"Organization preferred label: {organization.preferredLabel}")
  organizationalUnits = Organizational_Units.objects(organizationCode=organization.code)
  sdad = Sdad(
    organization=organization,
    organization_preferredLabel=organization.preferredLabel, 
    organizational_units=organizationalUnits,
    # organizational_unit_preferredLabel=organizationalUnits[0].preferredLabel if organizationalUnits else None,
    # supervisor_unit=organizationalUnits[0].supervisorUnitCode if organizationalUnits else None,
    # supervisor_unit_preferredLabel=Organizational_Units.objects(code=organizationalUnits[0].supervisorUnitCode).first().preferredLabel if organizationalUnits and organizationalUnits[0].supervisorUnitCode else None
  )
  foreas = Foreas(code=code, sdad=sdad)
  Foreas.objects(code=organization.code).update_one(**foreas.to_mongo(), upsert=True)
