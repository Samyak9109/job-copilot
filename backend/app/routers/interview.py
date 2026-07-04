from fastapi import APIRouter, Depends, HTTPException

from ..chains import chains
from ..database import get_db
from ..dependencies import get_current_user
from ..schemas import InterviewPrepIn, InterviewPrepOut, InterviewQuestionOut
from ..services import memory_service
from ..services.generation_history import record_generation
from ..services.lifecycle import log_action
from ..services.search_service import format_snippets, search_interview_questions

router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.post("/prep", response_model=InterviewPrepOut)
async def interview_prep(
    payload: InterviewPrepIn,
    db = Depends(get_db),
    user = Depends(get_current_user),
):
    user_context = await memory_service.recall(
        user.id, f"resume, projects and skills matching: {payload.job_description or payload.role}"
    )
    company_history = await memory_service.recall(
        user.id, f"past interview questions and answers for {payload.company}"
    )
    log_action(db, user.id, "RECALLED", f"Recalled memory for interview prep at {payload.company}",
               {"company": payload.company, "role": payload.role})

    snippets = search_interview_questions(payload.company, payload.role)

    try:
        result = chains.run_interview_prep(
            company=payload.company,
            role=payload.role,
            job_description=payload.job_description,
            user_context=user_context,
            company_history=company_history,
            search_snippets=format_snippets(snippets),
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Interview-prep chain failed: {exc}") from exc

    questions = [InterviewQuestionOut(**q) for q in result.get("questions", [])]

    history = record_generation(
        db,
        user_id=user.id,
        job_id=None,
        output_type="interview_prep",
        input_text=f"{payload.company} | {payload.role}",
        recalled_context=user_context,
        output_text="\n".join(q.question for q in questions),
    )
    log_action(db, user.id, "GENERATED", f"Generated interview prep for {payload.company}",
               {"generation_id": history["id"], "grounded": bool(snippets)})

    return InterviewPrepOut(
        generation_id=history["id"],
        questions=questions,
        sources=snippets,
        recalled_context_preview=history["recalled_context_preview"],
    )
