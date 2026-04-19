import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.v1.routers import (
    auth,
    calls,
    follow_ups,
    claims,
    finance,
    workflow,
    crm,
    leads,
    policies,
    users,
    roles,
    permissions,
    quotations,
    documents,
    activity_logs,
    storage,
)

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Application ────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    # Hide docs in production
    docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
    redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc",
)

# ── CORS Middleware ────────────────────────────────────────────────────────────
# Origins are read from the ALLOWED_ORIGINS env var.
# Dev default: "*" (all origins)
# Production: set ALLOWED_ORIGINS="https://yourapp.com,https://admin.yourapp.com"
_origins = settings.cors_origins
logger.info(f"CORS allowed origins: {_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# ── Global Exception Handler ───────────────────────────────────────────────────
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )

# ── Routers ────────────────────────────────────────────────────────────────────

# Auth & Storage
app.include_router(auth.router,           prefix=f"{settings.API_V1_STR}/auth",           tags=["Auth"])
app.include_router(storage.router,        prefix=f"{settings.API_V1_STR}/storage",        tags=["Storage"])

# Core entities
app.include_router(leads.router,          prefix=f"{settings.API_V1_STR}/leads",          tags=["Leads"])
app.include_router(policies.router,       prefix=f"{settings.API_V1_STR}/policies",       tags=["Policies"])
app.include_router(quotations.router,     prefix=f"{settings.API_V1_STR}/quotations",     tags=["Quotations"])
app.include_router(documents.router,      prefix=f"{settings.API_V1_STR}/documents",      tags=["Documents"])
app.include_router(activity_logs.router,  prefix=f"{settings.API_V1_STR}/activity-logs",  tags=["Activity Logs"])

# RBAC
app.include_router(users.router,          prefix=f"{settings.API_V1_STR}/users",          tags=["Users"])
app.include_router(roles.router,          prefix=f"{settings.API_V1_STR}/roles",          tags=["Roles"])
app.include_router(permissions.router,    prefix=f"{settings.API_V1_STR}/permissions",    tags=["Permissions"])


app.include_router(calls.router,          prefix=f"{settings.API_V1_STR}/calls",          tags=["Calls"])
app.include_router(follow_ups.router,     prefix=f"{settings.API_V1_STR}/follow-ups",    tags=["Follow-ups"])
app.include_router(claims.router,         prefix=f"{settings.API_V1_STR}/claims",        tags=["Claims"])
app.include_router(finance.router,        prefix=f"{settings.API_V1_STR}/finance",       tags=["Finance"])
app.include_router(workflow.router,       prefix=f"{settings.API_V1_STR}/workflow",      tags=["Workflow"])
app.include_router(crm.router,            prefix=f"{settings.API_V1_STR}/crm",           tags=["CRM"])


# ── Dashboard Stats ────────────────────────────────────────────────────────────
from sqlalchemy import text
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_user
from app.models.user import User
from fastapi import Depends

@app.get(f"{settings.API_V1_STR}/dashboard/stats", tags=["Dashboard"])
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Aggregate stats for the dashboard home screen."""
    from sqlalchemy.future import select
    from sqlalchemy import func
    from app.models.insurance import Lead, Policy, Quotation
    from app.models.call import Call
    from app.models.follow_up import FollowUp
    from app.models.claim import Claim
    from app.models.business import Loan
    from app.models.workflow import RTOWork, FitnessWork
    from app.models.crm import Customer, Visit
    from datetime import date

    today = date.today()

    total_leads = (await db.execute(select(func.count()).select_from(Lead))).scalar_one()
    new_today = (await db.execute(
        select(func.count()).select_from(Lead)
        .where(func.date(Lead.created_at) == today)
    )).scalar_one()
    total_policies = (await db.execute(select(func.count()).select_from(Policy))).scalar_one()
    active_policies = (await db.execute(
        select(func.count()).select_from(Policy).where(Policy.status == 'Active')
    )).scalar_one()
    total_quotations = (await db.execute(select(func.count()).select_from(Quotation))).scalar_one()
    total_calls = (await db.execute(select(func.count()).select_from(Call))).scalar_one()
    pending_followups = (await db.execute(
        select(func.count()).select_from(FollowUp).where(FollowUp.status == 'pending')
    )).scalar_one()
    overdue_followups = (await db.execute(
        select(func.count()).select_from(FollowUp).where(FollowUp.is_overdue == True)
    )).scalar_one()
    active_claims = (await db.execute(
        select(func.count()).select_from(Claim).where(Claim.status.in_(['filed', 'under_review', 'approved']))
    )).scalar_one()
    pending_rto = (await db.execute(
        select(func.count()).select_from(RTOWork).where(RTOWork.status == 'pending')
    )).scalar_one()
    pending_fitness = (await db.execute(
        select(func.count()).select_from(FitnessWork).where(FitnessWork.status == 'pending')
    )).scalar_one()
    active_loans = (await db.execute(
        select(func.count()).select_from(Loan).where(Loan.status.in_(['applied', 'under_review', 'approved', 'disbursed']))
    )).scalar_one()
    total_customers = (await db.execute(select(func.count()).select_from(Customer))).scalar_one()
    today_visits = (await db.execute(
        select(func.count()).select_from(Visit).where(func.date(Visit.scheduled_at) == today)
    )).scalar_one()

    return {
        "total_leads": total_leads,
        "new_leads_today": new_today,
        "pending_followups": pending_followups,
        "overdue_followups": overdue_followups,
        "total_policies": total_policies,
        "active_policies": active_policies,
        "total_quotations": total_quotations,
        "total_calls": total_calls,
        "active_claims": active_claims,
        "pending_rto": pending_rto,
        "pending_fitness": pending_fitness,
        "active_loans": active_loans,
        "total_customers": total_customers,
        "total_employees": 0,        # users count - Phase 4
        "today_visits": today_visits,
    }
@app.get("/", tags=["Health"])
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}", "status": "ok", "version": settings.VERSION}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}
