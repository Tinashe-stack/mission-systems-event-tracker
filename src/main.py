import argparse
import csv
from pathlib import Path

from rules import calculate_priority_score
from storage import (
    fetch_filtered_events,
    fetch_top_open_events,
    get_connection,
    initialize_database,
    insert_event,
    update_event_status,
)
from validate import validate_event

DATA_FILE = Path("data/sample_events.csv")


def load_events_from_csv(file_path: Path) -> tuple[int, int]:
    valid_count = 0
    invalid_count = 0

    conn = get_connection()
    initialize_database(conn)

    with file_path.open(mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row_number, row in enumerate(reader, start=2):
            is_valid, errors = validate_event(row)

            if not is_valid:
                invalid_count += 1
                print(f"[ROW {row_number}] Invalid event: {'; '.join(errors)}")
                continue

            row["subsystem"] = row["subsystem"].strip().upper()
            row["severity"] = row["severity"].strip().upper()
            row["status"] = row["status"].strip().upper()
            row["event_type"] = row["event_type"].strip().upper()
            row["priority_score"] = calculate_priority_score(row)
            row["operator"] = None
            row["status_updated_at"] = None

            insert_event(conn, row)
            valid_count += 1

    conn.close()
    return valid_count, invalid_count


def print_events(rows) -> None:
    print("-" * 100)

    if not rows:
        print("No events found.")
        return

    for row in rows:
        print(
            f"{row['event_id']} | {row['timestamp']} | {row['subsystem']} | "
            f"{row['event_type']} | {row['severity']} | "
            f"priority={row['priority_score']} | status={row['status']}"
        )
        print(f"  message: {row['message']}")


def handle_load(args) -> None:
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"Data file not found: {file_path}")
        return

    valid_count, invalid_count = load_events_from_csv(file_path)

    print("\nLoad complete.")
    print(f"Valid events loaded: {valid_count}")
    print(f"Invalid events rejected: {invalid_count}")

    conn = get_connection()
    rows = fetch_top_open_events(conn, limit=5)
    print("\nTop open events:")
    print_events(rows)
    conn.close()


def handle_list(args) -> None:
    conn = get_connection()
    initialize_database(conn)

    rows = fetch_filtered_events(
        conn,
        subsystem=args.subsystem,
        severity=args.severity,
        status=args.status,
        limit=args.limit,
    )

    print("\nFiltered events:")
    print_events(rows)
    conn.close()


def handle_update_status(args) -> None:
    conn = get_connection()
    initialize_database(conn)

    updated_rows = update_event_status(
        conn,
        event_id=args.event_id,
        new_status=args.status,
        operator=args.operator,
    )

    if updated_rows == 0:
        print(f"No event found with event_id={args.event_id}")
    else:
        print(f"Updated {args.event_id} to status={args.status.upper()}")

    conn.close()


def build_parser():
    parser = argparse.ArgumentParser(description="Mission Systems Event Tracker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    load_parser = subparsers.add_parser("load", help="Load events from a CSV file")
    load_parser.add_argument(
        "--file",
        default=str(DATA_FILE),
        help="Path to CSV file (default: data/sample_events.csv)",
    )
    load_parser.set_defaults(func=handle_load)

    list_parser = subparsers.add_parser("list", help="List events with optional filters")
    list_parser.add_argument("--subsystem", help="Filter by subsystem")
    list_parser.add_argument("--severity", help="Filter by severity")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--limit", type=int, default=10, help="Max rows to return")
    list_parser.set_defaults(func=handle_list)

    update_parser = subparsers.add_parser("update-status", help="Update event status")
    update_parser.add_argument("event_id", help="Event ID to update")
    update_parser.add_argument(
        "--status",
        required=True,
        choices=["NEW", "ACK", "RESOLVED"],
        help="New status value",
    )
    update_parser.add_argument("--operator", help="Operator name or ID")
    update_parser.set_defaults(func=handle_update_status)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()