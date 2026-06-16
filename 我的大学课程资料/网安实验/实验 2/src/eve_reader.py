"""Read normalized alert records from Suricata EVE JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def parse_eve_line(line: str) -> dict[str, Any] | None:
    try:
        event = json.loads(line)
    except (json.JSONDecodeError, TypeError):
        return None

    if event.get("event_type") != "alert" or not isinstance(event.get("alert"), dict):
        return None

    alert = event["alert"]
    action = str(alert.get("action", "unknown"))
    return {
        "timestamp": event.get("timestamp", ""),
        "signature": alert.get("signature", "unknown signature"),
        "category": alert.get("category", "unknown category"),
        "action": action,
        "blocked": action.lower() == "blocked",
        "severity": alert.get("severity"),
        "src_ip": event.get("src_ip", ""),
        "src_port": event.get("src_port"),
        "dest_ip": event.get("dest_ip", ""),
        "dest_port": event.get("dest_port"),
        "proto": event.get("proto", ""),
    }


def read_recent_alerts(path: str | Path, limit: int = 100) -> list[dict[str, Any]]:
    eve_path = Path(path)
    if not eve_path.exists():
        return []

    alerts: list[dict[str, Any]] = []
    with eve_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            parsed = parse_eve_line(line)
            if parsed is not None:
                alerts.append(parsed)

    return list(reversed(alerts[-limit:]))

