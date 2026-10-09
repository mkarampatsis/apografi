import os

from dotenv import load_dotenv
from mongoengine import connect, get_connection

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
ATLAS_DB_PSPED = os.getenv("ATLAS_DB_PSPED")

# True for testing and False for actual migration
DRY_RUN = False


def migrate_changes():

    print("Connecting to MongoDB...")

    connect(host=MONGO_URI, db=ATLAS_DB_PSPED, alias=ATLAS_DB_PSPED)

    # Get the underlying PyMongo database
    db = get_connection(ATLAS_DB_PSPED).get_database(ATLAS_DB_PSPED)

    changes_collection = db["changes"]
    monades_collection = db["monades"]

    # =====================================================
    # 1. Load monades
    # =====================================================

    print("Loading monades...")

    monades_by_code = {}
    foreis_by_code = {}

    cursor = monades_collection.find(
        {},
        {
            "_id": 0,
            "code": 1,
            "sdad.organization_preferredLabel": 1,
            "sdad.organizational_unit_preferredLabel": 1,
        },
    )

    for monada in cursor:
        code = monada.get("code")

        if not code:
            continue

        sdad = monada.get("sdad") or {}

        organization_name = sdad.get("organization_preferredLabel")
        organizational_unit_name = sdad.get("organizational_unit_preferredLabel")

        if not organizational_unit_name:
            continue

        monades_by_code[str(code)] = organizational_unit_name
        foreis_by_code[str(code)] = organization_name

    print(monades_by_code.get("816251"), foreis_by_code.get("816251"))
    print(
        f"Loaded {len(monades_by_code):,} monades and {len(foreis_by_code):,} foreis."
    )

    # =====================================================
    # 2. Find changes that still contain
    #    organizationalUnitCode
    # =====================================================

    print("Finding changes...")

    changes_cursor = changes_collection.find(
        {"what.key.organizationalUnitCode": {"$exists": True}, "what.entity": "remit"},
        {
            "_id": 1,
            "what": 1,
        },
    )

    # =====================================================
    # 3. Process changes
    # =====================================================

    total = 0
    updated = 0
    missing_monada = 0

    for change in changes_cursor:
        total += 1

        change_id = change["_id"]

        what = change.get("what") or {}

        key = what.get("key") or {}

        organizational_unit_code = key.get("organizationalUnitCode")

        if organizational_unit_code is None:
            print(
                f"[SKIP] No organizationalUnitCode found for change: {organizational_unit_code}"
            )
            continue

        code = str(organizational_unit_code)

        # -------------------------------------------------
        # Find organization name in our Python dictionary
        # -------------------------------------------------

        print(f"Looking for code: {code}")
        organization_name = foreis_by_code.get(code)
        organizational_unit_name = monades_by_code.get(code)

        print(
            f"Found organization: {organization_name} | organizational unit: {organizational_unit_name}"
        )

        if organizational_unit_name is None:
            missing_monada += 1

            print(f"[SKIP] No monada found for code: {code}")

            continue

        # -------------------------------------------------
        # Create new key
        # -------------------------------------------------

        new_key = {
            "organization": organization_name,
            "organizationalUnit": organizational_unit_name,
            "code": code,
        }

        print(
            f"[{'DRY RUN' if DRY_RUN else 'UPDATE'}] "
            f"{change_id} | "
            f"{code} -> {organizational_unit_name} -> {organization_name}"
        )

        # -------------------------------------------------
        # Update MongoDB
        # -------------------------------------------------

        if not DRY_RUN:
            result = changes_collection.update_one(
                {"_id": change_id},
                {"$set": {"what.key": new_key}},
            )

            if result.modified_count == 1:
                updated += 1

    # =====================================================
    # 4. Summary
    # =====================================================

    print()
    print("=" * 60)
    print("Migration finished")
    print("=" * 60)

    print(f"Changes found:     {total:,}")
    print(f"Changes updated:   {updated:,}")
    print(f"Missing monades:   {missing_monada:,}")
    print(f"Dry run:           {DRY_RUN}")

    print("=" * 60)


if __name__ == "__main__":
    migrate_changes()
