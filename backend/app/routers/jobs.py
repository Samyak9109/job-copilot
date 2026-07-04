from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import GenerationHistory, Job, User
from ..schemas import JOB_STATUSES, JobDetailOut, JobIn, JobOut, JobUpdate

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

_STATUS_DATE_FIELD = {
    "interview": "interview_date",
    "offer": "offer_date",
    "rejected": "rejected_date",
}


def _apply_status(job: Job, status: str):
    if status not in JOB_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {JOB_STATUSES}")
    job.status = status
    field = _STATUS_DATE_FIELD.get(status)
    if field and getattr(job, field) is None:
        setattr(job, field, datetime.now(timezone.utc))


def _owned(db, user, job_id) -> Job:
    job = db.get(Job, job_id)
    if job is None or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Job).filter(Job.user_id == user.id).order_by(Job.updated_date.desc()).all()


@router.post("", response_model=JobOut, status_code=201)
def create_job(payload: JobIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = Job(user_id=user.id, company=payload.company.strip(), title=payload.title.strip(), jd_text=payload.jd_text)
    _apply_status(job, payload.status or "applied")
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/{job_id}", response_model=JobDetailOut)
def get_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = _owned(db, user, job_id)
    gens = (
        db.query(GenerationHistory)
        .filter(GenerationHistory.user_id == user.id, GenerationHistory.job_id == job_id)
        .order_by(GenerationHistory.created_at.desc())
        .all()
    )
    detail = JobDetailOut.model_validate(job)
    detail.generations = gens  # type: ignore[assignment]
    return detail


@router.put("/{job_id}", response_model=JobOut)
def update_job(job_id: int, payload: JobUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = _owned(db, user, job_id)
    if payload.company is not None:
        job.company = payload.company.strip()
    if payload.title is not None:
        job.title = payload.title.strip()
    if payload.jd_text is not None:
        job.jd_text = payload.jd_text
    if payload.status is not None:
        _apply_status(job, payload.status)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=200)
def delete_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = _owned(db, user, job_id)
    db.query(GenerationHistory).filter(
        GenerationHistory.job_id == job_id, GenerationHistory.user_id == user.id
    ).update({GenerationHistory.job_id: None})
    db.delete(job)
    db.commit()
    return {"ok": True, "deleted": job_id}
