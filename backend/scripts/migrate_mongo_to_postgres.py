"""
MongoDB → PostgreSQL Migration Script
--------------------------------------
Run this ONCE after setting up your Supabase DB and running `alembic upgrade head`.

Prerequisites:
  pip install pymongo motor python-dotenv sqlalchemy asyncpg

Usage:
  MONGO_URI=mongodb://... DATABASE_URL=postgresql://... python scripts/migrate_mongo_to_postgres.py

IMPORTANT:
  - Supabase Auth users must be created FIRST via the Supabase Admin API or manually.
    This script only populates the `public.users` profile table.
  - Run in a dev environment first; back up production data before running there.
"""
import asyncio
import os
import uuid
from datetime import datetime
from decimal import Decimal
from pymongo import MongoClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv

from app.models.user import User, Role
from app.models.insurance import Lead, Policy, Quotation, Document

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/toque")
PG_URL = os.getenv("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://")

# ── ID mapping dicts (Mongo ObjectId string → new UUID) ──────────────────────
user_mapping: dict[str, uuid.UUID] = {}
lead_mapping: dict[str, uuid.UUID] = {}
policy_mapping: dict[str, uuid.UUID] = {}


def _safe_str(val) -> str | None:
    """Return a string or None — avoids crashing on unexpected types."""
    return str(val) if val is not None else None


def _safe_decimal(val, default=0.0) -> Decimal:
    try:
        return Decimal(str(val))
    except Exception:
        return Decimal(str(default))


