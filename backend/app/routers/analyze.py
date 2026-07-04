import json
from collections import Counter

from fastapi import APIRouter, Depends

from ..database import get_db
from ..dependencies import get_current_user
from ..schemas import SkillDemand, SkillGapAggregate

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


@router.get("/skill-gap/aggregate", response_model=SkillGapAggregate)
def aggregate_skill_gaps(db = Depends(get_db), user = Depends(get_current_user)):
    """Roll up every stored skill-gap analysis to surface recurring skill demand."""
    rows = list(db.skill_gaps.find({"user_id": user.id}))
    missing: Counter = Counter()
    matched: Counter = Counter()
    scores: list[int] = []
    for row in rows:
        missing_skills = row.get("missing_skills", [])
        matched_skills = row.get("matched_skills", [])
        if isinstance(missing_skills, str):
            try:
                missing_skills = json.loads(missing_skills)
            except json.JSONDecodeError:
                missing_skills = []
        if isinstance(matched_skills, str):
            try:
                matched_skills = json.loads(matched_skills)
            except json.JSONDecodeError:
                matched_skills = []
        missing.update(str(s).lower() for s in missing_skills)
        matched.update(str(s).lower() for s in matched_skills)
        scores.append(int(row.get("score", 0) or 0))

    return SkillGapAggregate(
        analyses=len(rows),
        recurring_missing=[SkillDemand(skill=s, count=c) for s, c in missing.most_common(12)],
        recurring_matched=[SkillDemand(skill=s, count=c) for s, c in matched.most_common(12)],
        average_score=round(sum(scores) / len(scores), 1) if scores else 0.0,
    )
