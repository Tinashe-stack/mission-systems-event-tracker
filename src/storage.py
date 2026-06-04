import sqlite3
from datetime import datetime, UTC
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
    conn.execute("""
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
        status_updated_at TEXT
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS event_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT NOT NULL,
        old_status TEXT,
        new_status TEXT NOT NULL,
        operator TEXT NOT NULL,
        changed_at TEXT NOT NULL,
        FOREIGN KEY (event_id) REFERENCES events(event_id)
    );
    """)

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
    operator: str,
) -> bool:
    current_row = conn.execute(
        "SELECT status FROM events WHERE event_id = ?",
        (event_id,),
    ).fetchone()

    if not current_row:
        return False

    old_status = current_row["status"]
    status_updated_at = datetime.now(UTC).isoformat()

    cursor = conn.execute(
        """
        UPDATE events
        SET status = ?, operator = ?, status_updated_at = ?
        WHERE event_id = ?
        """,
        (new_status, operator, status_updated_at, event_id),
    )
    conn.commit()

    if cursor.rowcount == 0:
        return False

    log_status_change(conn, event_id, old_status, new_status, operator)
    return True


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

def count_total_events(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT COUNT(*) AS count FROM events").fetchone()
    return row["count"] if row else 0

def count_events_by_status(conn: sqlite3.Connection):
    query = """
    SELECT status, COUNT(*) AS count
    FROM events
    GROUP BY status
    ORDER BY count DESC, status ASC;
    """
    return conn.execute(query).fetchall()

def count_events_by_severity(conn: sqlite3.Connection):
    query = """
    SELECT severity, COUNT(*) AS count
    FROM events
    GROUP BY severity
    ORDER BY count DESC, severity ASC;
    """
    return conn.execute(query).fetchall()

def count_events_by_subsystem(conn: sqlite3.Connection):
    query = """
    SELECT subsystem, COUNT(*) AS count
    FROM events
    GROUP BY subsystem
    ORDER BY count DESC, subsystem ASC;
    """
    return conn.execute(query).fetchall()

def log_status_change(
    conn: sqlite3.Connection,
    event_id: str,
    old_status: str | None,
    new_status: str,
    operator: str,
) -> None:
    changed_at = datetime.now(UTC).isoformat()

    conn.execute(
        """
        INSERT INTO event_status_history (event_id, old_status, new_status, operator, changed_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (event_id, old_status, new_status, operator, changed_at),
    )
    conn.commit()

def fetch_status_history(conn: sqlite3.Connection, event_id: str):
    query = """
    SELECT event_id, old_status, new_status, operator, changed_at
    FROM event_status_history
    WHERE event_id = ?
    ORDER BY changed_at ASC;
    """
    return conn.execute(query, (event_id,)).fetchall()
