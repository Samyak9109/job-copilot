from fastapi import APIRouter, Depends, HTTPException

from ..chains import chains
from ..database import get_db, next_id, utcnow
from ..dependencies import get_current_user
from ..schemas import GenerateIn, GenerateOut
from ..services import memory_service
from ..services.generation_history import record_generation
from ..services.lifecycle import log_action

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
async def generate(payload: GenerateIn, db = Depends(get_db), user = Depends(get_current_user)):
    if payload.output_type not in ALLOWED:
        raise HTTPException(status_code=400, detail=f"Invalid output_type. Allowed: {sorted(ALLOWED)}")

    job_description = payload.job_description
    if payload.job_id is not None:
        job = db.jobs.find_one({"id": payload.job_id, "user_id": user.id})
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        if not job_description:
            job_description = job.get("jd_text", "")

    recall_query = f"{_RECALL_QUERIES[payload.output_type]}. {job_description}".strip()
    try:
        context = await memory_service.recall(user.id, recall_query)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"Memory recall failed: {exc}") from exc

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
    history = record_generation(
        db,
        user_id=user.id,
        job_id=payload.job_id,
        output_type=payload.output_type,
        input_text=job_description,
        recalled_context=context,
        output_text=output_text,
        structured=structured,
    )

    if payload.output_type == "skill_gap_analysis" and structured:
        db.skill_gaps.insert_one({
            "id": next_id(db, "skill_gaps"),
            "user_id": user.id,
            "job_id": payload.job_id,
            "matched_skills": structured.get("matched_skills", []),
            "missing_skills": structured.get("missing_skills", []),
            "score": int(structured.get("score", 0) or 0),
            "created_at": utcnow(),
        })

    log_action(db, user.id, "GENERATED", f"Generated {payload.output_type}",
               {"generation_id": history["id"]})

    return GenerateOut(
        generation_id=history["id"],
        output_type=payload.output_type,
        output_text=output_text,
        structured=structured,
        recalled_context_preview=history["recalled_context_preview"],
    )
