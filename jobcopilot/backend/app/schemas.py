from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

# ---- Auth ----


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Memory ----


class RememberTextIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    memory_type: str = "other"
    text: str = Field(min_length=1)


class MemoryItemOut(BaseModel):
    id: int
    title: str
    memory_type: str
    source_type: str
    source_filename: str | None
    cognee_dataset_name: str
    content_preview: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Generation ----


class GenerateIn(BaseModel):
    output_type: str
    job_description: str = ""
    extra_instructions: str = ""
    job_id: int | None = None  # optionally link this generation to a tracked job


class GenerateOut(BaseModel):
    generation_id: int
    output_type: str
    output_text: str | None = None
    structured: dict | None = None
    recalled_context_preview: str


# ---- Interview prep ----


class InterviewPrepIn(BaseModel):
    company: str
    role: str
    job_description: str = ""


class InterviewQuestionOut(BaseModel):
    question: str
    category: str
    suggested_focus: str
    grounding: str = "likely-based-on-role"


class InterviewPrepOut(BaseModel):
    generation_id: int
    questions: list[InterviewQuestionOut]
    sources: list[dict]
    recalled_context_preview: str


# ---- Feedback ----


class FeedbackIn(BaseModel):
    generation_id: int
    rating: str
    feedback_text: str = ""


# ---- Lifecycle / dashboard ----


class MemoryLogOut(BaseModel):
    id: int
    action_type: str
    description: str
    metadata_json: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_memory_items: int
    total_generations: int
    remembered_count: int
    recalled_count: int
    improved_count: int
    forgotten_count: int
    generated_count: int
    last_activity: datetime | None


# ---- Application tracker (jobs) ----

JOB_STATUSES = ["applied", "interview", "offer", "rejected"]


class JobIn(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    title: str = Field(min_length=1, max_length=200)
    jd_text: str = ""
    status: str = "applied"


class JobUpdate(BaseModel):
    company: str | None = None
    title: str | None = None
    jd_text: str | None = None
    status: str | None = None


class JobOut(BaseModel):
    id: int
    company: str
    title: str
    jd_text: str
    status: str
    applied_date: datetime
    interview_date: datetime | None
    offer_date: datetime | None
    rejected_date: datetime | None
    updated_date: datetime

    class Config:
        from_attributes = True


class GenerationOut(BaseModel):
    id: int
    job_id: int | None
    output_type: str
    output_text: str
    created_at: datetime

    class Config:
        from_attributes = True


class JobDetailOut(JobOut):
    generations: list[GenerationOut] = []


# ---- Skill gap ----


class SkillDemand(BaseModel):
    skill: str
    count: int


class SkillGapAggregate(BaseModel):
    analyses: int
    recurring_missing: list[SkillDemand]
    recurring_matched: list[SkillDemand]
    average_score: float


TokenOut.model_rebuild()
