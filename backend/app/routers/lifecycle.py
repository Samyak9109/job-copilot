from fastapi import APIRouter, Depends

from ..database import get_db, public_doc
from ..dependencies import get_current_user
from ..schemas import MemoryLogOut

router = APIRouter(prefix="/api/lifecycle", tags=["lifecycle"])


@router.get("/logs", response_model=list[MemoryLogOut])
def logs(limit: int = 100, db = Depends(get_db), user = Depends(get_current_user)):
    rows = (
        db.memory_logs
        .find({"user_id": user.id})
        .sort("created_at", -1)
        .limit(min(limit, 300))
    )
    return [public_doc(row) for row in rows]
