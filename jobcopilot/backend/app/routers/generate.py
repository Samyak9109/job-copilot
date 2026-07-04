import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..chains import chains
from ..database import get_db
from ..dependencies import get_current_user
from ..models import GenerationHistory, Job, SkillGap, User
from ..schemas import GenerateIn, GenerateOut
from ..services import cognee_service
from ..services.lifecycle import log_action
from ..utils import truncate

router = APIRouter(prefix="/api/generate", tags=["generate"])

ALLOWED = {"cover_letter", "interview_answer", "resume_summary", "recruiter_message", "skill_gap_analysis"}

_RECALL_QUERIES = {
    "cover_letter": "most relevant projects, skills and experience for this job description",
    "interview_answer": "interview answers, projects and teamwork stories relevant to this question",
    "resume_summary": "resume details, strongest skills and achievements matching this job",
    "recruiter_message": "one strongest project and skill plus messaging style preferences",
    "skill_gap_analysis": "all skills, technologies and projects the candidate has",
}


@router.post("", response_model=GenerateOut)
async def generate(payload: GenerateIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.output_type not in ALLOWED:
        raise HTTPException(status_code=400, detail=f"Invalid output_type. Allowed: {sorted(ALLOWED)}")

    # Optionally tie this generation to a tracked job; fall back to the job's JD if none pasted.
    job_description = payload.job_description
    if payload.job_id is not None:
        job = db.get(Job, payload.job_id)
        if job is None or job.user_id != user.id:
            raise HTTPException(status_code=404, detail="Job not found")
        if not job_description:
            job_description = job.jd_text

    recall_query = f"{_RECALL_QUERIES[payload.output_type]}. {job_description}".strip()
    try:
        context = await cognee_service.recall(user.id, recall_query)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"Cognee recall failed: {exc}") from exc

    log_action(db, user.id, "RECALLED", f"Recalled memory for {payload.output_type}",
               {"query": recall_query[:200]})

    try:
        result = chains.run_generation(
            payload.output_type,
            job_description=job_description,
            context=context,
            extra_instructions=payload.extra_instructions,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Generation chain failed: {exc}") from exc

    output_text = result.get("text")
    structured = result.get("structured")
    stored_output = output_text if output_text is not None else json.dumps(structured)

    history = GenerationHistory(
        user_id=user.id,
        job_id=payload.job_id,
        output_type=payload.output_type,
        input_text=job_description,
        recalled_context_preview=truncate(context, 500),
        output_text=stored_output,
    )
    db.add(history)
    db.flush()

    # Persist skill-gap analyses so they can be aggregated across many JDs.
    if payload.output_type == "skill_gap_analysis" and structured:
        db.add(SkillGap(
            user_id=user.id,
            job_id=payload.job_id,
            matched_skills=json.dumps(structured.get("matched_skills", [])),
            missing_skills=json.dumps(structured.get("missing_skills", [])),
            score=int(structured.get("score", 0) or 0),
        ))

    log_action(db, user.id, "GENERATED", f"Generated {payload.output_type}",
               {"generation_id": history.id})
    db.commit()
    db.refresh(history)

    return GenerateOut(
        generation_id=history.id,
        output_type=payload.output_type,
        output_text=output_text,
        structured=structured,
        recalled_context_preview=truncate(context, 500),
    )
