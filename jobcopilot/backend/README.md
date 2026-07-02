# Job Copilot — Backend (FastAPI)

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```
Docs: http://localhost:8000/docs · Health: http://localhost:8000/api/health

Works with **no API keys** (local memory + offline LLM). Add keys in `.env` to go live.

## Layout
```
app/
  main.py            FastAPI app + router registration
  config.py          env-driven settings
  database.py        SQLAlchemy engine + session
  models.py          users, memory_items, generation_history, jobs, skill_gaps, feedback, memory_logs
  schemas.py         pydantic request/response models
  auth.py            bcrypt + JWT
  dependencies.py    get_current_user (Bearer)
  routers/           auth, memory, generate, interview, jobs, analyze, feedback, lifecycle, dashboard
  services/
    cognee_service.py  remember / recall / improve / forget  (real Cognee + local fallback)
    llm_service.py     configurable LangChain chat model (Gemini/OpenRouter/offline)
    pdf_service.py     PDF + DOCX text extraction
    search_service.py  Tavily wrapper (interview grounding)
    lifecycle.py       memory_logs writer
  chains/
    chains.py          LCEL chains (prompt | llm | parser)
    output_models.py   SkillGapResult, InterviewQuestionList
  prompts/*.txt        raw prompt templates
```

## Key endpoints
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/auth/register` \| `/login` | auth (returns JWT) |
| GET | `/api/auth/me` | current user |
| POST | `/api/memory/upload-pdf` | upload PDF/DOCX → remember |
| POST | `/api/memory/remember-text` | remember pasted text |
| GET/DELETE | `/api/memory/items[/{id}]` | list / forget |
| POST | `/api/generate` | cover letter / interview answer / resume summary / recruiter message / skill gap |
| POST | `/api/interview/prep` | search-grounded interview questions |
| GET/POST/PUT/DELETE | `/api/jobs[/{id}]` | application tracker CRUD + status pipeline |
| GET | `/api/analyze/skill-gap/aggregate` | recurring skill gaps across JDs |
| POST | `/api/feedback` | feedback → improve memory |
| GET | `/api/lifecycle/logs` | lifecycle timeline |
| GET | `/api/dashboard/stats` \| `/system` | counts + active backends |

## Notes / limitations
- **Item-level forget** is exact in `local` mode. In `cognee` mode, forgetting falls back to
  dataset-level pruning where item deletion isn't supported by the installed SDK version.
- `improve()` is implemented as "add a feedback memory + re-cognify" — the most portable
  mapping across Cognee versions.
