import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.core.config import settings
from app.models.user import User, Role, Permission
from app.core.database import Base

ROLES = [
    "Super Admin", "Admin", "Manager", "Branch Manager", "Regional Manager",
    "Sales Executive", "Telecaller", "Field Executive", "RTO Executive",
    "Claims Executive", "Loan Executive", "CRM Executive", "Accountant",
    "HR Manager", "Auditor", "Data Entry", "Support", "IT Admin", "Viewer"
]

# Simplified 85+ permissions grouping
PERMISSION_GROUPS = {
    "leads": ["view", "create", "edit", "delete", "assign", "import", "export", "transfer"],
    "policies": ["view", "create", "edit", "delete", "renew", "cancel", "verify"],
    "quotations": ["view", "create", "edit", "delete", "send", "approve"],
    "claims": ["view", "create", "edit", "delete", "approve", "reject", "settle"],
    "rto": ["view", "create", "edit", "delete", "process", "complete"],
    "fitness": ["view", "create", "edit", "delete", "process", "complete"],
    "loans": ["view", "create", "edit", "delete", "disburse", "close"],
    "finance": ["view", "create", "edit", "delete", "ledger", "payout", "audit"],
    "hr": ["view", "create", "edit", "delete", "payroll", "attendance"],
    "crm": ["view", "create", "edit", "delete", "visits"],
    "users": ["view", "create", "edit", "delete", "roles", "permissions"],
    "settings": ["view", "edit", "system_config"],
    "activity_logs": ["view"],
    "documents": ["view", "upload", "delete", "share"],
}

async def seed():
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(db_url)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as db:
        # 1. Create all permissions
        all_perms = []
        for group, actions in PERMISSION_GROUPS.items():
            for action in actions:
                perm_name = f"{group}.{action}"
                result = await db.execute(select(Permission).where(Permission.name == perm_name))
                perm = result.scalar_one_or_none()
                if not perm:
                    perm = Permission(id=uuid.uuid4(), name=perm_name, description=f"Can {action} {group}")
                    db.add(perm)
                all_perms.append(perm)
        
        await db.flush()

        # 2. Create roles and assign permissions
        for role_name in ROLES:
            result = await db.execute(select(Role).where(Role.name == role_name))
            role = result.scalar_one_or_none()
            if not role:
                role = Role(id=uuid.uuid4(), name=role_name)
                db.add(role)
            
            # Basic logic for auto-assigning permissions based on role
            if role_name == "Super Admin":
                role.permissions = all_perms
            elif role_name == "Admin":
                role.permissions = [p for p in all_perms if "delete" not in p.name or "users" not in p.name]
            elif "Sales" in role_name or "Telecaller" in role_name:
                role.permissions = [p for p in all_perms if p.name.startswith(("leads", "quotations", "documents"))]
            elif "Claims" in role_name:
                role.permissions = [p for p in all_perms if p.name.startswith(("claims", "policies", "documents"))]
            elif "RTO" in role_name:
                role.permissions = [p for p in all_perms if p.name.startswith(("rto", "documents"))]
            elif "Accountant" in role_name:
                role.permissions = [p for p in all_perms if p.name.startswith(("finance", "loans"))]
            elif "HR" in role_name:
                role.permissions = [p for p in all_perms if p.name.startswith(("hr", "users"))]
            else:
                # Default view permissions for others
                role.permissions = [p for p in all_perms if ".view" in p.name]

        await db.commit()
        print(f"✅ Seeded {len(ROLES)} roles and {len(all_perms)} permissions.")

if __name__ == "__main__":
    asyncio.run(seed())
