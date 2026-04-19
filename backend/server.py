from dotenv import load_dotenv
from pathlib import Path
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os, logging, bcrypt, jwt, uuid, secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

# ─── Setup ───────────────────────────────────────────────────────────────────
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'autoinsure_db')]
JWT_SECRET = os.environ.get('JWT_SECRET', 'fallback_secret')
JWT_ALGORITHM = "HS256"

app = FastAPI(title="AutoInsure Platform API")
api_router = APIRouter(prefix="/api")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ─── Helpers ─────────────────────────────────────────────────────────────────
def serialize_doc(doc):
    if doc is None:
        return None
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    doc.pop("password_hash", None)
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            doc[k] = str(v)
        elif isinstance(v, datetime):
            doc[k] = v.isoformat()
    return doc

def serialize_docs(docs):
    return [serialize_doc(d) for d in docs]

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def create_access_token(user_id: str, email: str) -> str:
    payload = {"sub": user_id, "email": email, "exp": datetime.now(timezone.utc) + timedelta(hours=24), "type": "access"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "refresh"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(request: Request) -> dict:
    token = None
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return serialize_doc(user)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_auth(permission: str = None):
    async def dependency(request: Request):
        user = await get_current_user(request)
        if permission and not has_permission(user, permission):
            raise HTTPException(status_code=403, detail="Permission denied")
        return user
    return dependency

# ─── Permission System (87 permissions, 19 roles) ───────────────────────────
ALL_PERMISSIONS = [
    "dashboard.view","dashboard.analytics","dashboard.reports","dashboard.export",
    "leads.view","leads.create","leads.edit","leads.delete","leads.import","leads.export","leads.assign",
    "calls.view","calls.create","calls.edit","calls.delete",
    "followups.view","followups.create","followups.edit","followups.delete","followups.assign",
    "quotations.view","quotations.create","quotations.edit","quotations.delete","quotations.approve","quotations.pdf",
    "claims.view","claims.create","claims.edit","claims.delete","claims.approve","claims.assign","claims.settle",
    "rto.view","rto.create","rto.edit","rto.delete","rto.assign",
    "fitness.view","fitness.create","fitness.edit","fitness.delete","fitness.assign",
    "finance.view","finance.create","finance.edit","finance.delete","finance.approve","finance.reports",
    "hr.view","hr.create","hr.edit","hr.delete","hr.payroll","hr.attendance","hr.leave",
    "loans.view","loans.create","loans.edit","loans.delete","loans.approve","loans.disburse",
    "crm.view","crm.create","crm.edit","crm.delete","crm.assign",
    "customers.view","customers.create","customers.edit","customers.delete",
    "visits.view","visits.create","visits.edit","visits.delete",
    "users.view","users.create","users.edit","users.delete","users.assign_role","users.manage_permissions",
    "settings.view","settings.edit",
    "audit.view","audit.export",
    "templates.view","templates.create","templates.edit","templates.delete",
    "reports.view","reports.create","reports.export",
    "notifications.view","notifications.manage",
]

ALL_ROLES = [
    "super_admin","admin","manager","branch_manager","regional_manager",
    "sales_executive","telecaller","field_executive",
    "rto_executive","claims_executive","loan_executive","crm_executive",
    "accountant","hr","auditor","data_entry","support","it_admin","viewer"
]

_view_all = [p for p in ALL_PERMISSIONS if ".view" in p]
_crud_basic = lambda mod: [f"{mod}.view",f"{mod}.create",f"{mod}.edit"]
_crud_full = lambda mod: [f"{mod}.view",f"{mod}.create",f"{mod}.edit",f"{mod}.delete"]

ROLE_PERMISSIONS = {
    "super_admin": ALL_PERMISSIONS,
    "admin": [p for p in ALL_PERMISSIONS if p != "audit.export"],
    "manager": _view_all + [f"{m}.create" for m in ["leads","calls","followups","quotations","claims","rto","fitness"]] + [f"{m}.edit" for m in ["leads","calls","followups","quotations","claims","rto","fitness"]] + ["dashboard.analytics","dashboard.reports","leads.assign","followups.assign","leads.export"],
    "branch_manager": _view_all + [f"{m}.create" for m in ["leads","calls","followups","quotations"]] + [f"{m}.edit" for m in ["leads","calls","followups","quotations"]] + ["dashboard.analytics","leads.assign"],
    "regional_manager": _view_all + ["dashboard.analytics","dashboard.reports","dashboard.export","leads.assign"],
    "sales_executive": _crud_basic("leads") + _crud_basic("calls") + _crud_basic("followups") + _crud_basic("quotations") + ["dashboard.view","customers.view","quotations.pdf"],
    "telecaller": ["dashboard.view","leads.view","calls.view","calls.create","followups.view","followups.create","customers.view"],
    "field_executive": ["dashboard.view","leads.view","visits.view","visits.create","visits.edit","customers.view","calls.view","calls.create","followups.view","followups.create"],
    "rto_executive": _crud_full("rto") + ["dashboard.view","leads.view","customers.view","rto.assign"],
    "claims_executive": _crud_full("claims") + ["dashboard.view","leads.view","customers.view","claims.assign","claims.approve","claims.settle"],
    "loan_executive": _crud_full("loans") + ["dashboard.view","customers.view","loans.approve","loans.disburse"],
    "crm_executive": _crud_full("crm") + _crud_full("customers") + _crud_full("visits") + ["dashboard.view","crm.assign"],
    "accountant": _crud_full("finance") + ["dashboard.view","dashboard.analytics","finance.approve","finance.reports"],
    "hr": _crud_full("hr") + ["dashboard.view","hr.payroll","hr.attendance","hr.leave"],
    "auditor": _view_all + ["audit.view","audit.export","dashboard.analytics","dashboard.reports","finance.reports"],
    "data_entry": [f"{m}.view" for m in ["leads","customers","calls","followups"]] + [f"{m}.create" for m in ["leads","customers","calls","followups","quotations","claims","rto","fitness"]],
    "support": _view_all + ["calls.create","followups.create"],
    "it_admin": _crud_full("users") + ["users.assign_role","users.manage_permissions","settings.view","settings.edit","dashboard.view","audit.view"],
    "viewer": _view_all,
}

def has_permission(user: dict, permission: str) -> bool:
    if user.get("role") == "super_admin":
        return True
    user_perms = user.get("permissions", [])
    if permission in user_perms:
        return True
    role_perms = ROLE_PERMISSIONS.get(user.get("role", ""), [])
    return permission in role_perms

# ─── Auth Endpoints ──────────────────────────────────────────────────────────
@api_router.post("/auth/login")
async def login(request: Request):
    body = await request.json()
    email = body.get("email", "").lower().strip()
    password = body.get("password", "")
    if not email or not password:
        raise HTTPException(400, "Email and password required")
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(password, user.get("password_hash", "")):
        raise HTTPException(401, "Invalid credentials")
    user_id = str(user["_id"])
    token = create_access_token(user_id, email)
    refresh = create_refresh_token(user_id)
    user_data = serialize_doc(user)
    return {"access_token": token, "refresh_token": refresh, "user": user_data}

@api_router.post("/auth/register")
async def register(request: Request):
    body = await request.json()
    email = body.get("email", "").lower().strip()
    password = body.get("password", "")
    name = body.get("name", "")
    phone = body.get("phone", "")
    if not email or not password or not name:
        raise HTTPException(400, "Name, email and password required")
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(409, "Email already registered")
    user_doc = {
        "email": email, "password_hash": hash_password(password), "name": name,
        "phone": phone, "role": "viewer", "permissions": [], "pin": "",
        "is_active": True, "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc)
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    token = create_access_token(user_id, email)
    refresh = create_refresh_token(user_id)
    user_doc["_id"] = result.inserted_id
    return {"access_token": token, "refresh_token": refresh, "user": serialize_doc(user_doc)}

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(require_auth())):
    return current_user

@api_router.post("/auth/logout")
async def logout():
    return {"message": "Logged out successfully"}

@api_router.post("/auth/change-pin")
async def change_pin(request: Request, current_user: dict = Depends(require_auth())):
    body = await request.json()
    pin = body.get("pin", "")
    if len(pin) != 4 or not pin.isdigit():
        raise HTTPException(400, "PIN must be 4 digits")
    await db.users.update_one({"_id": ObjectId(current_user["id"])}, {"$set": {"pin": pin}})
    return {"message": "PIN updated"}

# ─── Dashboard ───────────────────────────────────────────────────────────────
@api_router.get("/dashboard/stats")
async def dashboard_stats(current_user: dict = Depends(require_auth("dashboard.view"))):
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    stats = {
        "total_leads": await db.leads.count_documents({}),
        "new_leads_today": await db.leads.count_documents({"created_at": {"$gte": today}}),
        "pending_followups": await db.followups.count_documents({"status": "pending"}),
        "overdue_followups": await db.followups.count_documents({"status": "overdue"}),
        "active_claims": await db.claims.count_documents({"status": {"$in": ["filed","under_review"]}}),
        "pending_rto": await db.rto_works.count_documents({"status": "pending"}),
        "pending_fitness": await db.fitness_works.count_documents({"status": "scheduled"}),
        "total_quotations": await db.quotations.count_documents({}),
        "active_loans": await db.loans.count_documents({"status": {"$in": ["applied","approved","disbursed"]}}),
        "total_customers": await db.customers.count_documents({}),
        "total_employees": await db.employees.count_documents({"status": "active"}),
        "today_visits": await db.visits.count_documents({"visit_date": {"$gte": today.isoformat()}}),
    }
    return stats

# ─── Leads ───────────────────────────────────────────────────────────────────
@api_router.get("/leads")
async def get_leads(search: str = "", status: str = "", priority: str = "", page: int = 1, limit: int = 50, current_user: dict = Depends(require_auth("leads.view"))):
    query = {}
    if search:
        query["$or"] = [{"name": {"$regex": search, "$options": "i"}}, {"phone": {"$regex": search, "$options": "i"}}, {"email": {"$regex": search, "$options": "i"}}]
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    skip = (page - 1) * limit
    total = await db.leads.count_documents(query)
    leads = await db.leads.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return {"items": serialize_docs(leads), "total": total, "page": page}

@api_router.post("/leads")
async def create_lead(request: Request, current_user: dict = Depends(require_auth("leads.create"))):
    body = await request.json()
    doc = {
        "name": body.get("name", ""), "phone": body.get("phone", ""), "email": body.get("email", ""),
        "company": body.get("company", ""), "source": body.get("source", "direct"),
        "status": body.get("status", "new"), "priority": body.get("priority", "medium"),
        "assigned_to": body.get("assigned_to", current_user["id"]),
        "assigned_name": body.get("assigned_name", current_user["name"]),
        "vehicle_type": body.get("vehicle_type", ""), "vehicle_number": body.get("vehicle_number", ""),
        "insurance_type": body.get("insurance_type", ""), "notes": body.get("notes", ""),
        "created_by": current_user["id"], "created_by_name": current_user["name"],
        "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
    }
    result = await db.leads.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)

