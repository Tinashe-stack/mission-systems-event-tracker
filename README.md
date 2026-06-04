# Mission Systems Event Tracker

A Python-based event tracking application that simulates a mission-style monitoring workflow. The system ingests structured event data from CSV, validates each event, assigns a priority score, stores valid events in SQLite, and supports filtering, status updates, and summary reporting.

This project was built to practise modular Python development, requirements-driven design, validation logic, database persistence, command-line workflows, and automated testing.

## Features

- Load structured event data from a CSV file.
- Validate required fields, timestamps, subsystem values, severity values, and IP addresses.
- Calculate a `priority_score` based on severity and event type.
- Store valid events in a SQLite database.
- Filter events by subsystem, severity, and status.
- Update event status to `NEW`, `ACK`, or `RESOLVED`.
- Record the operator associated with a status change.
- Display summary statistics for the current event set.
- Run automated tests with `pytest`.

## Project structure

```text
mission-systems-event-tracker/
├── data/
│   └── sample_events.csv
├── docs/
│   └── requirements.md
├── src/
│   ├── main.py
│   ├── models.py
│   ├── rules.py
│   ├── storage.py
│   └── validate.py
├── tests/
│   ├── conftest.py
│   ├── test_rules.py
│   ├── test_storage.py
│   └── test_validate.py
├── .gitignore
├── README.md
└── requirements.txt
```

## How it works

The application reads synthetic mission-system events from `data/sample_events.csv`. Each row is validated, scored, and inserted into a SQLite database if valid. Once loaded, the event set can be queried with filters, updated by status, and summarised through the command line.

## Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the application

Load events from the sample CSV:

```bash
python src/main.py load
```

List events with optional filters:

```bash
python src/main.py list --status NEW
python src/main.py list --subsystem COMMS --severity CRITICAL
python src/main.py list --status ACK --limit 5
```

Update an event status:

```bash
python src/main.py update-status EVT-0005 --status ACK --operator tinashe
python src/main.py update-status EVT-0005 --status RESOLVED --operator tinashe
```

Show a summary report:

```bash
python src/main.py summary
```

## Example summary output

```text
Event summary:
----------------------------------------------------------------------------------------------------
Total events: 24

By status:
  NEW: 23
  ACK: 1

By severity:
  INFO: 7
  WARNING: 7
  ERROR: 6
  CRITICAL: 4

By subsystem:
  COMMS: 6
  NAV: 6
  POWER: 6
  SENSOR: 6
```

## Run tests

```bash
pytest
```

## Current test coverage

The project currently includes tests for:

- Valid event validation.
- Missing required field validation.
- Invalid severity validation.
- Priority scoring logic.
- SQLite insert and retrieval.
- Filtering by status and subsystem.
- Status updates.
- Excluding resolved events from top open events.
- Summary count queries.

## Why this project

This project is designed to demonstrate software engineering skills that go beyond simple scripting, including:

- Structured project organisation.
- Data validation and defensive programming.
- Business-rule implementation.
- Database integration.
- Command-line interface design.
- Automated testing.
- Clear, reproducible setup.

## Next steps

Planned improvements include:

- Export filtered results to CSV.
- Add more advanced audit history for status changes.
- Add a lightweight dashboard for event monitoring.
- Add more test coverage for CLI output and edge cases.