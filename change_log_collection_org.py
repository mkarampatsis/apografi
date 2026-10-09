import os

from dotenv import load_dotenv
from mongoengine import connect, get_connection

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
ATLAS_DB_PSPED = os.getenv("ATLAS_DB_PSPED")

# True for testing and False for actual migration
DRY_RUN = True


def migrate_changes():

    print("Connecting to MongoDB...")

    connect(host=MONGO_URI, db=ATLAS_DB_PSPED, alias=ATLAS_DB_PSPED)

    # Get the underlying PyMongo database
    db = get_connection(ATLAS_DB_PSPED).get_database(ATLAS_DB_PSPED)

    changes_collection = db["changes"]
    foreis_collection = db["foreis"]

    # =====================================================
    # 1. Load foreis
    # =====================================================

    print("Loading foreis...")

    foreis_by_code = {}
    suborganizations_by_code = {}

    cursor = foreis_collection.find(
        {},
        {
            "_id": 0,
            "code": 1,
            "sdad.organization_preferredLabel": 1,
            "sdad.subOrganizationOf_preferredLabel": 1,
        },
    )

    for forea in cursor:
        code = forea.get("code")

        if not code:
            continue

        sdad = forea.get("sdad") or {}

        organization_name = sdad.get("organization_preferredLabel")
        subOrganizationOf_name = sdad.get("subOrganizationOf_preferredLabel")

        if not organization_name:
            continue

        foreis_by_code[str(code)] = organization_name
        suborganizations_by_code[str(code)] = subOrganizationOf_name

    print(f"Loaded {len(foreis_by_code):,} foreis and {len(suborganizations_by_code):,} suborganizations.")

    # =====================================================
    # 2. Find changes that still contain
    #    organizationalUnitCode
    # =====================================================

    print("Finding changes...")

    changes_cursor = changes_collection.find(
        {"what.key.code": {"$exists": True}, "what.entity":"organization"},
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
    missing_foreis = 0

    for change in changes_cursor:
        total += 1

        change_id = change["_id"]

        what = change.get("what") or {}

        key = what.get("key") or {}

        organization_code = key.get("code")

        if organization_code is None:
            continue

        code = str(organization_code)

        # -------------------------------------------------
        # Find organization name in our Python dictionary
        # -------------------------------------------------

        organization_name = foreis_by_code.get(code)

        if organization_name is None:
            missing_foreis += 1

            print(f"[SKIP] No foreis found for code: {code}")

            continue

        # -------------------------------------------------
        # Create new key
        # -------------------------------------------------

        new_key = {
            "organization": organization_name,
            "code": code,
            "subOrganizationOf": suborganizations_by_code.get(code) or "",
        }

        print(
            f"[{'DRY RUN' if DRY_RUN else 'UPDATE'}] "
            f"{change_id} | "
            f"{code} -> {organization_name} -> {new_key.get('subOrganizationOf', '')}"
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
    print(f"Missing foreis:    {missing_foreis:,}")
    print(f"Dry run:           {DRY_RUN}")

    print("=" * 60)


if __name__ == "__main__":
    migrate_changes()
