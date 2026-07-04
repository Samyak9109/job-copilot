from fastapi import APIRouter, Depends

from ..database import get_db
from ..dependencies import get_current_user
from ..schemas import DashboardStats
from ..services import memory_service
from ..services.llm_service import active_provider

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def stats(db = Depends(get_db), user = Depends(get_current_user)):
    total_memory = db.memory_items.count_documents({"user_id": user.id, "is_deleted": False})
    total_gen = db.generation_history.count_documents({"user_id": user.id})
    action_counts = {
        row["_id"]: row["count"]
        for row in db.memory_logs.aggregate([
            {"$match": {"user_id": user.id}},
            {"$group": {"_id": "$action_type", "count": {"$sum": 1}}},
        ])
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
def system_info(user = Depends(get_current_user)):
    """Surfaced in the UI so judges can see which memory + LLM backends are live."""
    return {"memory_backend": memory_service.backend_name(), "llm_provider": active_provider()}
