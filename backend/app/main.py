from contextlib import asynccontextmanager

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


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Job Copilot API",
    description="AI career memory + generation engine with MongoDB memory and LangChain orchestration.",
    version="1.0.0",
    lifespan=lifespan,
)

# FRONTEND_ORIGIN may be a comma-separated list of allowed origins (prod + local).
_origins = {o.strip() for o in settings.frontend_origin.split(",") if o.strip()}
_origins |= {"http://localhost:5173", "http://127.0.0.1:5173"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