@api_router.get("/leads/{lead_id}")
async def get_lead(lead_id: str, current_user: dict = Depends(require_auth("leads.view"))):
    lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
    if not lead:
        raise HTTPException(404, "Lead not found")
    return serialize_doc(lead)

@api_router.put("/leads/{lead_id}")
async def update_lead(lead_id: str, request: Request, current_user: dict = Depends(require_auth("leads.edit"))):
    body = await request.json()
    body["updated_at"] = datetime.now(timezone.utc).isoformat()
    body.pop("id", None)
    body.pop("_id", None)
    await db.leads.update_one({"_id": ObjectId(lead_id)}, {"$set": body})
    lead = await db.leads.find_one({"_id": ObjectId(lead_id)})
    return serialize_doc(lead)

@api_router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str, current_user: dict = Depends(require_auth("leads.delete"))):
    await db.leads.delete_one({"_id": ObjectId(lead_id)})
    return {"message": "Lead deleted"}

# ─── Calls ───────────────────────────────────────────────────────────────────
@api_router.get("/calls")
async def get_calls(lead_id: str = "", page: int = 1, limit: int = 50, current_user: dict = Depends(require_auth("calls.view"))):
    query = {}
    if lead_id:
        query["lead_id"] = lead_id
    total = await db.calls.count_documents(query)
    calls = await db.calls.find(query).sort("created_at", -1).skip((page-1)*limit).limit(limit).to_list(limit)
    return {"items": serialize_docs(calls), "total": total}

