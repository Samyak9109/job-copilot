from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from .config import settings


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _mongo():
    from pymongo import ASCENDING, MongoClient, ReturnDocument

    return ASCENDING, MongoClient, ReturnDocument


@lru_cache
def get_client():
    _, MongoClient, _ = _mongo()
    return MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)


def get_database():
    return get_client()[settings.mongodb_db]


def get_db():
    yield get_database()


def next_id(db, name: str) -> int:
    _, _, ReturnDocument = _mongo()
    doc = db.counters.find_one_and_update(
        {"_id": name},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(doc["seq"])


def public_doc(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    if doc is None:
        return None
    out = dict(doc)
    out.pop("_id", None)
    return out


def init_db() -> None:
    ASCENDING, _, _ = _mongo()
    db = get_database()

    db.users.create_index([("email", ASCENDING)], unique=True)
    db.memory_items.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)])
    db.memory_items.create_index([("user_id", ASCENDING), ("is_deleted", ASCENDING)])
    db.memory_docs.create_index([("dataset", ASCENDING), ("ref", ASCENDING)], unique=True)
    db.generation_history.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)])
    db.generation_history.create_index([("user_id", ASCENDING), ("job_id", ASCENDING)])
    db.jobs.create_index([("user_id", ASCENDING), ("updated_date", ASCENDING)])
    db.skill_gaps.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)])
    db.feedback.create_index([("user_id", ASCENDING), ("generation_id", ASCENDING)])
    db.memory_logs.create_index([("user_id", ASCENDING), ("created_at", ASCENDING)])
