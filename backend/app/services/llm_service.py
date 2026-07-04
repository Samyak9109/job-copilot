"""Returns a configured LangChain chat model.

Provider is configurable (Gemini via langchain-google-genai, or OpenRouter via
langchain-openai with a custom base_url). If no key is configured, we return an
*offline* LangChain Runnable so the whole LCEL pipeline (prompt | llm | parser)
still works end-to-end for demos — chains.py never has to know the difference.
"""
from __future__ import annotations

import json
import re

from langchain_core.runnables import RunnableLambda

from ..config import settings

# skill lexicon used by the offline generator for a believable skill-gap analysis
_SKILL_LEXICON = [
    "react", "node.js", "node", "express", "mongodb", "postgresql", "sql", "python",
    "fastapi", "django", "flask", "javascript", "typescript", "redux", "socket.io",
    "docker", "kubernetes", "aws", "gcp", "azure", "git", "rest", "graphql", "redis",
    "tailwind", "html", "css", "java", "c++", "go", "rust", "next.js", "vue", "angular",
    "langchain", "llm", "ci/cd", "jest", "pytest", "oauth", "jwt", "microservices",
    "leadership", "communication", "agile", "testing", "figma",
]

_active_provider = "offline"


def active_provider() -> str:
    return _active_provider


def get_llm():
    """Return a LangChain chat model (or offline Runnable) usable in an LCEL chain."""
    global _active_provider
    provider = settings.llm_provider.lower()

    if provider in ("gemini", "auto") and settings.google_api_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            _active_provider = "gemini"
            return ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                google_api_key=settings.google_api_key,
                temperature=0.5,
            )
        except Exception:
            pass

    if provider in ("openrouter", "auto") and settings.openrouter_api_key:
        try:
            from langchain_openai import ChatOpenAI

            _active_provider = "openrouter"
            return ChatOpenAI(
                model=settings.openrouter_model,
                api_key=settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=0.5,
            )
        except Exception:
            pass

    # No usable provider -> offline deterministic generator, still a LangChain Runnable.
    _active_provider = "offline"
    return RunnableLambda(_offline_generate)


# --------------------------------------------------------------------------- #
#  Offline generator (deterministic, key-free) — keeps demos alive
# --------------------------------------------------------------------------- #
def _to_text(prompt_value) -> str:
    if hasattr(prompt_value, "to_string"):
        return prompt_value.to_string()
    if isinstance(prompt_value, str):
        return prompt_value
    return str(prompt_value)


def _section(text: str, header: str) -> str:
    m = re.search(rf"{re.escape(header)}\s*(.*?)(?=\n[A-Z][A-Z \(\)/]+:|\Z)", text, re.S)
    return (m.group(1).strip() if m else "")


def _memory_bullets(context: str) -> list[str]:
    return [ln.strip("- ").strip() for ln in context.splitlines() if ln.strip().startswith("- ")][:6]


def _skills_in(text: str) -> set[str]:
    low = text.lower()
    return {s for s in _SKILL_LEXICON if s in low}


def _offline_generate(prompt_value) -> str:
    text = _to_text(prompt_value)
    context = _section(text, "CANDIDATE MEMORY (recalled by Cognee):") or _section(text, "CANDIDATE MEMORY:")
    jd = _section(text, "JOB DESCRIPTION:")
    lower = text.lower()

    # ---- structured: skill gap ----
    if "matched_skills" in lower or "skillgapresult" in lower:
        return _offline_skill_gap(context, jd)

    # ---- structured: interview prep list ----
    if "suggested_focus" in lower or "interviewquestion" in lower:
        return _offline_interview_prep(context, jd, text)

    bullets = _memory_bullets(context)
    proj = next((b for b in bullets if "project" in b.lower()), bullets[0] if bullets else "your recent project")

    # ---- resume summary ----
    if "resume summary" in lower:
        return (
            f"Results-driven candidate with hands-on experience across the technologies this role targets. "
            f"Recent work includes {proj[:160]}. Strong at translating requirements into shipped, tested features, "
            f"and comfortable owning problems end to end. Eager to bring this to the team."
        )

    # ---- recruiter message ----
    if "recruiter" in lower:
        return (
            "Hi — I came across this opening and it lines up closely with what I do. "
            f"I've recently built {proj[:120]}, which maps directly to your requirements. "
            "I'd love to share more about how I could contribute — open to a quick chat this week?"
        )

    # ---- interview answer (STAR) ----
    if "star" in lower or "interview answer" in lower or "interview_answer" in lower:
        return (
            "**Situation.** In a recent project I owned a feature under a tight deadline.\n"
            f"**Task.** I needed to deliver it reliably — drawing on {proj[:140]}.\n"
            "**Action.** I broke the work into milestones, wrote tests as I went, and communicated blockers early.\n"
            "**Result.** We shipped on time; the feature held up in production and the approach became a template for the team."
        )

    # ---- default: cover letter ----
    return _offline_cover_letter(context, jd, bullets)


