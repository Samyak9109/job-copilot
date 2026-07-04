# Job Copilot

**AI career memory + generation engine.** Job Copilot remembers your resume, projects,
job descriptions, recruiter messages, and feedback — then uses that long-term memory to
generate tailored cover letters, interview answers, resume summaries, recruiter replies,
skill-gap analyses, and search-grounded interview prep. It also tracks your applications
through a status pipeline.

> Formerly *RecallHire* — renamed and merged with the AI Job Hunt Copilot scope.

## Why it matters
Most AI tools forget your context between prompts. Job Copilot builds **long-term,
per-user career memory** with **Cognee**, and uses **LangChain** to turn that recalled
memory into clean, structured, reliable application content every time.

## Tech stack
React + Vite + Tailwind · FastAPI + SQLAlchemy + SQLite · **Cognee** (memory) ·
**LangChain** (LCEL orchestration) · Gemini / OpenRouter · Tavily (interview grounding).

---

## Cognee usage — the four lifecycle operations
Cognee is the memory layer the whole product is designed around. The adapter lives in
`backend/app/services/cognee_service.py` and exposes four operations:

| Operation | Where it's used | Maps to real Cognee SDK |
|-----------|-----------------|-------------------------|
| **remember** | `POST /api/memory/upload-pdf`, `POST /api/memory/remember-text` — every resume, project, JD, recruiter note, feedback | `cognee.add()` + `cognee.cognify()` |
| **recall** | Before **every** generation (`/api/generate`, `/api/interview/prep`) to pull the most relevant memories | `cognee.search()` |
| **improve** | `POST /api/feedback` — user ratings & preferences enrich memory | `cognee.add()` (feedback note) + `cognee.cognify()` |
| **forget** | `DELETE /api/memory/items/{id}` — delete sensitive/obsolete memory | `cognee.delete()` / dataset prune |

Datasets are **per-user** (`user_{id}_career_memory`) and optionally **per-company**
(`user_{id}_jobs_{company_slug}`) so "forget this company" is a clean dataset delete.

### Two memory backends (`COGNEE_MODE`)
- `cognee` — the **real Cognee SDK** (needs an LLM key for `cognify()`).
- `local` — a **dependency-free embedded semantic store** (keyword-overlap recall) so the
  demo always runs, even with no Cognee install and no API keys. Same interface, same
  dataset isolation, same lifecycle semantics.

> **Honest note:** Cognee's public SDK does not literally export `remember/recall/improve/
> forget`. Those are RecallHire/Job Copilot's lifecycle vocabulary; the adapter maps them
> onto Cognee's real `add`/`cognify`/`search`/`delete` primitives.

## LangChain usage — LCEL chains (`prompt | llm | parser`)
LangChain never touches memory storage. It **consumes the text Cognee's `recall()` returns**
(passed in as `context`) and turns it into structured output. Chains live in
`backend/app/chains/chains.py`; prompts in `backend/app/prompts/*.txt`.

| Chain | Output parser | Output |
|-------|---------------|--------|
| Cover letter | `StrOutputParser` | text |
| Interview answer | `StrOutputParser` | text (STAR) |
| Resume summary | `StrOutputParser` | text |
| Recruiter message | `StrOutputParser` | text |
| Skill gap | `PydanticOutputParser(SkillGapResult)` | structured JSON → cards |
| Interview prep | `PydanticOutputParser(InterviewQuestionList)` | structured JSON, grounded by Tavily |

`llm_service.py` returns a configurable chat model (Gemini → OpenRouter → **offline
deterministic generator**), all as LangChain Runnables, so the LCEL pipeline works
end-to-end even with zero API keys.

---

## Features
- JWT auth (bcrypt), multi-user, per-user memory isolation
- PDF **and DOCX** ingestion → Cognee `remember()`
- Memory library with `forget()`
- Generation: cover letter, interview answer, resume summary, recruiter message
- Skill-gap analysis (structured) + **cross-JD aggregation** of recurring gaps
- Search-grounded interview prep (Tavily)
- Feedback → Cognee `improve()`
- **Application tracker**: jobs CRUD, `applied → interview → offer → rejected` pipeline with
  per-stage dates, and generated documents linked to each job
- Memory lifecycle dashboard (REMEMBERED / RECALLED / IMPROVED / FORGOTTEN / GENERATED)

---

## Setup

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # set GOOGLE_API_KEY / TAVILY_API_KEY if you have them
uvicorn app.main:app --reload --port 8000
```
Runs out-of-the-box with **no keys** (`COGNEE_MODE=local`, offline LLM). Add
`GOOGLE_API_KEY` for real generation and `TAVILY_API_KEY` for real interview grounding.
To use the **real Cognee SDK**: `pip install -r requirements-cognee.txt` (needs Python ≤
3.12) and set `COGNEE_MODE=cognee` + `COGNEE_API_KEY`. Cognee is intentionally kept out of
the core `requirements.txt` so the app always installs and runs.

### Frontend
```bash
cd frontend
npm install
cp .env.example .env        # VITE_API_BASE_URL=http://localhost:8000/api
npm run dev                 # http://localhost:5173
```

---

## Demo flow (for judges)
1. Register → land on the dashboard.
2. **Add Memory** → upload a resume PDF (remembered by Cognee).
3. Add project text: *"Munchy — full-stack food ordering platform (React, Node.js, Express,
   MongoDB, JWT, Google OAuth)"* and *"Scribbl — real-time whiteboard (React, Redux,
   Socket.IO, Canvas)"*.
4. **Generate** → Cover Letter for a full-stack JD → watch it recall Munchy/Scribbl.
5. **Skill Gap** → paste the JD → structured match/missing cards + recurring-gap bar chart.
6. Give feedback *"Too generic"* → Cognee **improves** memory.
7. Generate again → notice the shift toward concrete projects.
8. **Applications** → add a job, move it through the pipeline, generate & link docs.
9. **Memory Library** → forget a recruiter note.
10. **Memory Lifecycle** → the full REMEMBERED / RECALLED / IMPROVED / FORGOTTEN / GENERATED timeline.

The demo proves: it **remembered** documents, **recalled** relevant projects, **improved**
after feedback, and **forgot** sensitive data — with LangChain producing clean, structured
output throughout.
