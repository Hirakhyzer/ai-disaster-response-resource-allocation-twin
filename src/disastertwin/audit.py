"""Hash-chained audit ledger for synthetic disaster-response experiments."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def append_record(path: str | Path, payload: dict) -> dict:
    """Append one record to a JSONL hash chain."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    previous_hash = _last_hash(path)
    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "previous_hash": previous_hash,
        "payload": payload,
    }
    record["record_hash"] = _hash_record(record)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
    return record


def verify_log(path: str | Path) -> dict:
    """Verify a JSONL hash chain."""
    path = Path(path)
    if not path.exists():
        return {"valid": True, "record_count": 0}
    previous = "GENESIS"
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        expected_hash = record.pop("record_hash")
        if record.get("previous_hash") != previous or _hash_record(record) != expected_hash:
            return {"valid": False, "record_count": count}
        previous = expected_hash
        count += 1
    return {"valid": True, "record_count": count}


def _last_hash(path: Path) -> str:
    if not path.exists() or path.stat().st_size == 0:
        return "GENESIS"
    last = path.read_text(encoding="utf-8").splitlines()[-1]
    return json.loads(last)["record_hash"]


def _hash_record(record: dict) -> str:
    serialized = json.dumps(record, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()