def _offline_cover_letter(context: str, jd: str, bullets: list[str]) -> str:
    matched = sorted(_skills_in(context) & _skills_in(jd)) or sorted(_skills_in(context))[:4]
    skills_line = ", ".join(matched[:5]) if matched else "the core skills you're hiring for"
    proj = next((b for b in bullets if "project" in b.lower()), bullets[0] if bullets else "")
    proj_line = f" My work on {proj[:180]} is directly relevant here." if proj else ""
    return (
        "Dear Hiring Manager,\n\n"
        "I'm excited to apply for this role. Having reviewed the description, I believe my background is a strong match "
        f"for what you're looking for.\n\n"
        f"My strongest overlap with your requirements is in {skills_line}.{proj_line} "
        "Across my projects I've focused on shipping reliable, well-tested software and collaborating closely with teammates.\n\n"
        "I'd welcome the chance to discuss how I can contribute to your team. Thank you for your consideration.\n\n"
        "Best regards,\nThe Candidate"
    )


def _offline_skill_gap(context: str, jd: str) -> str:
    ctx_skills = _skills_in(context)
    jd_skills = _skills_in(jd) or ctx_skills
    matched = sorted(jd_skills & ctx_skills)
    missing = sorted(jd_skills - ctx_skills)
    projects = [b.strip("- ").strip()[:120] for b in context.splitlines() if "project" in b.lower()][:4]
    score = int(round(100 * (len(matched) / max(1, len(jd_skills)))))
    result = {
        "matched_skills": matched or sorted(ctx_skills)[:5],
        "missing_skills": missing[:8],
        "relevant_projects": projects or ["(add project memories to improve this)"],
        "resume_keywords": sorted(jd_skills)[:10],
        "learning_plan": (
            "Focus next on: " + ", ".join(missing[:4]) + "."
            if missing
            else "Your profile already covers the core requirements — deepen with a portfolio project."
        ),
        "score": score,
        "recommendation": (
            "Strong match — apply with confidence." if score >= 70
            else "Decent match — close 1-2 gaps before applying." if score >= 40
            else "Stretch role — build the missing skills first."
        ),
    }
    return json.dumps(result)


def _offline_interview_prep(context: str, jd: str, full: str) -> str:
    company = _section(full, "COMPANY:") or "the company"
    has_search = "no live search results" not in full.lower()
    skills = sorted(_skills_in(context) | _skills_in(jd))[:4] or ["your core stack"]
    projects = [b.strip("- ").strip()[:80] for b in context.splitlines() if "project" in b.lower()][:2]
    focus_proj = projects[0] if projects else "your strongest project"
    ground = "commonly-reported" if has_search else "likely-based-on-role"
    questions = [
        {
            "question": "Walk me through a project you're proud of and your specific role in it.",
            "category": "project-deep-dive",
            "suggested_focus": f"Lead with {focus_proj}; quantify impact.",
            "grounding": ground,
        },
        {
            "question": f"How would you design a scalable system using {skills[0]}?",
            "category": "technical",
            "suggested_focus": f"Tie back to your experience with {', '.join(skills[:3])}.",
            "grounding": "likely-based-on-role",
        },
        {
            "question": "Tell me about a time you handled a conflict or a tight deadline.",
            "category": "behavioral",
            "suggested_focus": "Use STAR; emphasise ownership and communication.",
            "grounding": "likely-based-on-role",
        },
        {
            "question": f"Why do you want to work at {company} specifically?",
            "category": "company-fit",
            "suggested_focus": f"Connect {company}'s mission to {focus_proj}.",
            "grounding": ground,
        },
    ]
    return json.dumps({"questions": questions})
