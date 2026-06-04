import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "mission_events.db"

CREATE_EVENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    subsystem TEXT NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    priority_score INTEGER NOT NULL,
    status TEXT NOT NULL,
    message TEXT NOT NULL,
    source_host TEXT,
    source_ip TEXT,
    operator TEXT,
    status_updated_at TEXT,
    ingested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

INSERT_EVENT_SQL = """
INSERT OR REPLACE INTO events (
    event_id,
    timestamp,
    subsystem,
    event_type,
    severity,
    priority_score,
    status,
    message,
    source_host,
    source_ip,
    operator,
    status_updated_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
"""

def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database(conn: sqlite3.Connection) -> None:
    conn.execute(CREATE_EVENTS_TABLE_SQL)
    conn.commit()

def insert_event(conn: sqlite3.Connection, event: dict) -> None:
    conn.execute(
        INSERT_EVENT_SQL,
        (
            event["event_id"],
            event["timestamp"],
            event["subsystem"],
            event["event_type"],
            event["severity"],
            event["priority_score"],
            event["status"],
            event["message"],
            event.get("source_host"),
            event.get("source_ip"),
            event.get("operator"),
            event.get("status_updated_at"),
        ),
    )
    conn.commit()

def fetch_top_open_events(conn: sqlite3.Connection, limit: int = 5):
    query = """
    SELECT *
    FROM events
    WHERE status != 'RESOLVED'
    ORDER BY priority_score DESC, timestamp DESC
    LIMIT ?;
    """
    return conn.execute(query, (limit,)).fetchall()

def fetch_filtered_events(
    conn: sqlite3.Connection,
    subsystem: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    limit: int = 10,
):
    query = """
    SELECT *
    FROM events
    WHERE 1=1
    """
    params = []

    if subsystem:
        query += " AND subsystem = ?"
        params.append(subsystem.upper())

    if severity:
        query += " AND severity = ?"
        params.append(severity.upper())

    if status:
        query += " AND status = ?"
        params.append(status.upper())

    query += " ORDER BY priority_score DESC, timestamp DESC LIMIT ?"
    params.append(limit)

    return conn.execute(query, params).fetchall()

def update_event_status(
    conn: sqlite3.Connection,
    event_id: str,
    new_status: str,
    operator: str | None = None,
) -> int:
    query = """
    UPDATE events
    SET status = ?,
        operator = ?,
        status_updated_at = CURRENT_TIMESTAMP
    WHERE event_id = ?;
    """
    cursor = conn.execute(query, (new_status.upper(), operator, event_id))
    conn.commit()
    return cursor.rowcount

from storage import (
    initialize_database,
    insert_event,
    fetch_top_open_events,
    fetch_filtered_events,
    update_event_status,
)
import sqlite3


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


def test_update_event_status_changes_stored_status():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialize_database(conn)

    insert_event(conn, make_event("EVT-TEST-100", status="NEW"))
    updated_rows = update_event_status(conn, "EVT-TEST-100", "ACK", operator="tinashe")

    rows = fetch_filtered_events(conn, status="ACK", limit=10)

    assert updated_rows == 1
    assert len(rows) == 1
    assert rows[0]["event_id"] == "EVT-TEST-100"
    assert rows[0]["status"] == "ACK"
    assert rows[0]["operator"] == "tinashe"

    conn.close()


def test_filter_by_status_returns_only_matching_rows():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialize_database(conn)

    insert_event(conn, make_event("EVT-TEST-101", status="NEW"))
    insert_event(conn, make_event("EVT-TEST-102", status="ACK"))

    rows = fetch_filtered_events(conn, status="ACK", limit=10)

    assert len(rows) == 1
    assert rows[0]["event_id"] == "EVT-TEST-102"
    assert rows[0]["status"] == "ACK"

    conn.close()


def test_filter_by_subsystem_returns_only_matching_rows():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialize_database(conn)

    insert_event(conn, make_event("EVT-TEST-103", subsystem="COMMS"))
    insert_event(conn, make_event("EVT-TEST-104", subsystem="NAV"))

    rows = fetch_filtered_events(conn, subsystem="NAV", limit=10)

    assert len(rows) == 1
    assert rows[0]["event_id"] == "EVT-TEST-104"
    assert rows[0]["subsystem"] == "NAV"

    conn.close()


def test_resolved_events_do_not_appear_in_top_open_events():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    initialize_database(conn)

    insert_event(conn, make_event("EVT-TEST-105", status="NEW", priority_score=90))
    insert_event(conn, make_event("EVT-TEST-106", status="RESOLVED", priority_score=100))

    rows = fetch_top_open_events(conn, limit=10)

    event_ids = [row["event_id"] for row in rows]

    assert "EVT-TEST-105" in event_ids
    assert "EVT-TEST-106" not in event_ids

    conn.close()