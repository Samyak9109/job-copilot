"""Cognee memory service — the memory layer RecallHire is built around.

This module exposes the four lifecycle operations the whole product revolves around:

    remember(...)  -> ingest a career memory
    recall(...)    -> retrieve the most relevant memories for a query
    improve(...)   -> enrich memory from user feedback
    forget(...)    -> delete a memory / dataset

IMPORTANT — a note on the real Cognee SDK
------------------------------------------
The public Cognee SDK does not ship functions literally named remember/recall/
improve/forget. Its real primitives are `cognee.add()` + `cognee.cognify()`
(ingest + build the knowledge graph), `cognee.search()` (retrieve) and
`cognee.delete()` / dataset pruning (forget). This service is the adapter that maps
RecallHire's lifecycle vocabulary onto those primitives.

Two backends, chosen by COGNEE_MODE:
  * "cognee" -> uses the real Cognee SDK (needs an LLM key for cognify()).
  * "local"  -> a dependency-free embedded semantic store so the demo ALWAYS runs
                even without Cognee installed or any API key. Same interface,
                same dataset isolation, same lifecycle semantics.

Datasets are per-user (and optionally per-company) so "forget this company" is a
clean dataset delete:  user_{id}_career_memory,  user_{id}_jobs_{company_slug}
"""
from __future__ import annotations

import json
import os
import re
import threading
import time
from dataclasses import dataclass, field

from ..config import settings

_STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "memory_store")
_lock = threading.Lock()

_STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "to", "of", "in", "on", "with", "at", "by",
    "is", "are", "was", "were", "be", "as", "it", "this", "that", "i", "my", "me",
    "we", "our", "you", "your", "from", "have", "has", "will", "can", "job", "role",
}


def dataset_for(user_id: int, company_slug: str | None = None, kind: str = "career_memory") -> str:
    if company_slug:
        return f"user_{user_id}_{kind}_{slugify(company_slug)}"
    return f"user_{user_id}_career_memory"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_") or "general"


def _format_with_metadata(title: str, memory_type: str, text: str) -> str:
    return f"[TYPE: {memory_type}] [TITLE: {title}]\n{text.strip()}"


# --------------------------------------------------------------------------- #
#  Local embedded semantic store (default, zero-dependency)
# --------------------------------------------------------------------------- #
def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", (text or "").lower()) if t not in _STOPWORDS and len(t) > 1]


@dataclass
class _LocalDoc:
    ref: str
    title: str
    memory_type: str
    text: str
    created_at: float = field(default_factory=time.time)


def _store_path(dataset: str) -> str:
    os.makedirs(_STORE_DIR, exist_ok=True)
    return os.path.join(_STORE_DIR, f"{dataset}.json")


def _load(dataset: str) -> list[dict]:
    path = _store_path(dataset)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError:
            return []


def _save(dataset: str, docs: list[dict]) -> None:
    with open(_store_path(dataset), "w", encoding="utf-8") as fh:
        json.dump(docs, fh, ensure_ascii=False, indent=2)


class LocalMemory:
    """Keyword-overlap semantic recall. Good enough to prove relevant retrieval."""

    def remember(self, dataset: str, title: str, memory_type: str, text: str) -> str:
        with _lock:
            docs = _load(dataset)
            ref = f"{dataset}:{int(time.time() * 1000)}:{len(docs)}"
            docs.append(_LocalDoc(ref=ref, title=title, memory_type=memory_type, text=text).__dict__)
            _save(dataset, docs)
        return ref

    def recall(self, datasets: list[str], query: str, top_k: int = 4) -> list[dict]:
        q = set(_tokens(query))
        scored: list[tuple[float, dict]] = []
        for dataset in datasets:
            for doc in _load(dataset):
                doc_tokens = _tokens(f"{doc['title']} {doc['memory_type']} {doc['text']}")
                if not doc_tokens:
                    continue
                overlap = sum(1 for t in doc_tokens if t in q)
                # normalise a little so long docs don't always win.
                score = overlap / (1 + (len(set(doc_tokens)) ** 0.5))
                if overlap:
                    scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [d for _, d in scored[:top_k]]
        if not results:  # fall back to most-recent memories so recall is never empty
            recent: list[dict] = []
            for dataset in datasets:
                recent.extend(_load(dataset))
            recent.sort(key=lambda d: d.get("created_at", 0), reverse=True)
            results = recent[:top_k]
        return results

    def improve(self, dataset: str, note: str) -> str:
        return self.remember(dataset, "Feedback / preference", "feedback", note)

    def forget(self, dataset: str, ref: str | None = None) -> int:
        with _lock:
            docs = _load(dataset)
            if ref is None:
                removed = len(docs)
                _save(dataset, [])
                try:
                    os.remove(_store_path(dataset))
                except OSError:
                    pass
                return removed
            kept = [d for d in docs if d.get("ref") != ref]
            _save(dataset, kept)
            return len(docs) - len(kept)


