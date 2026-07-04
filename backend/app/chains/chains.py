"""All LangChain LCEL chains: prompt | llm | output_parser.

LangChain does NOT touch memory storage. It only consumes the text that Cognee's
recall() returns (passed in as `context` / `user_context`) and turns it, plus the
user's current request, into clean, structured output.
"""
from pathlib import Path

from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from ..services.llm_service import get_llm
from .output_models import InterviewQuestionList, SkillGapResult

_PROMPTS = Path(__file__).resolve().parent.parent / "prompts"


def _load(name: str) -> str:
    return (_PROMPTS / name).read_text(encoding="utf-8")


_SYSTEM = _load("system_prompt.txt")


def _prompt(human_file: str) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([("system", _SYSTEM), ("human", _load(human_file))])


# ---- individual chain builders (built fresh so provider/keys are picked up live) ----
def cover_letter_chain():
    return _prompt("cover_letter.txt") | get_llm() | StrOutputParser()


def interview_answer_chain():
    return _prompt("interview_answer.txt") | get_llm() | StrOutputParser()


def resume_summary_chain():
    return _prompt("resume_summary.txt") | get_llm() | StrOutputParser()


def recruiter_message_chain():
    return _prompt("recruiter_message.txt") | get_llm() | StrOutputParser()


def skill_gap_chain():
    parser = PydanticOutputParser(pydantic_object=SkillGapResult)
    prompt = _prompt("skill_gap_analysis.txt").partial(format_instructions=parser.get_format_instructions())
    return prompt | get_llm() | parser


def interview_prep_chain():
    parser = PydanticOutputParser(pydantic_object=InterviewQuestionList)
    prompt = _prompt("interview_prep.txt").partial(format_instructions=parser.get_format_instructions())
    return prompt | get_llm() | parser


# ---- dispatchers used by the routers ----
def run_generation(output_type: str, *, job_description: str, context: str, extra_instructions: str = "") -> dict:
    if output_type == "cover_letter":
        text = cover_letter_chain().invoke(
            {"job_description": job_description, "context": context, "extra_instructions": extra_instructions or "None."}
        )
        return {"text": text}
    if output_type == "interview_answer":
        text = interview_answer_chain().invoke(
            {"question_or_job_description": job_description, "context": context}
        )
        return {"text": text}
    if output_type == "resume_summary":
        text = resume_summary_chain().invoke({"job_description": job_description, "context": context})
        return {"text": text}
    if output_type == "recruiter_message":
        text = recruiter_message_chain().invoke({"job_description": job_description, "context": context})
        return {"text": text}
    if output_type == "skill_gap_analysis":
        result: SkillGapResult = skill_gap_chain().invoke({"job_description": job_description, "context": context})
        return {"structured": result.model_dump()}
    raise ValueError(f"Unknown output_type: {output_type}")


def run_interview_prep(*, company, role, job_description, user_context, company_history, search_snippets) -> dict:
    result: InterviewQuestionList = interview_prep_chain().invoke(
        {
            "company": company,
            "role": role,
            "job_description": job_description or "(not provided)",
            "user_context": user_context,
            "company_history": company_history or "(none)",
            "search_snippets": search_snippets,
        }
    )
    return result.model_dump()
