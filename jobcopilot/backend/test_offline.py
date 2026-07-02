"""Dependency-free smoke test for the two demo-critical, key-free paths:
  1. the local Cognee memory store (remember -> relevant recall -> forget)
  2. the offline LLM generator (must emit schema-valid JSON for the LCEL parsers)

Run:  python test_offline.py   (no pip install needed)
"""
import importlib.util
import json
import sys
import types


def _load(mod_name, path):
    spec = importlib.util.spec_from_file_location(mod_name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = m
    spec.loader.exec_module(m)
    return m


def _stub_env():
    app = types.ModuleType("app"); app.__path__ = ["app"]; sys.modules["app"] = app
    cfg = types.ModuleType("app.config")

    class S:
        cognee_mode = "local"; cognee_api_key = ""
        llm_provider = "offline"; google_api_key = ""; openrouter_api_key = ""
        openrouter_model = ""; gemini_model = ""

    cfg.settings = S(); sys.modules["app.config"] = cfg
    svcs = types.ModuleType("app.services"); svcs.__path__ = ["app/services"]
    sys.modules["app.services"] = svcs
    lc = types.ModuleType("langchain_core"); lc.__path__ = []
    run = types.ModuleType("langchain_core.runnables")
    run.RunnableLambda = lambda fn: fn
    sys.modules["langchain_core"] = lc; sys.modules["langchain_core.runnables"] = run


class _PV:
    def __init__(self, t): self._t = t
    def to_string(self): return self._t


def test_local_memory():
    import asyncio
    cs = _load("app.services.cognee_service", "app/services/cognee_service.py")

    async def run():
        ds, ref = await cs.remember(1, "Munchy", "project", "Munchy: React Node.js Express MongoDB")
        await cs.remember(1, "Scribbl", "project", "Scribbl: React Redux Socket.IO Canvas")
        ctx = await cs.recall(1, "React Node full-stack projects")
        assert "Munchy" in ctx and "Scribbl" in ctx, ctx
        assert await cs.forget(1, ds, ref) == 1
        # cleanup the second doc's dataset file
        await cs.forget(1, ds)

    asyncio.run(run())
    print("[ok] local memory: remember -> recall -> forget")


def test_offline_generator():
    m = _load("app.services.llm_service", "app/services/llm_service.py")
    ctx = ("CANDIDATE MEMORY (recalled by Cognee):\n"
           "- [project] Munchy: React Node.js Express MongoDB JWT\n")
    jd = "JOB DESCRIPTION:\nReact, Node.js, TypeScript, Docker, AWS.\n"

    sg = json.loads(m._offline_generate(_PV(ctx + jd + "\nmatched_skills SkillGapResult")))
    required = {"matched_skills", "missing_skills", "relevant_projects",
                "resume_keywords", "learning_plan", "score", "recommendation"}
    assert required <= set(sg), sg
    assert isinstance(sg["score"], int)
    print("[ok] offline skill-gap JSON:", sg["matched_skills"], "->", sg["missing_skills"])

    ip = json.loads(m._offline_generate(_PV("COMPANY:\nRazorpay\n\nROLE:\nEngineer\n\n" + ctx +
                                            "\nsuggested_focus InterviewQuestion (No live search results available)")))
    assert len(ip["questions"]) >= 4
    assert all({"question", "category", "suggested_focus"} <= set(q) for q in ip["questions"])
    print("[ok] offline interview-prep JSON:", len(ip["questions"]), "questions")

    cl = m._offline_generate(_PV(ctx + jd + "\nWrite a personalized cover letter"))
    assert "Dear" in cl and len(cl) > 120
    print("[ok] offline cover letter:", len(cl), "chars")


if __name__ == "__main__":
    _stub_env()
    test_local_memory()
    test_offline_generator()
    print("\nALL OFFLINE-PATH TESTS PASSED")
