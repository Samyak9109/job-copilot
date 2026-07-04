"""Career memory service.

Production uses MongoDB for durable memory. Tests can run without MongoDB by
falling back to an in-memory store when `MONGODB_URI` is intentionally empty.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field

from ..config import settings

_STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "with", "at", "by",
    "is", "are", "was", "were", "be", "as", "it", "this", "that", "i", "my", "me",
    "we", "our", "you", "your", "from", "have", "has", "will", "can", "job", "role",
}


def dataset_for(user_id: int) -> str:
    return f"user_{user_id}_career_memory"


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if t not in _STOPWORDS and len(t) > 1]


def _score_docs(docs: list[dict], query: str, top_k: int) -> list[dict]:
    q = set(_tokens(query))
    scored: list[tuple[float, dict]] = []
    for doc in docs:
        doc_tokens = _tokens(f"{doc.get('title', '')} {doc.get('memory_type', '')} {doc.get('text', '')}")
        if not doc_tokens:
            continue
        overlap = sum(1 for t in doc_tokens if t in q)
        if overlap:
            score = overlap / (1 + (len(set(doc_tokens)) ** 0.5))
            scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:top_k]]


@dataclass
class _MemoryDoc:
    ref: str
    dataset: str
    title: str
    memory_type: str
    text: str
    created_at_ts: float = field(default_factory=time.time)


class InMemoryStore:
    """Non-persistent fallback for offline tests only."""

    def __init__(self) -> None:
        self._docs: list[dict] = []

    def remember(self, dataset: str, title: str, memory_type: str, text: str) -> str:
        ref = f"{dataset}:{int(time.time() * 1000)}:{len(self._docs)}"
        self._docs.append(_MemoryDoc(ref, dataset, title, memory_type, text).__dict__)
        return ref

    def recall(self, datasets: list[str], query: str, top_k: int = 4) -> list[dict]:
        docs = [d for d in self._docs if d.get("dataset") in datasets]
        results = _score_docs(docs, query, top_k)
        if results:
            return results
        return sorted(docs, key=lambda d: d.get("created_at_ts", 0), reverse=True)[:top_k]

    def improve(self, dataset: str, note: str) -> str:
        return self.remember(dataset, "Feedback / preference", "feedback", note)

    def forget(self, dataset: str, ref: str | None = None) -> int:
        before = len(self._docs)
        if ref is None:
            self._docs = [d for d in self._docs if d.get("dataset") != dataset]
        else:
            self._docs = [d for d in self._docs if d.get("dataset") != dataset or d.get("ref") != ref]
        return before - len(self._docs)


class MongoMemoryStore:
    """Mongo-backed keyword recall used by local Docker and cloud deployments."""

    def _db(self):
        from ..database import get_database, next_id, utcnow

        return get_database(), next_id, utcnow

    def remember(self, dataset: str, title: str, memory_type: str, text: str) -> str:
        db, next_id, utcnow = self._db()
        ref = f"{dataset}:{int(time.time() * 1000)}:{next_id(db, 'memory_docs')}"
        db.memory_docs.insert_one({
            "dataset": dataset,
            "ref": ref,
            "title": title,
            "memory_type": memory_type,
            "text": text,
            "created_at": utcnow(),
            "created_at_ts": time.time(),
        })
        return ref

    def recall(self, datasets: list[str], query: str, top_k: int = 4) -> list[dict]:
        db, _, _ = self._db()
        docs = list(db.memory_docs.find({"dataset": {"$in": datasets}}))
        results = _score_docs(docs, query, top_k)
        if results:
            return results
        return list(
            db.memory_docs
            .find({"dataset": {"$in": datasets}})
            .sort("created_at", -1)
            .limit(top_k)
        )

    def improve(self, dataset: str, note: str) -> str:
        return self.remember(dataset, "Feedback / preference", "feedback", note)

    def forget(self, dataset: str, ref: str | None = None) -> int:
        db, _, _ = self._db()
        if ref is None:
            result = db.memory_docs.delete_many({"dataset": dataset})
        else:
            result = db.memory_docs.delete_one({"dataset": dataset, "ref": ref})
        return int(result.deleted_count)


_memory_store = MongoMemoryStore() if settings.mongodb_uri else InMemoryStore()
_backend_name = "mongo" if settings.mongodb_uri else "memory"


def backend_name() -> str:
    return _backend_name


async def remember(user_id: int, title: str, memory_type: str, text: str) -> tuple[str, str]:
    dataset = dataset_for(user_id)
    ref = _memory_store.remember(dataset, title, memory_type, text)
    return dataset, ref


async def recall(user_id: int, query: str, datasets: list[str] | None = None, top_k: int = 4) -> str:
    docs = _memory_store.recall(datasets or [dataset_for(user_id)], query, top_k)
    return _render_context(docs)


async def improve(user_id: int, note: str) -> str:
    dataset = dataset_for(user_id)
    _memory_store.improve(dataset, note)
    return dataset


async def forget(user_id: int, dataset: str, ref: str | None = None) -> int:
    return _memory_store.forget(dataset, ref)


def _render_context(docs: list[dict]) -> str:
    if not docs:
        return "(No relevant career memory found yet. Ask the user to upload a resume or add projects.)"
    lines = []
    for doc in docs:
        text = (doc.get("text") or "").strip().replace("\n", " ")
        if len(text) > 900:
            text = text[:900] + " ..."
        lines.append(f"- [{doc.get('memory_type', 'memory')}] {doc.get('title', '')}: {text}")
    return "\n".join(lines)
