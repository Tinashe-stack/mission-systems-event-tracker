from datetime import datetime
import ipaddress

from models import ALLOWED_SEVERITIES, ALLOWED_STATUSES, ALLOWED_SUBSYSTEMS

REQUIRED_FIELDS = {
    "event_id",
    "timestamp",
    "subsystem",
    "event_type",
    "severity",
    "status",
    "message",
}

def parse_timestamp(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except (TypeError, ValueError):
        return False

def valid_ip(value: str | None) -> bool:
    if value in (None, ""):
        return True
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False

def validate_event(row: dict) -> tuple[bool, list[str]]:
    errors = []

    missing = [field for field in REQUIRED_FIELDS if not str(row.get(field, "")).strip()]
    if missing:
        errors.append(f"Missing required fields: {', '.join(sorted(missing))}")

    severity = str(row.get("severity", "")).strip().upper()
    if severity and severity not in ALLOWED_SEVERITIES:
        errors.append(f"Invalid severity: {severity}")

    status = str(row.get("status", "")).strip().upper()
    if status and status not in ALLOWED_STATUSES:
        errors.append(f"Invalid status: {status}")

    subsystem = str(row.get("subsystem", "")).strip().upper()
    if subsystem and subsystem not in ALLOWED_SUBSYSTEMS:
        errors.append(f"Invalid subsystem: {subsystem}")

    timestamp = str(row.get("timestamp", "")).strip()
    if timestamp and not parse_timestamp(timestamp):
        errors.append(f"Invalid timestamp: {timestamp}")

    source_ip = str(row.get("source_ip", "")).strip()
    if source_ip and not valid_ip(source_ip):
        errors.append(f"Invalid source_ip: {source_ip}")

    return len(errors) == 0, errors