# --------------------------------------------------------------------------- #
#  Real Cognee backend (best-effort; used when COGNEE_MODE=cognee)
# --------------------------------------------------------------------------- #
class CogneeMemory:
    def __init__(self) -> None:
        import cognee  # noqa: F401  (raises if not installed -> caller falls back)

        self._cognee = cognee
        if settings.cognee_api_key:
            os.environ.setdefault("LLM_API_KEY", settings.cognee_api_key)

    async def remember(self, dataset: str, title: str, memory_type: str, text: str) -> str:
        content = _format_with_metadata(title, memory_type, text)
        await self._cognee.add(content, dataset_name=dataset)
        await self._cognee.cognify([dataset])
        return dataset

    async def recall(self, datasets: list[str], query: str, top_k: int = 4) -> list[dict]:
        from cognee.api.v1.search import SearchType

        results: list[dict] = []
        for dataset in datasets:
            try:
                hits = await self._cognee.search(
                    query_type=SearchType.INSIGHTS,
                    query_text=query,
                    datasets=[dataset],
                )
            except TypeError:  # older signature
                hits = await self._cognee.search(SearchType.INSIGHTS, query)
            for h in (hits or [])[:top_k]:
                results.append({"title": dataset, "memory_type": "cognee", "text": str(h)})
        return results[:top_k]

    async def improve(self, dataset: str, note: str) -> str:
        await self._cognee.add(_format_with_metadata("Feedback", "feedback", note), dataset_name=dataset)
        await self._cognee.cognify([dataset])
        return dataset

    async def forget(self, dataset: str, ref: str | None = None) -> int:
        try:
            await self._cognee.prune.prune_data(dataset)  # type: ignore[attr-defined]
        except Exception:
            try:
                await self._cognee.delete(dataset_name=dataset)  # type: ignore[call-arg]
            except Exception:
                return 0
        return 1


# --------------------------------------------------------------------------- #
#  Public async interface (backend-agnostic)
# --------------------------------------------------------------------------- #
_local = LocalMemory()
_cognee_backend: CogneeMemory | None = None
_backend_name = "local"


def _resolve_backend():
    global _cognee_backend, _backend_name
    if settings.cognee_mode == "cognee":
        if _cognee_backend is None:
            try:
                _cognee_backend = CogneeMemory()
                _backend_name = "cognee"
            except Exception:
                _cognee_backend = None
                _backend_name = "local (cognee import failed)"
        return _cognee_backend
    _backend_name = "local"
    return None


def backend_name() -> str:
    _resolve_backend()
    return _backend_name


async def remember(user_id: int, title: str, memory_type: str, text: str, company_slug: str | None = None) -> tuple[str, str]:
    dataset = dataset_for(user_id, company_slug)
    backend = _resolve_backend()
    if backend is not None:
        ref = await backend.remember(dataset, title, memory_type, text)
    else:
        ref = _local.remember(dataset, title, memory_type, text)
    return dataset, ref


async def recall(user_id: int, query: str, datasets: list[str] | None = None, top_k: int = 4) -> str:
    datasets = datasets or [dataset_for(user_id)]
    backend = _resolve_backend()
    if backend is not None:
        docs = await backend.recall(datasets, query, top_k)
    else:
        docs = _local.recall(datasets, query, top_k)
    return _render_context(docs)


async def recall_docs(user_id: int, query: str, datasets: list[str] | None = None, top_k: int = 4) -> list[dict]:
    datasets = datasets or [dataset_for(user_id)]
    backend = _resolve_backend()
    if backend is not None:
        return await backend.recall(datasets, query, top_k)
    return _local.recall(datasets, query, top_k)


async def improve(user_id: int, note: str, company_slug: str | None = None) -> str:
    dataset = dataset_for(user_id, company_slug)
    backend = _resolve_backend()
    if backend is not None:
        await backend.improve(dataset, note)
    else:
        _local.improve(dataset, note)
    return dataset


async def forget(user_id: int, dataset: str, ref: str | None = None) -> int:
    backend = _resolve_backend()
    if backend is not None:
        return await backend.forget(dataset, ref)
    return _local.forget(dataset, ref)


def _render_context(docs: list[dict]) -> str:
    if not docs:
        return "(No relevant career memory found yet. Ask the user to upload a resume or add projects.)"
    lines = []
    for d in docs:
        text = (d.get("text") or "").strip().replace("\n", " ")
        if len(text) > 900:
            text = text[:900] + " ..."
        lines.append(f"- [{d.get('memory_type', 'memory')}] {d.get('title', '')}: {text}")
    return "\n".join(lines)
