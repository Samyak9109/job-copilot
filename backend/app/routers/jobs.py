from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from ..database import get_db, next_id, public_doc, utcnow
from ..dependencies import get_current_user
from ..schemas import JOB_STATUSES, JobDetailOut, JobIn, JobOut, JobUpdate

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

_STATUS_DATE_FIELD = {
    "interview": "interview_date",
    "offer": "offer_date",
    "rejected": "rejected_date",
}


def _apply_status(job: dict, status: str):
    if status not in JOB_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {JOB_STATUSES}")
    job["status"] = status
    field = _STATUS_DATE_FIELD.get(status)
    if field and job.get(field) is None:
        job[field] = datetime.now(timezone.utc)


def _owned(db, user, job_id: int) -> dict:
    job = db.jobs.find_one({"id": job_id, "user_id": user.id})
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("", response_model=list[JobOut])
def list_jobs(db = Depends(get_db), user = Depends(get_current_user)):
    rows = db.jobs.find({"user_id": user.id}).sort("updated_date", -1)
    return [public_doc(row) for row in rows]


@router.post("", response_model=JobOut, status_code=201)
def create_job(payload: JobIn, db = Depends(get_db), user = Depends(get_current_user)):
    now = utcnow()
    job = {
        "id": next_id(db, "jobs"),
        "user_id": user.id,
        "company": payload.company.strip(),
        "title": payload.title.strip(),
        "jd_text": payload.jd_text,
        "status": "applied",
        "applied_date": now,
        "interview_date": None,
        "offer_date": None,
        "rejected_date": None,
        "updated_date": now,
    }
    _apply_status(job, payload.status or "applied")
    db.jobs.insert_one(job)
    return public_doc(job)


@router.get("/{job_id}", response_model=JobDetailOut)
def get_job(job_id: int, db = Depends(get_db), user = Depends(get_current_user)):
    job = public_doc(_owned(db, user, job_id))
    gens = [
        public_doc(row)
        for row in db.generation_history
        .find({"user_id": user.id, "job_id": job_id})
        .sort("created_at", -1)
    ]
    job["generations"] = gens
    return job


@router.put("/{job_id}", response_model=JobOut)
def update_job(job_id: int, payload: JobUpdate, db = Depends(get_db), user = Depends(get_current_user)):
    job = public_doc(_owned(db, user, job_id))
    if payload.company is not None:
        job["company"] = payload.company.strip()
    if payload.title is not None:
        job["title"] = payload.title.strip()
    if payload.jd_text is not None:
        job["jd_text"] = payload.jd_text
    if payload.status is not None:
        _apply_status(job, payload.status)
    job["updated_date"] = utcnow()
    db.jobs.update_one({"id": job_id, "user_id": user.id}, {"$set": job})
    return job


@router.delete("/{job_id}", status_code=200)
def delete_job(job_id: int, db = Depends(get_db), user = Depends(get_current_user)):
    _owned(db, user, job_id)
    db.generation_history.update_many(
        {"job_id": job_id, "user_id": user.id},
        {"$set": {"job_id": None}},
    )
    db.jobs.delete_one({"id": job_id, "user_id": user.id})
    return {"ok": True, "deleted": job_id}