@api_router.post("/calls")
async def create_call(request: Request, current_user: dict = Depends(require_auth("calls.create"))):
    body = await request.json()
    doc = {
        "lead_id": body.get("lead_id", ""), "lead_name": body.get("lead_name", ""),
        "caller_id": current_user["id"], "caller_name": current_user["name"],
        "duration": body.get("duration", ""), "status": body.get("status", "completed"),
        "outcome": body.get("outcome", ""), "notes": body.get("notes", ""),
        "follow_up_date": body.get("follow_up_date", ""),
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.calls.insert_one(doc)
    doc["_id"] = result.inserted_id
    if body.get("follow_up_date"):
        await db.followups.insert_one({
            "lead_id": doc["lead_id"], "lead_name": doc["lead_name"],
            "assigned_to": current_user["id"], "assigned_name": current_user["name"],
            "date": body["follow_up_date"], "type": "call", "status": "pending",
            "notes": body.get("follow_up_notes", "Follow up after call"),
            "created_at": datetime.now(timezone.utc),
        })
    return serialize_doc(doc)

# ─── Follow-ups ──────────────────────────────────────────────────────────────
@api_router.get("/followups")
async def get_followups(status: str = "", page: int = 1, limit: int = 50, current_user: dict = Depends(require_auth("followups.view"))):
    query = {}
    if status:
        query["status"] = status
    total = await db.followups.count_documents(query)
    followups = await db.followups.find(query).sort("date", 1).skip((page-1)*limit).limit(limit).to_list(limit)
    return {"items": serialize_docs(followups), "total": total}

@api_router.post("/followups")
async def create_followup(request: Request, current_user: dict = Depends(require_auth("followups.create"))):
    body = await request.json()
    doc = {
        "lead_id": body.get("lead_id", ""), "lead_name": body.get("lead_name", ""),
        "assigned_to": body.get("assigned_to", current_user["id"]),
        "assigned_name": body.get("assigned_name", current_user["name"]),
        "date": body.get("date", ""), "type": body.get("type", "call"),
        "status": "pending", "notes": body.get("notes", ""),
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.followups.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)

@api_router.put("/followups/{followup_id}")
async def update_followup(followup_id: str, request: Request, current_user: dict = Depends(require_auth("followups.edit"))):
    body = await request.json()
    body.pop("id", None)
    body.pop("_id", None)
    await db.followups.update_one({"_id": ObjectId(followup_id)}, {"$set": body})
    doc = await db.followups.find_one({"_id": ObjectId(followup_id)})
    return serialize_doc(doc)

# ─── Quotations ──────────────────────────────────────────────────────────────
@api_router.get("/quotations")
async def get_quotations(status: str = "", page: int = 1, limit: int = 50, current_user: dict = Depends(require_auth("quotations.view"))):
    query = {}
    if status:
        query["status"] = status
    total = await db.quotations.count_documents(query)
    items = await db.quotations.find(query).sort("created_at", -1).skip((page-1)*limit).limit(limit).to_list(limit)
    return {"items": serialize_docs(items), "total": total}

@api_router.post("/quotations")
async def create_quotation(request: Request, current_user: dict = Depends(require_auth("quotations.create"))):
    body = await request.json()
    doc = {
        "lead_id": body.get("lead_id", ""), "lead_name": body.get("lead_name", ""),
        "customer_name": body.get("customer_name", ""), "vehicle_type": body.get("vehicle_type", ""),
        "vehicle_number": body.get("vehicle_number", ""), "insurance_type": body.get("insurance_type", ""),
        "premium_amount": body.get("premium_amount", 0), "coverage_details": body.get("coverage_details", ""),
        "idv": body.get("idv", 0), "ncb": body.get("ncb", "0%"),
        "status": "draft", "created_by": current_user["id"], "created_by_name": current_user["name"],
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.quotations.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)

@api_router.put("/quotations/{qid}")
async def update_quotation(qid: str, request: Request, current_user: dict = Depends(require_auth("quotations.edit"))):
    body = await request.json()
    body.pop("id", None)
    body.pop("_id", None)
    await db.quotations.update_one({"_id": ObjectId(qid)}, {"$set": body})
    doc = await db.quotations.find_one({"_id": ObjectId(qid)})
    return serialize_doc(doc)

# ─── Claims ──────────────────────────────────────────────────────────────────
@api_router.get("/claims")
async def get_claims(status: str = "", page: int = 1, limit: int = 50, current_user: dict = Depends(require_auth("claims.view"))):
    query = {}
    if status:
        query["status"] = status
    total = await db.claims.count_documents(query)
    items = await db.claims.find(query).sort("created_at", -1).skip((page-1)*limit).limit(limit).to_list(limit)
    return {"items": serialize_docs(items), "total": total}

@api_router.post("/claims")
async def create_claim(request: Request, current_user: dict = Depends(require_auth("claims.create"))):
    body = await request.json()
    doc = {
        "customer_name": body.get("customer_name", ""), "policy_number": body.get("policy_number", ""),
        "claim_type": body.get("claim_type", ""), "claim_amount": body.get("claim_amount", 0),
        "status": "filed", "assigned_to": body.get("assigned_to", ""),
        "assigned_name": body.get("assigned_name", ""), "notes": body.get("notes", ""),
        "vehicle_number": body.get("vehicle_number", ""), "incident_date": body.get("incident_date", ""),
        "created_by": current_user["id"], "created_at": datetime.now(timezone.utc),
    }
    result = await db.claims.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)

@api_router.put("/claims/{cid}")
async def update_claim(cid: str, request: Request, current_user: dict = Depends(require_auth("claims.edit"))):
    body = await request.json()
    body.pop("id", None)
    body.pop("_id", None)
    await db.claims.update_one({"_id": ObjectId(cid)}, {"$set": body})
    doc = await db.claims.find_one({"_id": ObjectId(cid)})
    return serialize_doc(doc)

# ─── RTO Works ───────────────────────────────────────────────────────────────
@api_router.get("/rto-works")
async def get_rto_works(status: str = "", page: int = 1, limit: int = 50, current_user: dict = Depends(require_auth("rto.view"))):
    query = {}
    if status:
        query["status"] = status
    total = await db.rto_works.count_documents(query)
    items = await db.rto_works.find(query).sort("created_at", -1).skip((page-1)*limit).limit(limit).to_list(limit)
    return {"items": serialize_docs(items), "total": total}

@api_router.post("/rto-works")
async def create_rto_work(request: Request, current_user: dict = Depends(require_auth("rto.create"))):
    body = await request.json()
    doc = {
        "customer_name": body.get("customer_name", ""), "vehicle_number": body.get("vehicle_number", ""),
        "work_type": body.get("work_type", ""), "status": "pending",
        "assigned_to": body.get("assigned_to", ""), "assigned_name": body.get("assigned_name", ""),
        "fees": body.get("fees", 0), "notes": body.get("notes", ""),
        "due_date": body.get("due_date", ""),
        "created_by": current_user["id"], "created_at": datetime.now(timezone.utc),
    }
    result = await db.rto_works.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)

@api_router.put("/rto-works/{rid}")
async def update_rto_work(rid: str, request: Request, current_user: dict = Depends(require_auth("rto.edit"))):
    body = await request.json()
    body.pop("id", None)
    body.pop("_id", None)
    await db.rto_works.update_one({"_id": ObjectId(rid)}, {"$set": body})
    doc = await db.rto_works.find_one({"_id": ObjectId(rid)})
    return serialize_doc(doc)

# ─── Fitness Works ───────────────────────────────────────────────────────────
@api_router.get("/fitness-works")
async def get_fitness_works(status: str = "", page: int = 1, limit: int = 50, current_user: dict = Depends(require_auth("fitness.view"))):
    query = {}
    if status:
        query["status"] = status
    total = await db.fitness_works.count_documents(query)
    items = await db.fitness_works.find(query).sort("created_at", -1).skip((page-1)*limit).limit(limit).to_list(limit)
    return {"items": serialize_docs(items), "total": total}

@api_router.post("/fitness-works")
async def create_fitness_work(request: Request, current_user: dict = Depends(require_auth("fitness.create"))):
    body = await request.json()
    doc = {
        "customer_name": body.get("customer_name", ""), "vehicle_number": body.get("vehicle_number", ""),
        "vehicle_type": body.get("vehicle_type", ""), "test_date": body.get("test_date", ""),
        "status": "scheduled", "assigned_to": body.get("assigned_to", ""),
        "assigned_name": body.get("assigned_name", ""), "fees": body.get("fees", 0),
        "notes": body.get("notes", ""), "center_name": body.get("center_name", ""),
        "created_by": current_user["id"], "created_at": datetime.now(timezone.utc),
    }
    result = await db.fitness_works.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)

