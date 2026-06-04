from dataclasses import dataclass
from typing import Optional

ALLOWED_SUBSYSTEMS = {"NAV", "COMMS", "POWER", "SENSOR"}
ALLOWED_SEVERITIES = {"INFO", "WARNING", "ERROR", "CRITICAL"}
ALLOWED_STATUSES = {"NEW", "ACK", "RESOLVED"}

@dataclass
class Event:
    event_id: str
    timestamp: str
    subsystem: str
    event_type: str
    severity: str
    status: str
    message: str
    source_host: Optional[str] = None
    source_ip: Optional[str] = None
    priority_score: Optional[int] = None