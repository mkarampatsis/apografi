#!venv/vin/python
from src.models.apografi.organization import Organization
from src.models.apografi.organizational_unit import OrganizationalUnit
from src.models.apografi.dictionary import Dictionary

from src.models.psped.monada import Apografi, Monada
from pprint import pprint

i=0

unitTypes = Dictionary.objects(code="UnitTypes")
pursposes = Dictionary.objects(code="Functions")

for organization_unit in OrganizationalUnit.objects():
    i+=1
    print(i)
    organizational_unit_code = organization_unit.code
    # print(organizational_unit_code)
    supervisor_unit_code = organization_unit.supervisorUnitCode
    organization_code = organization_unit.organizationCode

    organization = Organization.objects(code=organization_code).first()
    organizational_unit = OrganizationalUnit.objects(code=organizational_unit_code).first()
    supervisor_unit = OrganizationalUnit.objects(code=supervisor_unit_code).first()

    apografi = Apografi(
      foreas=organization,
      foreas_preferredLabel=organization.preferredLabel, 
      foreas_purpose=pursposes.filter(apografi_id=organization.purposeCode).first() if organization.purposeCode else None,
      monada=organizational_unit, 
      monada_preferredLabel=organizational_unit.preferredLabel,
      monada_unitType=unitTypes.filter(apografi_id=organizational_unit.unitTypeCode).first() if organizational_unit.unitTypeCode else None,
      monada_purpose=pursposes.filter(apografi_id=organizational_unit.purposeCode).first() if organizational_unit.purposeCode else None,
      proistamenh_monada=supervisor_unit,
      proistamenh_monada_preferredLabel=supervisor_unit.preferredLabel if supervisor_unit else None,
      proistamenh_monada_unitType=unitTypes.filter(apografi_id=supervisor_unit.unitTypeCode).first() if supervisor_unit.unitTypeCode else None,
      proistamenh_monada_purpose=pursposes.filter(apografi_id=supervisor_unit.purposeCode).first() if supervisor_unit and supervisor_unit.purposeCode else None,
    )

    monada = Monada.objects(code=organizational_unit_code).first()
    if monada:
        monada.apografi = apografi
        monada.save(upsert=True)
        #print(monada.to_mongo().to_dict())
    else:
        monada = Monada(code=organizational_unit_code, apografi=apografi, remitsFinalized=False, provisionText=None)
        monada.save()

    # if organizational_unit_code == "800399":
    #     pprint(organization_unit.to_mongo().to_dict())
    # organization = Organization.objects(code=organization_unit.organizationCode).first()
    # monada = Monada(foreas=organization, monada=organization_unit)
    # Monada.objects(code=code).update_one(**monada.to_mongo(), upsert=True)