@api_router.put("/fitness-works/{fid}")
async def update_fitness_work(fid: str, request: Request, current_user: dict = Depends(require_auth("fitness.edit"))):
    body = await request.json()
    body.pop("id", None)
    body.pop("_id", None)
    await db.fitness_works.update_one({"_id": ObjectId(fid)}, {"$set": body})
    doc = await db.fitness_works.find_one({"_id": ObjectId(fid)})
    return serialize_doc(doc)

# ─── Finance / Transactions ──────────────────────────────────────────────────
@api_router.get("/transactions")
async def get_transactions(type: str = "", category: str = "", page: int = 1, limit: int = 50, current_user: dict = Depends(require_auth("finance.view"))):
    query = {}
    if type:
        query["type"] = type
    if category:
        query["category"] = category
    total = await db.transactions.count_documents(query)
    items = await db.transactions.find(query).sort("date", -1).skip((page-1)*limit).limit(limit).to_list(limit)
    # Get summary
    pipeline = [{"$group": {"_id": "$type", "total": {"$sum": "$amount"}}}]
    summary_cursor = db.transactions.aggregate(pipeline)
    summary = {}
    async for s in summary_cursor:
        summary[s["_id"]] = s["total"]
    return {"items": serialize_docs(items), "total": total, "summary": {"income": summary.get("income", 0), "expense": summary.get("expense", 0)}}

@api_router.post("/transactions")
async def create_transaction(request: Request, current_user: dict = Depends(require_auth("finance.create"))):
    body = await request.json()
    doc = {
        "type": body.get("type", "income"), "category": body.get("category", ""),
        "amount": body.get("amount", 0), "description": body.get("description", ""),
        "reference": body.get("reference", ""), "date": body.get("date", datetime.now(timezone.utc).isoformat()),
        "created_by": current_user["id"], "created_by_name": current_user["name"],
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.transactions.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)

# ─── HR / Employees ──────────────────────────────────────────────────────────
@api_router.get("/employees")
async def get_employees(status: str = "", department: str = "", page: int = 1, limit: int = 50, current_user: dict = Depends(require_auth("hr.view"))):
    query = {}
    if status:
        query["status"] = status
    if department:
        query["department"] = department
    total = await db.employees.count_documents(query)
    items = await db.employees.find(query).sort("name", 1).skip((page-1)*limit).limit(limit).to_list(limit)
    return {"items": serialize_docs(items), "total": total}

@api_router.post("/employees")
async def create_employee(request: Request, current_user: dict = Depends(require_auth("hr.create"))):
    body = await request.json()
    doc = {
        "name": body.get("name", ""), "email": body.get("email", ""),
        "phone": body.get("phone", ""), "role": body.get("role", ""),
        "department": body.get("department", ""), "salary": body.get("salary", 0),
        "join_date": body.get("join_date", ""), "status": "active",
        "address": body.get("address", ""), "emergency_contact": body.get("emergency_contact", ""),
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.employees.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)

@api_router.put("/employees/{eid}")
async def update_employee(eid: str, request: Request, current_user: dict = Depends(require_auth("hr.edit"))):
    body = await request.json()
    body.pop("id", None)
    body.pop("_id", None)
    await db.employees.update_one({"_id": ObjectId(eid)}, {"$set": body})
    doc = await db.employees.find_one({"_id": ObjectId(eid)})
    return serialize_doc(doc)

# ─── Loans ───────────────────────────────────────────────────────────────────
@api_router.get("/loans")
async def get_loans(status: str = "", page: int = 1, limit: int = 50, current_user: dict = Depends(require_auth("loans.view"))):
    query = {}
    if status:
        query["status"] = status
    total = await db.loans.count_documents(query)
    items = await db.loans.find(query).sort("created_at", -1).skip((page-1)*limit).limit(limit).to_list(limit)
    return {"items": serialize_docs(items), "total": total}

@api_router.post("/loans")
async def create_loan(request: Request, current_user: dict = Depends(require_auth("loans.create"))):
    body = await request.json()
    doc = {
        "customer_name": body.get("customer_name", ""), "loan_type": body.get("loan_type", ""),
        "amount": body.get("amount", 0), "interest_rate": body.get("interest_rate", 0),
        "tenure": body.get("tenure", 0), "emi": body.get("emi", 0),
        "status": "applied", "assigned_to": body.get("assigned_to", ""),
        "assigned_name": body.get("assigned_name", ""), "notes": body.get("notes", ""),
        "customer_phone": body.get("customer_phone", ""),
        "created_by": current_user["id"], "created_at": datetime.now(timezone.utc),
    }
    result = await db.loans.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)

@api_router.put("/loans/{lid}")
async def update_loan(lid: str, request: Request, current_user: dict = Depends(require_auth("loans.edit"))):
    body = await request.json()
    body.pop("id", None)
    body.pop("_id", None)
    await db.loans.update_one({"_id": ObjectId(lid)}, {"$set": body})
    doc = await db.loans.find_one({"_id": ObjectId(lid)})
    return serialize_doc(doc)

# ─── Customers ───────────────────────────────────────────────────────────────
@api_router.get("/customers")
async def get_customers(search: str = "", page: int = 1, limit: int = 50, current_user: dict = Depends(require_auth("customers.view"))):
    query = {}
    if search:
        query["$or"] = [{"name": {"$regex": search, "$options": "i"}}, {"phone": {"$regex": search, "$options": "i"}}]
    total = await db.customers.count_documents(query)
    items = await db.customers.find(query).sort("name", 1).skip((page-1)*limit).limit(limit).to_list(limit)
    return {"items": serialize_docs(items), "total": total}

@api_router.post("/customers")
async def create_customer(request: Request, current_user: dict = Depends(require_auth("customers.create"))):
    body = await request.json()
    doc = {
        "name": body.get("name", ""), "phone": body.get("phone", ""),
        "email": body.get("email", ""), "address": body.get("address", ""),
        "policies": body.get("policies", []), "vehicles": body.get("vehicles", []),
        "created_by": current_user["id"], "created_by_name": current_user["name"],
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.customers.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)

@api_router.get("/customers/{cid}")
async def get_customer(cid: str, current_user: dict = Depends(require_auth("customers.view"))):
    doc = await db.customers.find_one({"_id": ObjectId(cid)})
    if not doc:
        raise HTTPException(404, "Customer not found")
    return serialize_doc(doc)

@api_router.put("/customers/{cid}")
async def update_customer(cid: str, request: Request, current_user: dict = Depends(require_auth("customers.edit"))):
    body = await request.json()
    body.pop("id", None)
    body.pop("_id", None)
    await db.customers.update_one({"_id": ObjectId(cid)}, {"$set": body})
    doc = await db.customers.find_one({"_id": ObjectId(cid)})
    return serialize_doc(doc)

# ─── Visits ──────────────────────────────────────────────────────────────────
@api_router.get("/visits")
async def get_visits(page: int = 1, limit: int = 50, current_user: dict = Depends(require_auth("visits.view"))):
    total = await db.visits.count_documents({})
    items = await db.visits.find({}).sort("visit_date", -1).skip((page-1)*limit).limit(limit).to_list(limit)
    return {"items": serialize_docs(items), "total": total}

