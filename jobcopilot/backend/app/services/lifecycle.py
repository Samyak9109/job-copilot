"""Helper for recording Cognee lifecycle events into the memory_logs table.

Every remember / recall / improve / forget / generate action funnels through here so
the Lifecycle dashboard can render a single, trustworthy timeline of memory activity.
"""
import json

from sqlalchemy.orm import Session

from ..models import MemoryLog

VALID_ACTIONS = {"REMEMBERED", "RECALLED", "IMPROVED", "FORGOTTEN", "GENERATED"}


def log_action(
    db: Session,
    user_id: int,
    action_type: str,
    description: str,
    metadata: dict | None = None,
) -> MemoryLog:
    action_type = action_type.upper()
    if action_type not in VALID_ACTIONS:
        action_type = "GENERATED"
    entry = MemoryLog(
        user_id=user_id,
        action_type=action_type,
        description=description[:2000],
        metadata_json=json.dumps(metadata) if metadata else None,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
