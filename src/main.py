import argparse
import csv
from pathlib import Path

from rules import calculate_priority_score

from storage import (
    count_events_by_status,
    count_events_by_severity,
    count_events_by_subsystem,
    count_total_events,
    fetch_filtered_events,
    fetch_top_open_events,
    get_connection,
    initialize_database,
    insert_event,
    update_event_status,
)
from validate import validate_event

DATA_FILE = Path("data/sample_events.csv")

EXPORTS_DIR = Path("exports")


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
    
def handle_summary(args) -> None:
    conn = get_connection()
    initialize_database(conn)

    total_events = count_total_events(conn)
    by_status = count_events_by_status(conn)
    by_severity = count_events_by_severity(conn)
    by_subsystem = count_events_by_subsystem(conn)
    top_open = fetch_top_open_events(conn, limit=3)

    print("\nEvent summary:")
    print("-" * 100)
    print(f"Total events: {total_events}")

    print("\nBy status:")
    for row in by_status:
        print(f"  {row['status']}: {row['count']}")

    print("\nBy severity:")
    for row in by_severity:
        print(f"  {row['severity']}: {row['count']}")

    print("\nBy subsystem:")
    for row in by_subsystem:
        print(f"  {row['subsystem']}: {row['count']}")

    print("\nTop open events:")
    print_events(top_open)

    conn.close()

def export_rows_to_csv(rows, output_path: Path) -> int:
    if not rows:
        return 0

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = list(rows[0].keys())

        with output_path.open(mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows([dict(row) for row in rows])

        return len(rows)

    except OSError as exc:
        raise RuntimeError(f"Failed to export CSV to {output_path}: {exc}") from exc


def handle_export(args) -> None:
    conn = get_connection()
    initialize_database(conn)

    rows = fetch_filtered_events(
        conn,
        subsystem=args.subsystem,
        severity=args.severity,
        status=args.status,
        limit=args.limit,
    )

    output_path = Path(args.output) if args.output else EXPORTS_DIR / "filtered_events.csv"
    exported_count = export_rows_to_csv(rows, output_path)

    if exported_count == 0:
        print("No events found for export.")
    else:
        print(f"Exported {exported_count} events to {output_path}")

    conn.close()
    conn = get_connection()
    initialize_database(conn)

    rows = fetch_filtered_events(
        conn,
        subsystem=args.subsystem,
        severity=args.severity,
        status=args.status,
        limit=args.limit,
    )

    if not rows:
        print("No events found for export.")
        conn.close()
        return

    EXPORTS_DIR.mkdir(exist_ok=True)

    output_path = Path(args.output) if args.output else EXPORTS_DIR / "filtered_events.csv"

    fieldnames = list(rows[0].keys())

    with output_path.open(mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([dict(row) for row in rows])

    print(f"Exported {len(rows)} events to {output_path}")
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
    
    summary_parser = subparsers.add_parser("summary", help="Show event summary report")
    summary_parser.set_defaults(func=handle_summary)
    
    export_parser = subparsers.add_parser("export", help="Export filtered events to CSV")
    export_parser.add_argument("--subsystem", help="Filter by subsystem")
    export_parser.add_argument("--severity", help="Filter by severity")
    export_parser.add_argument("--status", help="Filter by status")
    export_parser.add_argument("--limit", type=int, default=100, help="Max rows to export")
    export_parser.add_argument("--output", help="Output CSV file path")
    export_parser.set_defaults(func=handle_export)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()