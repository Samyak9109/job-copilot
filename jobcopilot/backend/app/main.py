from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .routers import (
    analyze,
    auth,
    dashboard,
    feedback,
    generate,
    interview,
    jobs,
    lifecycle,
    memory,
)

app = FastAPI(
    title="Job Copilot API",
    description="AI career memory + generation engine — Cognee lifecycle memory orchestrated by LangChain.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    init_db()


@app.get("/api/health", tags=["health"])
def health():
    return {"status": "ok", "service": "Job Copilot"}


app.include_router(auth.router)
app.include_router(memory.router)
app.include_router(generate.router)
app.include_router(interview.router)
app.include_router(jobs.router)
app.include_router(analyze.router)
app.include_router(feedback.router)
app.include_router(lifecycle.router)
app.include_router(dashboard.router)
