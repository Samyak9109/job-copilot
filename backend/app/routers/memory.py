from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from ..config import settings
from ..database import get_db, next_id, public_doc, utcnow
from ..dependencies import get_current_user
from ..schemas import MemoryItemOut, RememberTextIn
from ..services import cognee_service
from ..services.lifecycle import log_action
from ..services.pdf_service import extract_document_text
from ..utils import truncate

router = APIRouter(prefix="/api/memory", tags=["memory"])

ALLOWED_TYPES = {"resume", "project", "job_description", "interview_answer", "recruiter_note", "feedback", "other"}


def _preview(text: str, n: int = 400) -> str:
    return truncate(" ".join(text.split()), n)


async def _store_memory(db, user, *, title, memory_type, text, source_type, source_filename):
    if memory_type not in ALLOWED_TYPES:
        memory_type = "other"
    try:
        dataset, ref = await cognee_service.remember(user.id, title, memory_type, text)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"Cognee remember failed: {exc}") from exc

    item = {
        "id": next_id(db, "memory_items"),
        "user_id": user.id,
        "title": title,
        "memory_type": memory_type,
        "source_type": source_type,
        "source_filename": source_filename,
        "cognee_dataset_name": dataset,
        "cognee_ref": ref,
        "content_preview": _preview(text),
        "created_at": utcnow(),
        "is_deleted": False,
    }
    db.memory_items.insert_one(item)
    log_action(db, user.id, "REMEMBERED", f"Remembered {memory_type}: {title}",
               {"dataset": dataset, "memory_item_id": item["id"]})
    return public_doc(item)


@router.post("/upload-pdf", response_model=MemoryItemOut, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    memory_type: str = Form("resume"),
    db = Depends(get_db),
    user = Depends(get_current_user),
):
    name = (file.filename or "").lower()
    if not (name.endswith(".pdf") or name.endswith(".docx")):
        raise HTTPException(status_code=415, detail="Only PDF or DOCX files are allowed")

    data = await file.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large (max {settings.max_upload_mb}MB)")

    text = extract_document_text(data, file.filename or "")
    return await _store_memory(
        db, user, title=title.strip(), memory_type=memory_type, text=text,
        source_type="pdf" if name.endswith(".pdf") else "docx",
        source_filename=file.filename,
    )


@router.post("/remember-text", response_model=MemoryItemOut, status_code=201)
async def remember_text(
    payload: RememberTextIn,
    db = Depends(get_db),
    user = Depends(get_current_user),
):
    return await _store_memory(
        db, user, title=payload.title.strip(), memory_type=payload.memory_type,
        text=payload.text, source_type="text", source_filename=None,
    )


@router.get("/items", response_model=list[MemoryItemOut])
def list_items(db = Depends(get_db), user = Depends(get_current_user)):
    rows = (
        db.memory_items
        .find({"user_id": user.id, "is_deleted": False})
        .sort("created_at", -1)
    )
    return [public_doc(row) for row in rows]


@router.delete("/items/{memory_id}", status_code=200)
async def forget_item(memory_id: int, db = Depends(get_db), user = Depends(get_current_user)):
    item = db.memory_items.find_one({"id": memory_id, "user_id": user.id, "is_deleted": False})
    if item is None:
        raise HTTPException(status_code=404, detail="Memory item not found")

    try:
        await cognee_service.forget(user.id, item["cognee_dataset_name"], item.get("cognee_ref"))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"Cognee forget failed: {exc}") from exc

    db.memory_items.update_one({"id": memory_id, "user_id": user.id}, {"$set": {"is_deleted": True}})
    log_action(db, user.id, "FORGOTTEN", f"Forgot {item['memory_type']}: {item['title']}",
               {"dataset": item["cognee_dataset_name"], "memory_item_id": item["id"]})
    return {"ok": True, "forgotten": item["title"]}
