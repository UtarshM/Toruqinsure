"""
Activity Log Service
---------------------
Central helper for writing audit trail entries across all services.

Usage in any service:
    from app.services.activity_log_service import log_action

    await log_action(db, user=current_user, action="created_lead",
                     entity_type="lead", entity_id=new_lead.id,
                     meta={"client_name": new_lead.client_name})

The function flushes (not commits) so the caller can batch it with the
main business operation in a single transaction commit.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
from typing import Any, Dict, List, Optional

from app.models.insurance import ActivityLog
from app.models.user import User

logger = logging.getLogger(__name__)


async def log_action(
    db: AsyncSession,
    *,
    user: Optional[User],
    action: str,
    entity_type: str,
    entity_id: UUID,
    meta: Optional[Dict[str, Any]] = None,
) -> ActivityLog:
    """
    Write a single activity log entry and flush it to the session.
    Caller is responsible for committing the transaction.

    Args:
        db          : Current async DB session.
        user        : The acting user (can be None for system actions).
        action      : Snake_case action name, e.g. "created_lead".
        entity_type : Table name of the affected entity, e.g. "lead".
        entity_id   : UUID of the affected row.
        meta        : Optional extra context serialised into the JSONB metadata column.
    """
    entry = ActivityLog(
        user_id=user.id if user else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        metadata_=meta or {},
    )
    db.add(entry)

    try:
        await db.flush()  # Write to session without committing — caller commits
    except Exception as exc:
        # Logging failures must NEVER break the main operation
        logger.warning(f"[ActivityLog] Failed to flush log entry ({action} on {entity_type}/{entity_id}): {exc}")

    return entry


async def get_entity_history(
    db: AsyncSession,
    entity_type: str,
    entity_id: UUID,
    limit: int = 50,
) -> List[ActivityLog]:
    """Return the activity history for a specific entity, newest first."""
    stmt = (
        select(ActivityLog)
        .filter(
            ActivityLog.entity_type == entity_type,
            ActivityLog.entity_id == entity_id,
        )
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_user_activity(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 100,
) -> List[ActivityLog]:
    """Return the last N actions performed by a specific user."""
    stmt = (
        select(ActivityLog)
        .filter(ActivityLog.user_id == user_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
