#!/usr/bin/env bash
# Dev launcher: starts MongoDB, FastAPI, and the frontend through Docker Compose.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

cd "$ROOT"
exec docker compose up --build
