# Mission Systems Event Tracker

Mission Systems Event Tracker is a Python-based software engineering project for ingesting, validating, storing, querying, updating, summarising, and exporting mission-style event data.

The project is designed to demonstrate core backend engineering skills through a realistic operational monitoring workflow using Python, SQLite, CSV ingestion, a command-line interface, and a Streamlit dashboard.

## Features

- Load structured event data from CSV.
- Validate incoming records before insertion.
- Calculate and store event priority scores.
- Persist data in a SQLite database.
- Query and filter stored events from the command line.
- Update event statuses and record operator actions.
- Maintain event status history for auditability.
- Summarise stored data through reporting views.
- Export filtered event data to CSV.
- Monitor events through a Streamlit dashboard with filters, charts, and status updates.

## Tech stack

- Python 3
- SQLite
- Pandas
- Streamlit
- Pytest

## Project structure

```text
mission-systems-event-tracker/
├── data/
│   └── sample_events.csv
├── docs/
│   └── requirements.md
├── src/
│   ├── dashboard.py
│   ├── main.py
│   ├── models.py
│   ├── rules.py
│   ├── storage.py
│   └── validate.py
├── tests/
├── requirements.txt
└── README.md
```

## Installation

Clone the repository and move into the project folder:

```bash
git clone https://github.com/Tinashe-stack/mission-systems-event-tracker.git
cd mission-systems-event-tracker
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

## Run the CLI

Load events from CSV:

```bash
python3 src/main.py load --file data/sample_events.csv
```

List events:

```bash
python3 src/main.py list
```

List events with filters:

```bash
python3 src/main.py list --status NEW
python3 src/main.py list --severity HIGH
python3 src/main.py list --subsystem NAV
```

Update an event status:

```bash
python3 src/main.py update-status EVT-1001 --status ACK --operator tinashe
```

## Run the dashboard

Start the Streamlit dashboard:

```bash
python3 -m streamlit run src/dashboard.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Dashboard capabilities

The dashboard includes:

- Sidebar filters for status, severity, and subsystem.
- Search across message, event type, and subsystem.
- Live summary metrics.
- Charts for status and severity distribution.
- Filtered event tables.
- Top open events view.
- Recent status history view.
- Event status update form.

## Data model

Each event record includes fields such as:

- `event_id`
- `timestamp`
- `subsystem`
- `event_type`
- `severity`
- `priority_score`
- `status`
- `message`
- `operator`
- `status_updated_at`

The project also stores status history in a separate audit table for tracking event lifecycle changes.

## Testing

Run tests with:

```bash
pytest
```

## Example workflow

1. Load sample event data into the database.
2. Use the CLI to inspect stored events.
3. Open the Streamlit dashboard.
4. Filter events by severity, status, or subsystem.
5. Update an event status from the dashboard.
6. Confirm the change appears in recent history.

## Current scope

This project currently focuses on:

- Local Python execution
- SQLite persistence
- CSV-based ingestion
- Command-line operations
- Lightweight dashboard monitoring

The following are currently out of scope:

- Authentication
- Multi-user access control
- Cloud deployment
- Real-time streaming ingestion
- Distributed database infrastructure

## Why this project exists

This project was built to demonstrate practical software engineering skills including:

- input validation
- modular Python design
- database interaction
- state updates and audit history
- testing and documentation
- lightweight application presentation through a dashboard

## Future enhancements

Possible future improvements include:

- richer dashboard visualisations
- inline dashboard editing beyond status changes
- advanced analytics views
- pagination for large result sets
- deployment as a hosted internal tool

## Author

Built as a portfolio project to demonstrate backend and application-layer software engineering skills.