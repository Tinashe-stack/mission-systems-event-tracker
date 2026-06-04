from storage import initialize_database, insert_event, fetch_top_open_events
import sqlite3


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