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


@router.get("/stats", response_model=DashboardStats)
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    total_memory = db.query(func.count(MemoryItem.id)).filter(
        MemoryItem.user_id == user.id, MemoryItem.is_deleted == False  # noqa: E712
    ).scalar() or 0
    total_gen = db.query(func.count(GenerationHistory.id)).filter(
        GenerationHistory.user_id == user.id
    ).scalar() or 0
    action_counts = {
        action: count
        for action, count in (
            db.query(MemoryLog.action_type, func.count(MemoryLog.id))
            .filter(MemoryLog.user_id == user.id)
            .group_by(MemoryLog.action_type)
            .all()
        )
    }

    return DashboardStats(
        total_memory_items=total_memory,
        total_generations=total_gen,
        remembered_count=action_counts.get("REMEMBERED", 0),
        improved_count=action_counts.get("IMPROVED", 0),
        forgotten_count=action_counts.get("FORGOTTEN", 0),
        generated_count=action_counts.get("GENERATED", 0),
    )


@router.get("/system")
def system_info(user: User = Depends(get_current_user)):
    """Surfaced in the UI so judges can see which memory + LLM backends are live."""
    return {"memory_backend": cognee_service.backend_name(), "llm_provider": active_provider()}
