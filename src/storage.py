import sqlite3
from pathlib import Path

DB_PATH = Path("mission_events.db")

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
    source_ip
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
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