"""Tavily search wrapper used ONLY to ground interview-prep questions in real,
candidate-reported interview experiences (Glassdoor/AmbitionBox/Reddit surfaced via
search — snippets only, never a full-page scrape).

Falls back to an empty result set (and the chain says so) if no TAVILY_API_KEY is set.
"""
from ..config import settings


def search_interview_questions(company: str, role: str, max_results: int = 6) -> list[dict]:
    query = f"{company} {role} interview questions asked candidate experience"
    if not settings.tavily_api_key:
        return []
    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=settings.tavily_api_key)
        resp = client.search(query=query, max_results=max_results, search_depth="basic")
        out = []
        for r in resp.get("results", [])[:max_results]:
            out.append(
                {
                    "title": r.get("title", ""),
                    "snippet": (r.get("content", "") or "")[:400],
                    "url": r.get("url", ""),
                }
            )
        return out
    except Exception:
        return []


def format_snippets(snippets: list[dict]) -> str:
    if not snippets:
        return "(No live search results available — generate from role patterns and label them as such.)"
    return "\n".join(f"- {s['title']}: {s['snippet']} ({s['url']})" for s in snippets)
