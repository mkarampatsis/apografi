from models.sdad.organizational_units import Organizational_Units
from models.psped.monada import Monada
from connection import get_database

dbname = get_database()

def updateApografiOrganizationalUnits_With_remitsFinalized():
  print("Συγχρονισμός μονάδων για remitFinalized...")
  # Step 1: Find all codes from Monada where remitsFinalized is True
  finalized_codes = list(
    Monada.objects(remitsFinalized=True).distinct("code")
  )

  # Step 2: First set all OrganizationalUnits to remitsFinalized=False
  Organizational_Units.objects.update(remitsFinalized=False)

  # Step 3: Then set only the matching codes to remitsFinalized=True
  if finalized_codes:
    Organizational_Units.objects(code__in=finalized_codes).update(remitsFinalized=True)
  
  print("Τέλος συγχρονισμού μονάδων για remitFinalized.")

updateApografiOrganizationalUnits_With_remitsFinalized()