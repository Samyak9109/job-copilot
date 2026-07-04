# Job Copilot

**AI career memory + generation engine.** Job Copilot remembers your resume, projects,
job descriptions, recruiter messages, and feedback — then uses that long-term memory to
generate tailored cover letters, interview answers, resume summaries, recruiter replies,
skill-gap analyses, and search-grounded interview prep. It also tracks your applications
through a status pipeline.

> Formerly *RecallHire* — renamed and merged with the AI Job Hunt Copilot scope.

## Why it matters
Most AI tools forget your context between prompts. Job Copilot builds **long-term,
per-user career memory** in MongoDB, and uses **LangChain** to turn that recalled memory
into clean, structured, reliable application content every time.

## Tech stack
React + Vite + Tailwind · FastAPI + MongoDB Atlas / local Mongo · **LangChain** (LCEL
orchestration) · Gemini / OpenRouter · Tavily (interview grounding).

---

## Memory lifecycle
The memory layer lives in `backend/app/services/memory_service.py` and exposes four
product operations:

| Operation | Where it's used | Storage behavior |
|-----------|-----------------|------------------|
| **remember** | `POST /api/memory/upload-pdf`, `POST /api/memory/remember-text` | stores extracted text in MongoDB |
| **recall** | Before `/api/generate` and `/api/interview/prep` | retrieves relevant user memories |
| **improve** | `POST /api/feedback` | stores feedback as future memory |
| **forget** | `DELETE /api/memory/items/{id}` | deletes the memory document and hides the library item |

Datasets are **per-user** (`user_{id}_career_memory`) so each account has isolated memory.

## LangChain usage — LCEL chains (`prompt | llm | parser`)
LangChain never touches memory storage. It **consumes the text `recall()` returns**
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
- PDF **and DOCX** ingestion → `remember()`
- Memory library with `forget()`
- Generation: cover letter, interview answer, resume summary, recruiter message
- Skill-gap analysis (structured) + **cross-JD aggregation** of recurring gaps
- Search-grounded interview prep (Tavily)
- Feedback → `improve()`
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
Runs with MongoDB and the offline LLM without paid AI keys. Add `GOOGLE_API_KEY` for real
Gemini generation and `TAVILY_API_KEY` for real interview grounding.

### Frontend
```bash
cd frontend
npm install
cp .env.example .env        # VITE_API_BASE_URL=http://localhost:8000/api
npm run dev                 # http://localhost:5173
```

---

## Free deployment notes
For a hackathon submission link that still works when your laptop is off, use a free
cloud host instead of a local tunnel. The recommended free setup is Render for the
FastAPI backend and Vercel for the React frontend.

If deployed on Render's free tier, expect these limitations:
- The service may sleep after inactivity, so the first request can take 30-60 seconds.
- Use MongoDB Atlas for persistence. Render's local filesystem is temporary on the free tier,
  so do not rely on local files for judging data.
- Uploaded resume/DOCX content is extracted and stored as memory text in MongoDB; original
  uploaded files are not treated as durable storage.

For a stable judging demo, create a free MongoDB Atlas cluster and set `MONGODB_URI`.
Real AI generation can be enabled on free hosting by setting `LLM_PROVIDER=gemini` and
`GOOGLE_API_KEY`; otherwise the app can run in `LLM_PROVIDER=offline` for a key-free
fallback.

### Vercel frontend + Render backend
Deploy in this order:
1. Deploy the frontend on Vercel first so you get the frontend URL.
2. Deploy the backend on Render and set `FRONTEND_ORIGIN` to that Vercel URL.
3. Copy the Render backend URL back into Vercel as `VITE_API_BASE_URL`, then redeploy the
   frontend once.

Frontend on Vercel:
- Framework preset: Vite
- Build command: `cd frontend && npm ci && npm run build`
- Output directory: `frontend/dist`
- Temporary first deploy env: leave `VITE_API_BASE_URL` unset or set a placeholder.
- Final env after Render is live: `VITE_API_BASE_URL=https://your-render-backend.onrender.com/api`

Backend on Render:
- Root directory: `backend`
- Runtime: Docker
- Health check path: `/api/health`
- Required env: `JWT_SECRET`, `LLM_PROVIDER=gemini`, `GOOGLE_API_KEY`,
  `MONGODB_URI`, `MONGODB_DB=jobcopilot`, `FRONTEND_ORIGIN=https://your-vercel-app.vercel.app`

---

## Demo flow (for judges)
1. Register → land on the dashboard.
2. **Add Memory** → upload a resume PDF.
3. Add project text: *"Munchy — full-stack food ordering platform (React, Node.js, Express,
   MongoDB, JWT, Google OAuth)"* and *"Scribbl — real-time whiteboard (React, Redux,
   Socket.IO, Canvas)"*.
4. **Generate** → Cover Letter for a full-stack JD → watch it recall Munchy/Scribbl.
5. **Skill Gap** → paste the JD → structured match/missing cards + recurring-gap bar chart.
6. Give feedback *"Too generic"* → memory improves.
7. Generate again → notice the shift toward concrete projects.
8. **Applications** → add a job, move it through the pipeline, generate & link docs.
9. **Memory Library** → forget a recruiter note.
10. **Memory Lifecycle** → the full REMEMBERED / RECALLED / IMPROVED / FORGOTTEN / GENERATED timeline.

The demo proves: it **remembered** documents, **recalled** relevant projects, **improved**
after feedback, and **forgot** sensitive data — with LangChain producing clean, structured
output throughout.