@api_router.post("/visits")
async def create_visit(request: Request, current_user: dict = Depends(require_auth("visits.create"))):
    body = await request.json()
    doc = {
        "customer_id": body.get("customer_id", ""), "customer_name": body.get("customer_name", ""),
        "visited_by": current_user["id"], "visited_by_name": current_user["name"],
        "visit_date": body.get("visit_date", datetime.now(timezone.utc).isoformat()),
        "purpose": body.get("purpose", ""), "outcome": body.get("outcome", ""),
        "location": body.get("location", ""), "notes": body.get("notes", ""),
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.visits.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)

# ─── User Management ────────────────────────────────────────────────────────
@api_router.get("/users")
async def get_users(role: str = "", search: str = "", page: int = 1, limit: int = 50, current_user: dict = Depends(require_auth("users.view"))):
    query = {}
    if role:
        query["role"] = role
    if search:
        query["$or"] = [{"name": {"$regex": search, "$options": "i"}}, {"email": {"$regex": search, "$options": "i"}}]
    total = await db.users.count_documents(query)
    users = await db.users.find(query, {"password_hash": 0}).sort("name", 1).skip((page-1)*limit).limit(limit).to_list(limit)
    return {"items": serialize_docs(users), "total": total}

@api_router.post("/users")
async def create_user(request: Request, current_user: dict = Depends(require_auth("users.create"))):
    body = await request.json()
    email = body.get("email", "").lower().strip()
    if not email:
        raise HTTPException(400, "Email required")
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(409, "Email already exists")
    doc = {
        "email": email, "password_hash": hash_password(body.get("password", "Password@123")),
        "name": body.get("name", ""), "phone": body.get("phone", ""),
        "role": body.get("role", "viewer"), "permissions": body.get("permissions", []),
        "is_active": True, "pin": "",
        "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
    }
    result = await db.users.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)

