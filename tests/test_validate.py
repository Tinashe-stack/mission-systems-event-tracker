from validate import validate_event


def test_valid_event_passes_validation():
    event = {
        "event_id": "EVT-TEST-001",
        "timestamp": "2026-06-04T08:00:00Z",
        "subsystem": "COMMS",
        "event_type": "LINK_DOWN",
        "severity": "CRITICAL",
        "status": "NEW",
        "message": "Primary comms link lost",
        "source_host": "comms-node-01",
        "source_ip": "10.0.2.14",
    }

    is_valid, errors = validate_event(event)

    assert is_valid is True
    assert errors == []


def test_missing_required_field_fails_validation():
    event = {
        "event_id": "EVT-TEST-002",
        "timestamp": "2026-06-04T08:01:00Z",
        "subsystem": "NAV",
        "event_type": "GPS_DRIFT",
        "severity": "WARNING",
        "status": "NEW",
        "message": "",  # missing required value
        "source_host": "nav-core-01",
        "source_ip": "10.0.1.10",
    }

    is_valid, errors = validate_event(event)

    assert is_valid is False
    assert any("Missing required fields" in error for error in errors)


def test_invalid_severity_fails_validation():
    event = {
        "event_id": "EVT-TEST-003",
        "timestamp": "2026-06-04T08:02:00Z",
        "subsystem": "POWER",
        "event_type": "TEMP_HIGH",
        "severity": "SEVERE",  # invalid
        "status": "NEW",
        "message": "Temperature exceeded threshold",
        "source_host": "power-unit-01",
        "source_ip": "10.0.3.21",
    }

    is_valid, errors = validate_event(event)

    assert is_valid is False
    assert any("Invalid severity" in error for error in errors)