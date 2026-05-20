from mongoengine import connect
from dotenv import load_dotenv

from models.sdad.organizational_units import Organizational_Units
from models.psped.remit import Remit

import os

load_dotenv()

ATLAS_DB_SDAD = os.getenv('ATLAS_DB_SDAD')
ATLAS_DB_PSPED = os.getenv('ATLAS_DB_PSPED')
MONGO_URI = os.getenv('MONGO_URI')

# Connect to SDAD
connect(
  host=MONGO_URI,
  db=ATLAS_DB_SDAD,
  alias=ATLAS_DB_SDAD,
)

# Connect to PSPED
connect(
  host=MONGO_URI,
  db=ATLAS_DB_PSPED,
  alias=ATLAS_DB_PSPED,
)

# --- Iterate through all remits ---
for remit in Remit.objects:   # <-- MongoEngine syntax
  unit_code = remit.organizationalUnitCode
  print(f"Processing remit {remit.id} with organizationalUnitCode: {unit_code}")

  if not unit_code:
    print(f"Remit {remit.id} has no organizationalUnitCode, skipping.")
    remit.update(
      set__status="ΟΡΦΑΝΗ"
    )
    continue

  # Find matching organizational-unit
  org_unit = Organizational_Units.objects(code=unit_code).first()

  if not org_unit:
    print(f"No organizational-unit found for code {unit_code}")
    remit.update(
      set__status="ΟΡΦΑΝΗ"
    )
    continue

  # Extract organizationCode fields
  org_code_info = getattr(org_unit, "organizationCode", None)

  if not org_code_info:
    print(f"organizational-unit {unit_code} has no organizationCode field.")
    remit.update(
      set__status="ΟΡΦΑΝΗ"
    )
    continue

  # print(org_code_info.to_json())
  # print(org_code_info["code"], org_code_info["preferredLabel"])
  organization_field = {
    "code": org_code_info["code"],
    "preferredLabel": org_code_info["preferredLabel"]
  }

  organizational_unit_field =  {
    "code": org_unit["code"],
    "preferredLabel": org_unit["preferredLabel"]
  }

  # Update remit (MongoEngine way)
  remit.update(
    set__organization=organization_field,
    set__organizational_unit=organizational_unit_field
  )

  print(f"Updated remit {remit.id} with organization {organization_field}")