def _safe_datetime(val) -> datetime | None:
    """Handle both datetime objects and ISO strings from Mongo."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    try:
        return datetime.fromisoformat(str(val))
    except Exception:
        return None


async def migrate_data():
    if not PG_URL or PG_URL == "postgresql+asyncpg://":
        print("❌  DATABASE_URL not set. Aborting.")
        return

    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client.get_default_database()

    engine = create_async_engine(PG_URL, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with SessionLocal() as db:

        # ── 1. Seed Roles ──────────────────────────────────────────────────────
        print("── Migrating Roles ──")
        roles: dict[str, Role] = {}
        for role_name in ["Admin", "Manager", "Employee", "Viewer"]:
            r = Role(id=uuid.uuid4(), name=role_name)
            db.add(r)
            roles[role_name.lower()] = r
        await db.commit()
        print(f"   ✔ Created {len(roles)} roles")

        # ── 2. Users ───────────────────────────────────────────────────────────
        print("── Migrating Users ──")
        user_count = 0
        for m_user in mongo_db.users.find():
            new_id = uuid.uuid4()
            user_mapping[str(m_user["_id"])] = new_id

            mongo_role = str(m_user.get("role", "employee")).lower()
            role_obj = roles.get(mongo_role) or roles["employee"]

            pg_user = User(
                id=new_id,
                email=m_user.get("email", f"unknown_{new_id}@placeholder.com"),
                full_name=m_user.get("name") or m_user.get("full_name") or "Unknown",
                role_id=role_obj.id,
                is_active=m_user.get("is_active", True),
            )
            db.add(pg_user)
            user_count += 1

        await db.commit()
        print(f"   ✔ Migrated {user_count} users")

        # ── 3. Leads ───────────────────────────────────────────────────────────
        print("── Migrating Leads ──")
        lead_count = 0
        for m_lead in mongo_db.leads.find():
            new_id = uuid.uuid4()
            lead_mapping[str(m_lead["_id"])] = new_id

            old_assigned = _safe_str(m_lead.get("assigned_to"))
            pg_lead = Lead(
                id=new_id,
                assigned_to=user_mapping.get(old_assigned) if old_assigned else None,
                client_name=m_lead.get("client_name") or m_lead.get("name") or "Unknown",
                client_email=_safe_str(m_lead.get("client_email") or m_lead.get("email")),
                client_phone=_safe_str(m_lead.get("client_phone") or m_lead.get("phone")),
                status=m_lead.get("status", "New"),
            )
            db.add(pg_lead)
            lead_count += 1

        await db.commit()
        print(f"   ✔ Migrated {lead_count} leads")

        # ── 4. Quotations ──────────────────────────────────────────────────────
        print("── Migrating Quotations ──")
        quot_count = 0
        for m_quot in mongo_db.quotations.find():
            old_lead_id = _safe_str(m_quot.get("lead_id"))
            old_created_by = _safe_str(m_quot.get("created_by"))

            # Extract amount — handle different Mongo field names
            amount = _safe_decimal(
                m_quot.get("amount")
                or m_quot.get("premium_amount")
                or m_quot.get("premium")
                or 0
            )

            # Flatten any extra Mongo fields into the JSONB `details` column
            skip_keys = {"_id", "lead_id", "created_by", "amount", "premium_amount",
                         "premium", "status", "created_at", "updated_at"}
            details = {k: str(v) for k, v in m_quot.items() if k not in skip_keys}

            pg_quot = Quotation(
                id=uuid.uuid4(),
                lead_id=lead_mapping.get(old_lead_id) if old_lead_id else None,
                created_by=user_mapping.get(old_created_by) if old_created_by else None,
                amount=amount,
                status=m_quot.get("status", "Draft"),
                details=details or None,
            )
            db.add(pg_quot)
            quot_count += 1

        await db.commit()
        print(f"   ✔ Migrated {quot_count} quotations")

        # ── 5. Policies + Nested Document Flattening ───────────────────────────
        print("── Migrating Policies & Flattening Nested Documents ──")
        policy_count = 0
        doc_count = 0

        for m_policy in mongo_db.policies.find():
            new_policy_id = uuid.uuid4()
            old_lead_id = _safe_str(m_policy.get("lead_id"))
            policy_mapping[str(m_policy["_id"])] = new_policy_id

            pg_policy = Policy(
                id=new_policy_id,
                lead_id=lead_mapping.get(old_lead_id) if old_lead_id else None,
                policy_number=_safe_str(m_policy.get("policy_number")) or f"MIGRATED-{new_policy_id.hex[:8].upper()}",
                provider=_safe_str(m_policy.get("provider") or m_policy.get("insurer")) or "Unknown",
                type=_safe_str(m_policy.get("type") or m_policy.get("policy_type")) or "Unknown",
                premium_amount=_safe_decimal(m_policy.get("premium_amount") or m_policy.get("premium")),
                status=m_policy.get("status", "Active"),
                start_date=_safe_datetime(m_policy.get("start_date")) or datetime.utcnow(),
                end_date=_safe_datetime(m_policy.get("end_date")) or datetime.utcnow(),
            )
            db.add(pg_policy)
            policy_count += 1

            # ── Flatten nested documents array ─────────────────────────────────
            # Mongo pattern: policy.documents = [{file_name, file_url, type}, ...]
            for nested_doc in m_policy.get("documents", []):
                file_name = (
                    nested_doc.get("file_name")
                    or nested_doc.get("name")
                    or nested_doc.get("filename")
                    or "document"
                )
                # Use the stored URL/path as the file_path (Supabase Storage path or old URL)
                file_path = (
                    nested_doc.get("file_url")
                    or nested_doc.get("url")
                    or nested_doc.get("file_path")
                    or nested_doc.get("path")
                    or f"MIGRATED/policies/{new_policy_id}/{file_name}"
                )

                pg_doc = Document(
                    id=uuid.uuid4(),
                    entity_type="policy",
                    entity_id=new_policy_id,
                    file_name=str(file_name),
                    file_path=str(file_path),
                    uploaded_by=None,  # unknown at migration time
                )
                db.add(pg_doc)
                doc_count += 1

            # Also flatten documents nested under leads if your schema had that
            for nested_doc in m_policy.get("lead_documents", []):
                file_name = nested_doc.get("file_name") or nested_doc.get("name") or "document"
                file_path = (
                    nested_doc.get("file_url")
                    or nested_doc.get("url")
                    or f"MIGRATED/leads/{old_lead_id}/{file_name}"
                )
                lead_uuid = lead_mapping.get(old_lead_id) if old_lead_id else None
                if lead_uuid:
                    pg_doc = Document(
                        id=uuid.uuid4(),
                        entity_type="lead",
                        entity_id=lead_uuid,
                        file_name=str(file_name),
                        file_path=str(file_path),
                        uploaded_by=None,
                    )
                    db.add(pg_doc)
                    doc_count += 1

        await db.commit()
        print(f"   ✔ Migrated {policy_count} policies")
        print(f"   ✔ Flattened {doc_count} nested documents into the documents table")

    print("\n✅  Migration complete!")
    print(f"   Users:      {user_count}")
    print(f"   Leads:      {lead_count}")
    print(f"   Quotations: {quot_count}")
    print(f"   Policies:   {policy_count}")
    print(f"   Documents:  {doc_count}")


if __name__ == "__main__":
    asyncio.run(migrate_data())
