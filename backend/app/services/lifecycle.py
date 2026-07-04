"""Helper for recording Cognee lifecycle events into the memory_logs table.

Every remember / recall / improve / forget / generate action funnels through here so
the Lifecycle dashboard can render a single, trustworthy timeline of memory activity.
"""
import json

from ..database import next_id, public_doc, utcnow

VALID_ACTIONS = {"REMEMBERED", "RECALLED", "IMPROVED", "FORGOTTEN", "GENERATED"}


def log_action(
    db,
    user_id: int,
    action_type: str,
    description: str,
    metadata: dict | None = None,
) -> dict:
    action_type = action_type.upper()
    if action_type not in VALID_ACTIONS:
        action_type = "GENERATED"
    entry = dict(
        id=next_id(db, "memory_logs"),
        user_id=user_id,
        action_type=action_type,
        description=description[:2000],
        metadata_json=json.dumps(metadata) if metadata else None,
        created_at=utcnow(),
    )
    db.memory_logs.insert_one(entry)
    return public_doc(entry)
