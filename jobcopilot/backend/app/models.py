from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class MemoryItem(Base):
    __tablename__ = "memory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    memory_type: Mapped[str] = mapped_column(String(40))
    source_type: Mapped[str] = mapped_column(String(20))
    source_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cognee_dataset_name: Mapped[str] = mapped_column(String(120))
    cognee_ref: Mapped[str | None] = mapped_column(String(120), nullable=True)
    content_preview: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)


class GenerationHistory(Base):
    __tablename__ = "generation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"), nullable=True, index=True)
    output_type: Mapped[str] = mapped_column(String(40))
    input_text: Mapped[str] = mapped_column(Text)
    recalled_context_preview: Mapped[str] = mapped_column(Text)
    output_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class Job(Base):
    """A tracked job application. Status pipeline: applied -> interview -> offer -> rejected."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    company: Mapped[str] = mapped_column(String(200))
    title: Mapped[str] = mapped_column(String(200))
    jd_text: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="applied")
    applied_date: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    interview_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    offer_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejected_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_date: Mapped[datetime] = mapped_column(DateTime, default=_utcnow, onupdate=_utcnow)


class SkillGap(Base):
    """Persisted skill-gap analysis for a job (enables cross-JD aggregation)."""

    __tablename__ = "skill_gaps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    job_id: Mapped[int | None] = mapped_column(ForeignKey("jobs.id"), nullable=True, index=True)
    matched_skills: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
    missing_skills: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
    score: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    generation_id: Mapped[int] = mapped_column(ForeignKey("generation_history.id"))
    rating: Mapped[str] = mapped_column(String(40))
    feedback_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    improved_memory: Mapped[bool] = mapped_column(Boolean, default=False)


class MemoryLog(Base):
    __tablename__ = "memory_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    action_type: Mapped[str] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(Text)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
