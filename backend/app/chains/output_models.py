"""Pydantic models that force structured, render-ready JSON out of the LLM.

These are handed to LangChain's PydanticOutputParser so the frontend can render cards
directly with no manual parsing of free-form LLM text.
"""
from pydantic import BaseModel, Field


class SkillGapResult(BaseModel):
    matched_skills: list[str] = Field(description="Skills the candidate already has that the job needs")
    missing_skills: list[str] = Field(description="Skills the job needs that are missing from the candidate's memory")
    relevant_projects: list[str] = Field(description="Candidate projects most relevant to this job")
    resume_keywords: list[str] = Field(description="Keywords to add to the resume for ATS")
    learning_plan: str = Field(description="Short, concrete plan to close the gaps")
    score: int = Field(description="Overall match score 0-100")
    recommendation: str = Field(description="One-line recommendation")


class InterviewQuestion(BaseModel):
    question: str
    category: str = Field(description="technical | behavioral | company-fit | project-deep-dive")
    suggested_focus: str = Field(description="What the candidate should emphasise, drawn from their memory")
    grounding: str = Field(
        default="likely-based-on-role",
        description="commonly-reported (supported by a search snippet) | likely-based-on-role",
    )


class InterviewQuestionList(BaseModel):
    questions: list[InterviewQuestion]
