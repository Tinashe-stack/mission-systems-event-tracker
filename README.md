# Mission Systems Event Tracker

A Python-based event tracking application that simulates a mission-style monitoring system. The project ingests structured event data from CSV, validates each event, assigns a priority score, stores valid events in SQLite, and returns the highest-priority unresolved events.

This project was built to practise requirements-driven software development, modular Python design, validation, scoring logic, database persistence, and automated testing.

## Features

- Load structured event data from a CSV file.
- Validate required fields, timestamps, subsystem values, severity values, and IP addresses.
- Calculate a `priority_score` based on severity and event type.
- Store valid events in a SQLite database.
- Query and display the highest-priority unresolved events.
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

The application reads synthetic mission-system events from `data/sample_events.csv`. Each row is validated, scored, and inserted into a SQLite database if valid. After loading the data, the program prints the top unresolved events ordered by priority.

## Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the application

From the project root:

```bash
python src/main.py
```

Example output:

```text
Load complete.
Valid events loaded: 24
Invalid events rejected: 0

Top open events:
EVT-0023 | 2026-06-04T08:22:50Z | POWER | FAILOVER_TRIGGERED | CRITICAL | priority=100 | status=NEW
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

## Why this project

This project is designed to demonstrate software engineering skills that go beyond simple scripting, including:

- Structured project organisation.
- Data validation and defensive programming.
- Business-rule implementation.
- Database integration.
- Automated testing.
- Clear, reproducible setup.

## Next steps

Planned improvements include:

- Add invalid sample events to test rejection paths visibly.
- Add more query functions such as filtering by subsystem or severity.
- Add status update commands such as ACK and RESOLVED.
- Add summary statistics for open vs resolved events.
- Add a lightweight dashboard or CLI subcommands.