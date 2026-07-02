from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..chains import chains
from ..database import get_db
from ..dependencies import get_current_user
from ..models import GenerationHistory, User
from ..schemas import InterviewPrepIn, InterviewPrepOut, InterviewQuestionOut
from ..services import cognee_service
from ..services.cognee_service import dataset_for
from ..services.lifecycle import log_action
from ..services.search_service import format_snippets, search_interview_questions

router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.post("/prep", response_model=InterviewPrepOut)
async def interview_prep(
    payload: InterviewPrepIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # 1. recall the candidate's own memory relevant to this JD
    user_context = await cognee_service.recall(
        user.id, f"resume, projects and skills matching: {payload.job_description or payload.role}"
    )
    # 2. recall any past interview Q&A for this company (per-company dataset)
    company_dataset = dataset_for(user.id, payload.company, kind="jobs")
    company_history = await cognee_service.recall(
        user.id,
        f"past interview questions and answers for {payload.company}",
        datasets=[dataset_for(user.id), company_dataset],
    )
    log_action(db, user.id, "RECALLED", f"Recalled memory for interview prep at {payload.company}",
               {"company": payload.company, "role": payload.role})

    # 3. ground in real candidate-reported questions via Tavily (snippets only)
    snippets = search_interview_questions(payload.company, payload.role)

    # 4. LangChain chain -> structured question list
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

    history = GenerationHistory(
        user_id=user.id,
        output_type="interview_prep",
        input_text=f"{payload.company} | {payload.role}",
        recalled_context_preview=(user_context or "")[:500],
        output_text="\n".join(q.question for q in questions),
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    log_action(db, user.id, "GENERATED", f"Generated interview prep for {payload.company}",
               {"generation_id": history.id, "grounded": bool(snippets)})

    return InterviewPrepOut(
        generation_id=history.id,
        questions=questions,
        sources=snippets,
        recalled_context_preview=(user_context or "")[:500],
    )
