#!/usr/bin/env bash
# Dev launcher: starts the FastAPI backend and the Vite frontend together.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

( cd "$ROOT/backend" && \
  [ -d .venv ] || python3 -m venv .venv; \
  . .venv/bin/activate && pip install -q -r requirements.txt && \
  [ -f .env ] || cp .env.example .env && \
  uvicorn app.main:app --reload --port 8000 ) &

( cd "$ROOT/frontend" && \
  [ -d node_modules ] || npm install && \
  [ -f .env ] || cp .env.example .env && \
  npm run dev ) &

wait
