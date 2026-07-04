from fastapi import APIRouter, Depends, HTTPException

from ..database import get_db, next_id, utcnow
from ..dependencies import get_current_user
from ..schemas import FeedbackIn
from ..services import memory_service
from ..services.lifecycle import log_action

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

_RATING_NOTE = {
    "good": "The user rated this output as good. Keep this style and level of specificity.",
    "too_generic": "The user found the output too generic. Future outputs must be more specific and project-focused.",
    "too_long": "The user found the output too long. Future outputs should be more concise.",
    "too_short": "The user found the output too short. Future outputs should add a bit more detail.",
    "missing_project_details": "The user said project details were missing. Always weave in concrete remembered projects.",
    "selected": "This output was selected for the next round — this style works well; reuse it.",
    "rejected": "This application was rejected — adjust approach; avoid repeating this exact framing.",
}


@router.post("", status_code=201)
async def submit_feedback(payload: FeedbackIn, db = Depends(get_db), user = Depends(get_current_user)):
    generation = db.generation_history.find_one({"id": payload.generation_id, "user_id": user.id})
    if generation is None:
        raise HTTPException(status_code=404, detail="Generation not found")

    fb = {
        "id": next_id(db, "feedback"),
        "user_id": user.id,
        "generation_id": payload.generation_id,
        "rating": payload.rating,
        "feedback_text": payload.feedback_text,
        "created_at": utcnow(),
        "improved_memory": False,
    }
    db.feedback.insert_one(fb)

    note = _RATING_NOTE.get(payload.rating, f"User feedback on {generation['output_type']}: {payload.rating}.")
    if payload.feedback_text:
        note += f" User note: {payload.feedback_text}"
    note += f" (Context: {generation['output_type']} generation.)"

    try:
        dataset = await memory_service.improve(user.id, note)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"Memory improve failed: {exc}") from exc

    db.feedback.update_one({"id": fb["id"], "user_id": user.id}, {"$set": {"improved_memory": True}})
    log_action(db, user.id, "IMPROVED", f"Improved memory from feedback: {payload.rating}",
               {"dataset": dataset, "feedback_id": fb["id"], "generation_id": generation["id"]})

    return {"ok": True, "improved": True, "note": note}
