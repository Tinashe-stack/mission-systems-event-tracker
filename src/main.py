import csv
from pathlib import Path

from validate import validate_event
from rules import calculate_priority_score
from storage import get_connection, initialize_database, insert_event, fetch_top_open_events

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

            insert_event(conn, row)
            valid_count += 1

    conn.close()
    return valid_count, invalid_count


def print_top_open_events(limit: int = 5) -> None:
    conn = get_connection()
    rows = fetch_top_open_events(conn, limit=limit)

    print("\nTop open events:")
    print("-" * 100)

    if not rows:
        print("No events found.")
        conn.close()
        return

    for row in rows:
        print(
            f"{row['event_id']} | {row['timestamp']} | {row['subsystem']} | "
            f"{row['event_type']} | {row['severity']} | "
            f"priority={row['priority_score']} | status={row['status']}"
        )
        print(f"  message: {row['message']}")

    conn.close()


def main() -> None:
    if not DATA_FILE.exists():
        print(f"Data file not found: {DATA_FILE}")
        return

    valid_count, invalid_count = load_events_from_csv(DATA_FILE)

    print("\nLoad complete.")
    print(f"Valid events loaded: {valid_count}")
    print(f"Invalid events rejected: {invalid_count}")

    print_top_open_events(limit=5)


if __name__ == "__main__":
    main()