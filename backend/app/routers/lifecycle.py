from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import MemoryLog, User
from ..schemas import MemoryLogOut

router = APIRouter(prefix="/api/lifecycle", tags=["lifecycle"])


@router.get("/logs", response_model=list[MemoryLogOut])
def logs(limit: int = 100, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(MemoryLog)
        .filter(MemoryLog.user_id == user.id)
        .order_by(MemoryLog.created_at.desc())
        .limit(min(limit, 300))
        .all()
    )
