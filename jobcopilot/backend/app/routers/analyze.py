import json
from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import SkillGap, User
from ..schemas import SkillDemand, SkillGapAggregate

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


@router.get("/skill-gap/aggregate", response_model=SkillGapAggregate)
def aggregate_skill_gaps(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Roll up every stored skill-gap analysis to surface recurring skill demand."""
    rows = db.query(SkillGap).filter(SkillGap.user_id == user.id).all()
    missing: Counter = Counter()
    matched: Counter = Counter()
    scores: list[int] = []
    for row in rows:
        try:
            missing.update(s.lower() for s in json.loads(row.missing_skills))
            matched.update(s.lower() for s in json.loads(row.matched_skills))
        except json.JSONDecodeError:
            continue
        scores.append(row.score)

    return SkillGapAggregate(
        analyses=len(rows),
        recurring_missing=[SkillDemand(skill=s, count=c) for s, c in missing.most_common(12)],
        recurring_matched=[SkillDemand(skill=s, count=c) for s, c in matched.most_common(12)],
        average_score=round(sum(scores) / len(scores), 1) if scores else 0.0,
    )
