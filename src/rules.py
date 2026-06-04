SEVERITY_BASE_SCORES = {
    "INFO": 10,
    "WARNING": 30,
    "ERROR": 60,
    "CRITICAL": 90,
}

EVENT_TYPE_ADJUSTMENTS = {
    "LINK_DOWN": 10,
    "FAILOVER_TRIGGERED": 10,
    "AUTH_FAILURE": 8,
    "SENSOR_FAULT": 6,
    "WAYPOINT_SYNC_FAIL": 6,
    "POSITION_JUMP": 5,
    "CURRENT_SPIKE": 5,
    "VOLTAGE_DROP": 4,
    "TEMP_HIGH": 4,
    "PACKET_LOSS": 3,
    "GPS_DRIFT": 2,
    "DATA_GAP": 2,
    "CALIBRATION_NEEDED": 1,
    "HEARTBEAT": -5,
    "STATUS_UPDATE": -3,
    "LINK_RESTORED": -4,
    "POWER_RESTORE": -4,
}

def calculate_priority_score(event: dict) -> int:
    severity = str(event.get("severity", "")).strip().upper()
    event_type = str(event.get("event_type", "")).strip().upper()

    base = SEVERITY_BASE_SCORES.get(severity, 0)
    adjustment = EVENT_TYPE_ADJUSTMENTS.get(event_type, 0)
    score = base + adjustment

    return max(score, 0)