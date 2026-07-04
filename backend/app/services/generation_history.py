import json

from ..database import next_id, public_doc, utcnow
from ..utils import truncate


def record_generation(
    db,
    *,
    user_id: int,
    job_id: int | None,
    output_type: str,
    input_text: str,
    recalled_context: str,
    output_text: str | None = None,
    structured: dict | None = None,
) -> dict:
    stored_output = output_text if output_text is not None else json.dumps(structured or {})
    history = {
        "id": next_id(db, "generation_history"),
        "user_id": user_id,
        "job_id": job_id,
        "output_type": output_type,
        "input_text": input_text,
        "recalled_context_preview": truncate(recalled_context, 500),
        "output_text": stored_output,
        "created_at": utcnow(),
    }
    db.generation_history.insert_one(history)
    return public_doc(history)