@api_router.put("/users/{uid}")
async def update_user(uid: str, request: Request, current_user: dict = Depends(require_auth("users.edit"))):
    body = await request.json()
    body.pop("id", None)
    body.pop("_id", None)
    body.pop("password_hash", None)
    if "password" in body and body["password"]:
        body["password_hash"] = hash_password(body.pop("password"))
    else:
        body.pop("password", None)
    body["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.users.update_one({"_id": ObjectId(uid)}, {"$set": body})
    doc = await db.users.find_one({"_id": ObjectId(uid)}, {"password_hash": 0})
    return serialize_doc(doc)

@api_router.delete("/users/{uid}")
async def delete_user(uid: str, current_user: dict = Depends(require_auth("users.delete"))):
    await db.users.delete_one({"_id": ObjectId(uid)})
    return {"message": "User deleted"}

# ─── Roles & Permissions ────────────────────────────────────────────────────
@api_router.get("/roles")
async def get_roles(current_user: dict = Depends(require_auth())):
    return {"roles": ALL_ROLES, "role_permissions": {r: ROLE_PERMISSIONS.get(r, []) for r in ALL_ROLES}}

@api_router.get("/permissions")
async def get_permissions(current_user: dict = Depends(require_auth())):
    return {"permissions": ALL_PERMISSIONS, "total": len(ALL_PERMISSIONS)}

# ─── Seed Data ───────────────────────────────────────────────────────────────
async def seed_data():
    # Seed admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@autoinsure.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin@123")
    existing = await db.users.find_one({"email": admin_email})
    if existing is None:
        await db.users.insert_one({
            "email": admin_email, "password_hash": hash_password(admin_password),
            "name": "Super Admin", "phone": "9876543210", "role": "super_admin",
            "permissions": [], "pin": "1234", "is_active": True,
            "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
        })
    elif not verify_password(admin_password, existing.get("password_hash", "")):
        await db.users.update_one({"email": admin_email}, {"$set": {"password_hash": hash_password(admin_password)}})

    # Seed other users
    seed_users = [
        {"email": "manager@autoinsure.com", "name": "Rajesh Kumar", "phone": "9876543211", "role": "manager", "password": "Manager@123"},
        {"email": "sales@autoinsure.com", "name": "Priya Sharma", "phone": "9876543212", "role": "sales_executive", "password": "Sales@123"},
        {"email": "telecaller@autoinsure.com", "name": "Amit Patel", "phone": "9876543213", "role": "telecaller", "password": "Tele@123"},
        {"email": "rto@autoinsure.com", "name": "Suresh Reddy", "phone": "9876543214", "role": "rto_executive", "password": "Rto@123"},
        {"email": "claims@autoinsure.com", "name": "Deepa Nair", "phone": "9876543215", "role": "claims_executive", "password": "Claims@123"},
        {"email": "accountant@autoinsure.com", "name": "Vikram Singh", "phone": "9876543216", "role": "accountant", "password": "Acc@123"},
    ]
    for u in seed_users:
        if not await db.users.find_one({"email": u["email"]}):
            await db.users.insert_one({
                "email": u["email"], "password_hash": hash_password(u["password"]),
                "name": u["name"], "phone": u["phone"], "role": u["role"],
                "permissions": [], "pin": "", "is_active": True,
                "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
            })

    # Seed leads
    if await db.leads.count_documents({}) == 0:
        leads = [
            {"name": "Rahul Mehta", "phone": "9898765432", "email": "rahul@gmail.com", "company": "Mehta Motors", "source": "referral", "status": "new", "priority": "high", "vehicle_type": "Car", "vehicle_number": "MH01AB1234", "insurance_type": "comprehensive", "notes": "Interested in full coverage"},
            {"name": "Sneha Gupta", "phone": "9898765433", "email": "sneha@gmail.com", "company": "", "source": "website", "status": "contacted", "priority": "medium", "vehicle_type": "Car", "vehicle_number": "DL02CD5678", "insurance_type": "third_party", "notes": "Called once, asked for quote"},
            {"name": "Karan Singh", "phone": "9898765434", "email": "karan@yahoo.com", "company": "Singh Transport", "source": "walk_in", "status": "qualified", "priority": "high", "vehicle_type": "Truck", "vehicle_number": "RJ14EF9012", "insurance_type": "commercial", "notes": "Fleet of 5 trucks"},
            {"name": "Meera Joshi", "phone": "9898765435", "email": "meera@gmail.com", "company": "", "source": "referral", "status": "proposal", "priority": "medium", "vehicle_type": "Two Wheeler", "vehicle_number": "KA03GH3456", "insurance_type": "comprehensive", "notes": "New bike purchase"},
            {"name": "Arjun Rao", "phone": "9898765436", "email": "arjun@outlook.com", "company": "Rao Enterprises", "source": "cold_call", "status": "negotiation", "priority": "high", "vehicle_type": "Car", "vehicle_number": "TN04IJ7890", "insurance_type": "comprehensive", "notes": "Comparing prices with other insurers"},
            {"name": "Pooja Desai", "phone": "9898765437", "email": "pooja@gmail.com", "company": "", "source": "social_media", "status": "won", "priority": "low", "vehicle_type": "Car", "vehicle_number": "GJ05KL2345", "insurance_type": "third_party", "notes": "Policy issued"},
            {"name": "Nikhil Verma", "phone": "9898765438", "email": "nikhil@gmail.com", "company": "", "source": "website", "status": "lost", "priority": "low", "vehicle_type": "Car", "vehicle_number": "UP06MN6789", "insurance_type": "comprehensive", "notes": "Went with competitor"},
            {"name": "Anita Kumari", "phone": "9898765439", "email": "anita@gmail.com", "company": "Kumari Traders", "source": "referral", "status": "new", "priority": "high", "vehicle_type": "Commercial", "vehicle_number": "MP07OP0123", "insurance_type": "commercial", "notes": "Needs fleet insurance"},
            {"name": "Vivek Chopra", "phone": "9898765440", "email": "vivek@gmail.com", "company": "", "source": "walk_in", "status": "contacted", "priority": "medium", "vehicle_type": "Car", "vehicle_number": "HR08QR4567", "insurance_type": "comprehensive", "notes": "Old policy expiring next month"},
            {"name": "Divya Pillai", "phone": "9898765441", "email": "divya@gmail.com", "company": "", "source": "cold_call", "status": "new", "priority": "low", "vehicle_type": "Two Wheeler", "vehicle_number": "KL09ST8901", "insurance_type": "third_party", "notes": "Renewal inquiry"},
            {"name": "Manish Agarwal", "phone": "9898765442", "email": "manish@gmail.com", "company": "Agarwal Auto", "source": "referral", "status": "qualified", "priority": "high", "vehicle_type": "Car", "vehicle_number": "WB10UV2345", "insurance_type": "comprehensive", "notes": "Looking for best deal"},
            {"name": "Ritu Saxena", "phone": "9898765443", "email": "ritu@gmail.com", "company": "", "source": "website", "status": "proposal", "priority": "medium", "vehicle_type": "Car", "vehicle_number": "PB11WX6789", "insurance_type": "comprehensive", "notes": "Sent quotation"},
        ]
        now = datetime.now(timezone.utc)
        for i, lead in enumerate(leads):
            lead.update({"assigned_to": "", "assigned_name": "", "created_by": "", "created_by_name": "System", "created_at": now - timedelta(days=30-i*2), "updated_at": now - timedelta(days=15-i)})
        await db.leads.insert_many(leads)

    # Seed calls
    if await db.calls.count_documents({}) == 0:
        calls = [
            {"lead_id": "", "lead_name": "Rahul Mehta", "caller_id": "", "caller_name": "Priya Sharma", "duration": "5 min", "status": "completed", "outcome": "interested", "notes": "Will send documents tomorrow", "follow_up_date": "", "created_at": datetime.now(timezone.utc) - timedelta(days=5)},
            {"lead_id": "", "lead_name": "Sneha Gupta", "caller_id": "", "caller_name": "Amit Patel", "duration": "3 min", "status": "completed", "outcome": "callback", "notes": "Busy, call back tomorrow", "follow_up_date": "", "created_at": datetime.now(timezone.utc) - timedelta(days=3)},
            {"lead_id": "", "lead_name": "Karan Singh", "caller_id": "", "caller_name": "Priya Sharma", "duration": "10 min", "status": "completed", "outcome": "meeting_scheduled", "notes": "Meeting on Monday", "follow_up_date": "", "created_at": datetime.now(timezone.utc) - timedelta(days=2)},
            {"lead_id": "", "lead_name": "Arjun Rao", "caller_id": "", "caller_name": "Amit Patel", "duration": "0 min", "status": "no_answer", "outcome": "no_answer", "notes": "Phone switched off", "follow_up_date": "", "created_at": datetime.now(timezone.utc) - timedelta(days=1)},
            {"lead_id": "", "lead_name": "Vivek Chopra", "caller_id": "", "caller_name": "Priya Sharma", "duration": "7 min", "status": "completed", "outcome": "interested", "notes": "Wants comprehensive quote", "follow_up_date": "", "created_at": datetime.now(timezone.utc)},
        ]
        await db.calls.insert_many(calls)

    # Seed follow-ups
    if await db.followups.count_documents({}) == 0:
        now = datetime.now(timezone.utc)
        followups = [
            {"lead_id": "", "lead_name": "Rahul Mehta", "assigned_to": "", "assigned_name": "Priya Sharma", "date": (now + timedelta(days=1)).isoformat(), "type": "call", "status": "pending", "notes": "Collect documents", "created_at": now},
            {"lead_id": "", "lead_name": "Sneha Gupta", "assigned_to": "", "assigned_name": "Amit Patel", "date": (now).isoformat(), "type": "call", "status": "pending", "notes": "Follow up on callback", "created_at": now - timedelta(days=1)},
            {"lead_id": "", "lead_name": "Karan Singh", "assigned_to": "", "assigned_name": "Priya Sharma", "date": (now - timedelta(days=1)).isoformat(), "type": "visit", "status": "overdue", "notes": "Visit office for fleet details", "created_at": now - timedelta(days=3)},
            {"lead_id": "", "lead_name": "Arjun Rao", "assigned_to": "", "assigned_name": "Amit Patel", "date": (now + timedelta(days=2)).isoformat(), "type": "whatsapp", "status": "pending", "notes": "Send comparison sheet", "created_at": now},
            {"lead_id": "", "lead_name": "Pooja Desai", "assigned_to": "", "assigned_name": "Priya Sharma", "date": (now - timedelta(days=5)).isoformat(), "type": "call", "status": "completed", "notes": "Policy delivered", "created_at": now - timedelta(days=7)},
        ]
        await db.followups.insert_many(followups)

    # Seed quotations
    if await db.quotations.count_documents({}) == 0:
        quots = [
            {"lead_id": "", "lead_name": "Arjun Rao", "customer_name": "Arjun Rao", "vehicle_type": "Car", "vehicle_number": "TN04IJ7890", "insurance_type": "comprehensive", "premium_amount": 15500, "coverage_details": "Full coverage with roadside assistance", "idv": 450000, "ncb": "20%", "status": "sent", "created_by": "", "created_by_name": "Priya Sharma", "created_at": datetime.now(timezone.utc) - timedelta(days=3)},
            {"lead_id": "", "lead_name": "Ritu Saxena", "customer_name": "Ritu Saxena", "vehicle_type": "Car", "vehicle_number": "PB11WX6789", "insurance_type": "comprehensive", "premium_amount": 12800, "coverage_details": "Standard comprehensive", "idv": 380000, "ncb": "35%", "status": "draft", "created_by": "", "created_by_name": "Priya Sharma", "created_at": datetime.now(timezone.utc) - timedelta(days=1)},
            {"lead_id": "", "lead_name": "Karan Singh", "customer_name": "Karan Singh", "vehicle_type": "Truck", "vehicle_number": "RJ14EF9012", "insurance_type": "commercial", "premium_amount": 45000, "coverage_details": "Commercial fleet - 5 vehicles", "idv": 1500000, "ncb": "0%", "status": "accepted", "created_by": "", "created_by_name": "Rajesh Kumar", "created_at": datetime.now(timezone.utc) - timedelta(days=7)},
            {"lead_id": "", "lead_name": "Meera Joshi", "customer_name": "Meera Joshi", "vehicle_type": "Two Wheeler", "vehicle_number": "KA03GH3456", "insurance_type": "comprehensive", "premium_amount": 3200, "coverage_details": "Two wheeler comprehensive with PA cover", "idv": 85000, "ncb": "0%", "status": "sent", "created_by": "", "created_by_name": "Priya Sharma", "created_at": datetime.now(timezone.utc) - timedelta(days=2)},
        ]
        await db.quotations.insert_many(quots)

    # Seed claims
    if await db.claims.count_documents({}) == 0:
        claims_data = [
            {"customer_name": "Pooja Desai", "policy_number": "POL-2024-001", "claim_type": "accident", "claim_amount": 85000, "status": "under_review", "assigned_to": "", "assigned_name": "Deepa Nair", "notes": "Rear-end collision on highway", "vehicle_number": "GJ05KL2345", "incident_date": "2025-01-15", "created_by": "", "created_at": datetime.now(timezone.utc) - timedelta(days=10)},
            {"customer_name": "Rahul Mehta", "policy_number": "POL-2024-002", "claim_type": "theft", "claim_amount": 320000, "status": "filed", "assigned_to": "", "assigned_name": "", "notes": "Vehicle stolen from parking", "vehicle_number": "MH01AB1234", "incident_date": "2025-01-20", "created_by": "", "created_at": datetime.now(timezone.utc) - timedelta(days=5)},
            {"customer_name": "Vivek Chopra", "policy_number": "POL-2024-003", "claim_type": "natural_disaster", "claim_amount": 45000, "status": "approved", "assigned_to": "", "assigned_name": "Deepa Nair", "notes": "Flood damage to engine", "vehicle_number": "HR08QR4567", "incident_date": "2025-01-10", "created_by": "", "created_at": datetime.now(timezone.utc) - timedelta(days=15)},
        ]
        await db.claims.insert_many(claims_data)

    # Seed RTO works
    if await db.rto_works.count_documents({}) == 0:
        rto_data = [
            {"customer_name": "Karan Singh", "vehicle_number": "RJ14EF9012", "work_type": "registration", "status": "in_progress", "assigned_to": "", "assigned_name": "Suresh Reddy", "fees": 5500, "notes": "New vehicle registration", "due_date": "2025-02-15", "created_by": "", "created_at": datetime.now(timezone.utc) - timedelta(days=7)},
            {"customer_name": "Meera Joshi", "vehicle_number": "KA03GH3456", "work_type": "transfer", "status": "pending", "assigned_to": "", "assigned_name": "Suresh Reddy", "fees": 3000, "notes": "Ownership transfer", "due_date": "2025-02-20", "created_by": "", "created_at": datetime.now(timezone.utc) - timedelta(days=3)},
            {"customer_name": "Manish Agarwal", "vehicle_number": "WB10UV2345", "work_type": "renewal", "status": "completed", "assigned_to": "", "assigned_name": "Suresh Reddy", "fees": 2500, "notes": "RC renewal done", "due_date": "2025-01-30", "created_by": "", "created_at": datetime.now(timezone.utc) - timedelta(days=15)},
        ]
        await db.rto_works.insert_many(rto_data)

    # Seed fitness works
    if await db.fitness_works.count_documents({}) == 0:
        fitness_data = [
            {"customer_name": "Karan Singh", "vehicle_number": "RJ14EF9012", "vehicle_type": "Truck", "test_date": "2025-02-10", "status": "scheduled", "assigned_to": "", "assigned_name": "Suresh Reddy", "fees": 2000, "notes": "Annual fitness test", "center_name": "RTO Jaipur", "created_by": "", "created_at": datetime.now(timezone.utc) - timedelta(days=5)},
            {"customer_name": "Anita Kumari", "vehicle_number": "MP07OP0123", "vehicle_type": "Commercial", "test_date": "2025-01-25", "status": "passed", "assigned_to": "", "assigned_name": "", "fees": 2000, "notes": "Passed all tests", "center_name": "RTO Bhopal", "created_by": "", "created_at": datetime.now(timezone.utc) - timedelta(days=20)},
            {"customer_name": "Vivek Chopra", "vehicle_number": "HR08QR4567", "vehicle_type": "Car", "test_date": "2025-02-05", "status": "in_progress", "assigned_to": "", "assigned_name": "", "fees": 1500, "notes": "Emission test pending", "center_name": "RTO Gurgaon", "created_by": "", "created_at": datetime.now(timezone.utc) - timedelta(days=2)},
        ]
        await db.fitness_works.insert_many(fitness_data)

    # Seed transactions
    if await db.transactions.count_documents({}) == 0:
        txns = [
            {"type": "income", "category": "premium", "amount": 15500, "description": "Comprehensive policy - Arjun Rao", "reference": "TXN-001", "date": (datetime.now(timezone.utc) - timedelta(days=10)).isoformat(), "created_by": "", "created_by_name": "Vikram Singh", "created_at": datetime.now(timezone.utc) - timedelta(days=10)},
            {"type": "income", "category": "premium", "amount": 45000, "description": "Commercial fleet policy - Karan Singh", "reference": "TXN-002", "date": (datetime.now(timezone.utc) - timedelta(days=8)).isoformat(), "created_by": "", "created_by_name": "Vikram Singh", "created_at": datetime.now(timezone.utc) - timedelta(days=8)},
            {"type": "expense", "category": "commission", "amount": 4500, "description": "Agent commission - Priya Sharma", "reference": "TXN-003", "date": (datetime.now(timezone.utc) - timedelta(days=7)).isoformat(), "created_by": "", "created_by_name": "Vikram Singh", "created_at": datetime.now(timezone.utc) - timedelta(days=7)},
            {"type": "income", "category": "rto_fees", "amount": 5500, "description": "RTO registration fees - Karan Singh", "reference": "TXN-004", "date": (datetime.now(timezone.utc) - timedelta(days=5)).isoformat(), "created_by": "", "created_by_name": "Vikram Singh", "created_at": datetime.now(timezone.utc) - timedelta(days=5)},
            {"type": "expense", "category": "office", "amount": 12000, "description": "Office rent - January", "reference": "TXN-005", "date": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat(), "created_by": "", "created_by_name": "Vikram Singh", "created_at": datetime.now(timezone.utc) - timedelta(days=3)},
            {"type": "income", "category": "premium", "amount": 3200, "description": "Two wheeler policy - Meera Joshi", "reference": "TXN-006", "date": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(), "created_by": "", "created_by_name": "Vikram Singh", "created_at": datetime.now(timezone.utc) - timedelta(days=2)},
            {"type": "expense", "category": "salary", "amount": 250000, "description": "Staff salary - January", "reference": "TXN-007", "date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(), "created_by": "", "created_by_name": "Vikram Singh", "created_at": datetime.now(timezone.utc) - timedelta(days=1)},
            {"type": "income", "category": "claim_recovery", "amount": 25000, "description": "Claim recovery - Vivek Chopra", "reference": "TXN-008", "date": datetime.now(timezone.utc).isoformat(), "created_by": "", "created_by_name": "Vikram Singh", "created_at": datetime.now(timezone.utc)},
        ]
        await db.transactions.insert_many(txns)

    # Seed employees
    if await db.employees.count_documents({}) == 0:
        emps = [
            {"name": "Rajesh Kumar", "email": "manager@autoinsure.com", "phone": "9876543211", "role": "Manager", "department": "Sales", "salary": 55000, "join_date": "2023-01-15", "status": "active", "address": "Mumbai", "emergency_contact": "9876543200", "created_at": datetime.now(timezone.utc)},
            {"name": "Priya Sharma", "email": "sales@autoinsure.com", "phone": "9876543212", "role": "Sales Executive", "department": "Sales", "salary": 35000, "join_date": "2023-06-01", "status": "active", "address": "Delhi", "emergency_contact": "9876543201", "created_at": datetime.now(timezone.utc)},
            {"name": "Amit Patel", "email": "telecaller@autoinsure.com", "phone": "9876543213", "role": "Telecaller", "department": "Sales", "salary": 22000, "join_date": "2024-01-10", "status": "active", "address": "Ahmedabad", "emergency_contact": "9876543202", "created_at": datetime.now(timezone.utc)},
            {"name": "Suresh Reddy", "email": "rto@autoinsure.com", "phone": "9876543214", "role": "RTO Executive", "department": "Operations", "salary": 30000, "join_date": "2023-09-15", "status": "active", "address": "Hyderabad", "emergency_contact": "9876543203", "created_at": datetime.now(timezone.utc)},
            {"name": "Deepa Nair", "email": "claims@autoinsure.com", "phone": "9876543215", "role": "Claims Executive", "department": "Claims", "salary": 32000, "join_date": "2024-03-01", "status": "active", "address": "Kochi", "emergency_contact": "9876543204", "created_at": datetime.now(timezone.utc)},
        ]
        await db.employees.insert_many(emps)

    # Seed loans
    if await db.loans.count_documents({}) == 0:
        loans_data = [
            {"customer_name": "Karan Singh", "loan_type": "vehicle", "amount": 800000, "interest_rate": 8.5, "tenure": 60, "emi": 16400, "status": "disbursed", "assigned_to": "", "assigned_name": "", "notes": "Truck purchase loan", "customer_phone": "9898765434", "created_by": "", "created_at": datetime.now(timezone.utc) - timedelta(days=30)},
            {"customer_name": "Rahul Mehta", "loan_type": "personal", "amount": 200000, "interest_rate": 12.0, "tenure": 24, "emi": 9420, "status": "approved", "assigned_to": "", "assigned_name": "", "notes": "Personal loan for insurance premium", "customer_phone": "9898765432", "created_by": "", "created_at": datetime.now(timezone.utc) - timedelta(days=10)},
            {"customer_name": "Anita Kumari", "loan_type": "vehicle", "amount": 1500000, "interest_rate": 9.0, "tenure": 48, "emi": 37300, "status": "applied", "assigned_to": "", "assigned_name": "", "notes": "Commercial vehicle loan", "customer_phone": "9898765439", "created_by": "", "created_at": datetime.now(timezone.utc) - timedelta(days=2)},
        ]
        await db.loans.insert_many(loans_data)

    # Seed customers
    if await db.customers.count_documents({}) == 0:
        custs = [
            {"name": "Rahul Mehta", "phone": "9898765432", "email": "rahul@gmail.com", "address": "123 MG Road, Mumbai", "policies": ["POL-2024-002"], "vehicles": ["MH01AB1234"], "created_by": "", "created_by_name": "System", "created_at": datetime.now(timezone.utc)},
            {"name": "Sneha Gupta", "phone": "9898765433", "email": "sneha@gmail.com", "address": "45 Connaught Place, Delhi", "policies": [], "vehicles": ["DL02CD5678"], "created_by": "", "created_by_name": "System", "created_at": datetime.now(timezone.utc)},
            {"name": "Karan Singh", "phone": "9898765434", "email": "karan@yahoo.com", "address": "78 MI Road, Jaipur", "policies": ["POL-2024-004"], "vehicles": ["RJ14EF9012"], "created_by": "", "created_by_name": "System", "created_at": datetime.now(timezone.utc)},
            {"name": "Pooja Desai", "phone": "9898765437", "email": "pooja@gmail.com", "address": "12 SG Highway, Ahmedabad", "policies": ["POL-2024-001"], "vehicles": ["GJ05KL2345"], "created_by": "", "created_by_name": "System", "created_at": datetime.now(timezone.utc)},
            {"name": "Vivek Chopra", "phone": "9898765440", "email": "vivek@gmail.com", "address": "90 Sector 17, Chandigarh", "policies": ["POL-2024-003"], "vehicles": ["HR08QR4567"], "created_by": "", "created_by_name": "System", "created_at": datetime.now(timezone.utc)},
            {"name": "Manish Agarwal", "phone": "9898765442", "email": "manish@gmail.com", "address": "56 Park Street, Kolkata", "policies": [], "vehicles": ["WB10UV2345"], "created_by": "", "created_by_name": "System", "created_at": datetime.now(timezone.utc)},
            {"name": "Anita Kumari", "phone": "9898765439", "email": "anita@gmail.com", "address": "34 DB Mall Road, Bhopal", "policies": [], "vehicles": ["MP07OP0123"], "created_by": "", "created_by_name": "System", "created_at": datetime.now(timezone.utc)},
            {"name": "Meera Joshi", "phone": "9898765435", "email": "meera@gmail.com", "address": "67 MG Road, Bangalore", "policies": [], "vehicles": ["KA03GH3456"], "created_by": "", "created_by_name": "System", "created_at": datetime.now(timezone.utc)},
        ]
        await db.customers.insert_many(custs)

    # Seed visits
    if await db.visits.count_documents({}) == 0:
        visits_data = [
            {"customer_id": "", "customer_name": "Karan Singh", "visited_by": "", "visited_by_name": "Priya Sharma", "visit_date": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(), "purpose": "Document collection", "outcome": "Documents collected", "location": "Jaipur Office", "notes": "All documents verified", "created_at": datetime.now(timezone.utc) - timedelta(days=2)},
            {"customer_id": "", "customer_name": "Anita Kumari", "visited_by": "", "visited_by_name": "Rajesh Kumar", "visit_date": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(), "purpose": "Fleet inspection", "outcome": "Inspection completed", "location": "Bhopal Warehouse", "notes": "3 out of 5 vehicles inspected", "created_at": datetime.now(timezone.utc) - timedelta(days=1)},
            {"customer_id": "", "customer_name": "Manish Agarwal", "visited_by": "", "visited_by_name": "Priya Sharma", "visit_date": datetime.now(timezone.utc).isoformat(), "purpose": "Policy delivery", "outcome": "Pending", "location": "Kolkata Office", "notes": "Scheduled for today", "created_at": datetime.now(timezone.utc)},
        ]
        await db.visits.insert_many(visits_data)

    logger.info("Seed data loaded successfully")

# ─── App Setup ───────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    await db.leads.create_index([("name", 1), ("phone", 1)])
    await db.leads.create_index("status")
    await db.calls.create_index("lead_id")
    await db.followups.create_index("status")
    await db.followups.create_index("date")
    await db.customers.create_index("phone")
    await db.transactions.create_index("type")
    await seed_data()
    logger.info("AutoInsure Platform API started")

@app.on_event("shutdown")
async def shutdown():
    client.close()
