from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import GenerationHistory, MemoryItem, MemoryLog, User
from ..schemas import DashboardStats
from ..services import cognee_service
from ..services.llm_service import active_provider

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _count_action(db, user_id, action):
    return db.query(func.count(MemoryLog.id)).filter(
        MemoryLog.user_id == user_id, MemoryLog.action_type == action
    ).scalar() or 0


@router.get("/stats", response_model=DashboardStats)
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    total_memory = db.query(func.count(MemoryItem.id)).filter(
        MemoryItem.user_id == user.id, MemoryItem.is_deleted == False  # noqa: E712
    ).scalar() or 0
    total_gen = db.query(func.count(GenerationHistory.id)).filter(
        GenerationHistory.user_id == user.id
    ).scalar() or 0
    last_log = db.query(MemoryLog).filter(MemoryLog.user_id == user.id).order_by(
        MemoryLog.created_at.desc()
    ).first()

    return DashboardStats(
        total_memory_items=total_memory,
        total_generations=total_gen,
        remembered_count=_count_action(db, user.id, "REMEMBERED"),
        recalled_count=_count_action(db, user.id, "RECALLED"),
        improved_count=_count_action(db, user.id, "IMPROVED"),
        forgotten_count=_count_action(db, user.id, "FORGOTTEN"),
        generated_count=_count_action(db, user.id, "GENERATED"),
        last_activity=last_log.created_at if last_log else None,
    )


@router.get("/system")
def system_info(user: User = Depends(get_current_user)):
    """Surfaced in the UI so judges can see which memory + LLM backends are live."""
    return {"memory_backend": cognee_service.backend_name(), "llm_provider": active_provider()}
