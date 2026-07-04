"""MongoDB collection names used by the application.

The API keeps stable integer `id` fields for frontend compatibility; MongoDB's
native `_id` remains internal and is stripped from responses.
"""

USERS = "users"
MEMORY_ITEMS = "memory_items"
MEMORY_DOCS = "memory_docs"
GENERATION_HISTORY = "generation_history"
JOBS = "jobs"
SKILL_GAPS = "skill_gaps"
FEEDBACK = "feedback"
MEMORY_LOGS = "memory_logs"
