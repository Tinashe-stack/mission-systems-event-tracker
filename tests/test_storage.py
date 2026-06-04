import sqlite3

from storage import (
    count_events_by_severity,
    count_events_by_status,
    count_events_by_subsystem,
    count_total_events,
    fetch_filtered_events,
    fetch_status_history,
    fetch_top_open_events,
    initialize_database,
    insert_event,
    update_event_status,
)

def make_event(
    event_id,
    subsystem="COMMS",
    event_type="LINK_DOWN",
    severity="CRITICAL",
    priority_score=100,
    status="NEW",
):
    return {
        "event_id": event_id,
        "timestamp": "2026-06-04T08:03:00Z",
        "subsystem": subsystem,
        "event_type": event_type,
        "severity": severity,
        "priority_score": priority_score,
        "status": status,
        "message": f"Test message for {event_id}",
        "source_host": "test-host",
        "source_ip": "10.0.0.1",
        "operator": None,
        "status_updated_at": None,
    }


def test_inserted_event_can_be_retrieved_from_database():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    initialize_database(conn)

    event = {
        "event_id": "EVT-TEST-004",
        "timestamp": "2026-06-04T08:03:00Z",
        "subsystem": "SENSOR",
        "event_type": "SENSOR_FAULT",
        "severity": "ERROR",
        "priority_score": 66,
        "status": "NEW",
        "message": "Sensor returned invalid values",
        "source_host": "sensor-hub-01",
        "source_ip": "10.0.4.31",
    }

    insert_event(conn, event)
    rows = fetch_top_open_events(conn, limit=10)

    assert len(rows) == 1
    assert rows[0]["event_id"] == "EVT-TEST-004"
    assert rows[0]["priority_score"] == 66
    assert rows[0]["status"] == "NEW"

    conn.close()
    
def test_count_total_events_returns_correct_number():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialize_database(conn)

    insert_event(conn, make_event("EVT-TEST-200"))
    insert_event(conn, make_event("EVT-TEST-201"))
    insert_event(conn, make_event("EVT-TEST-202"))

    total = count_total_events(conn)

    assert total == 3

    conn.close()


def test_count_events_by_status_returns_expected_counts():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialize_database(conn)

    insert_event(conn, make_event("EVT-TEST-203", status="NEW"))
    insert_event(conn, make_event("EVT-TEST-204", status="NEW"))
    insert_event(conn, make_event("EVT-TEST-205", status="ACK"))
    insert_event(conn, make_event("EVT-TEST-206", status="RESOLVED"))

    rows = count_events_by_status(conn)
    counts = {row["status"]: row["count"] for row in rows}

    assert counts["NEW"] == 2
    assert counts["ACK"] == 1
    assert counts["RESOLVED"] == 1

    conn.close()


def test_count_events_by_severity_returns_expected_counts():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialize_database(conn)

    insert_event(conn, make_event("EVT-TEST-207", severity="INFO", priority_score=10))
    insert_event(conn, make_event("EVT-TEST-208", severity="WARNING", priority_score=30))
    insert_event(conn, make_event("EVT-TEST-209", severity="WARNING", priority_score=30))
    insert_event(conn, make_event("EVT-TEST-210", severity="CRITICAL", priority_score=100))

    rows = count_events_by_severity(conn)
    counts = {row["severity"]: row["count"] for row in rows}

    assert counts["INFO"] == 1
    assert counts["WARNING"] == 2
    assert counts["CRITICAL"] == 1

    conn.close()


def test_count_events_by_subsystem_returns_expected_counts():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialize_database(conn)

    insert_event(conn, make_event("EVT-TEST-211", subsystem="COMMS"))
    insert_event(conn, make_event("EVT-TEST-212", subsystem="NAV"))
    insert_event(conn, make_event("EVT-TEST-213", subsystem="POWER"))
    insert_event(conn, make_event("EVT-TEST-214", subsystem="SENSOR"))
    insert_event(conn, make_event("EVT-TEST-215", subsystem="SENSOR"))

    rows = count_events_by_subsystem(conn)
    counts = {row["subsystem"]: row["count"] for row in rows}

    assert counts["COMMS"] == 1
    assert counts["NAV"] == 1
    assert counts["POWER"] == 1
    assert counts["SENSOR"] == 2

    conn.close()

def test_update_event_status_logs_history_entry():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialize_database(conn)

    insert_event(conn, make_event("EVT-TEST-500", status="NEW"))

    updated = update_event_status(conn, "EVT-TEST-500", "ACK", "tinashe")
    history_rows = fetch_status_history(conn, "EVT-TEST-500")

    assert updated is True
    assert len(history_rows) == 1
    assert history_rows[0]["event_id"] == "EVT-TEST-500"
    assert history_rows[0]["old_status"] == "NEW"
    assert history_rows[0]["new_status"] == "ACK"
    assert history_rows[0]["operator"] == "tinashe"

    conn.close()


def test_fetch_status_history_returns_rows_in_order():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialize_database(conn)

    insert_event(conn, make_event("EVT-TEST-501", status="NEW"))

    update_event_status(conn, "EVT-TEST-501", "ACK", "tinashe")
    update_event_status(conn, "EVT-TEST-501", "RESOLVED", "tinashe")

    history_rows = fetch_status_history(conn, "EVT-TEST-501")

    assert len(history_rows) == 2
    assert history_rows[0]["old_status"] == "NEW"
    assert history_rows[0]["new_status"] == "ACK"
    assert history_rows[1]["old_status"] == "ACK"
    assert history_rows[1]["new_status"] == "RESOLVED"

    conn.close()


def test_fetch_status_history_returns_empty_for_unknown_event():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialize_database(conn)

    history_rows = fetch_status_history(conn, "EVT-DOES-NOT-EXIST")

    assert history_rows == []

    conn.close()