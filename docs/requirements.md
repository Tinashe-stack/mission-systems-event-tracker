# Mission Systems Event Tracker Requirements

## Overview

The Mission Systems Event Tracker is a Python application that ingests structured event records, validates them, assigns a priority score, stores valid events in a SQLite database, and presents the highest-priority unresolved events to the operator.

The purpose of the project is to simulate a mission-style monitoring workflow while demonstrating requirements-driven software development, modular design, data validation, scoring logic, persistence, and automated testing.

## Objectives

- Ingest structured event data from a CSV source.
- Validate incoming records against required fields and allowed values.
- Calculate a priority score so that more critical events appear first.
- Store valid events in a SQLite database.
- Retrieve unresolved events ordered by priority.
- Provide a simple, reproducible Python project with automated tests.

## User role

### Operator

The operator is the main user of the system.

The operator needs to:
- Load event data into the tracker.
- Identify which events are most urgent.
- Review unresolved events.
- Trust that invalid data is rejected rather than silently stored.

## User stories

- As an operator, I want to load event data from a CSV file so that I can populate the tracker with historical or simulated events.
- As an operator, I want invalid events to be rejected so that the stored data remains reliable.
- As an operator, I want events to receive a priority score so that I can focus on the most urgent issues first.
- As an operator, I want valid events stored in a database so that I can query them efficiently.
- As an operator, I want to view the highest-priority unresolved events so that I can respond quickly.
- As a developer, I want automated tests for validation, scoring, and storage so that I can change the code more safely.

## Functional requirements

### FR1 — CSV ingestion
The system shall read event records from a CSV file.

### FR2 — Validation
The system shall validate each event before storage.  
Validation shall check:
- Required fields are present.
- Severity is one of the allowed values.
- Status is one of the allowed values.
- Subsystem is one of the allowed values.
- Timestamp is parseable.
- IP address is valid if provided.

### FR3 — Priority scoring
The system shall assign a numeric `priority_score` to each valid event.  
The score shall be based on:
- Severity.
- Event type adjustment rules.

### FR4 — Persistence
The system shall store valid events in a SQLite database.  
Each event shall have a unique `event_id`.

### FR5 — Querying
The system shall retrieve unresolved events ordered by highest priority first.

### FR6 — Error reporting
The system shall report invalid rows during ingestion with clear error messages.

### FR7 — Automated tests
The system shall include automated tests for:
- Validation rules.
- Priority scoring.
- Database insertion and retrieval.

## Non-functional requirements

### NFR1 — Reliability
The system shall reject invalid data rather than crashing or storing malformed records.

### NFR2 — Maintainability
The codebase shall be split into focused modules such as validation, rules, storage, and application entry logic.

### NFR3 — Testability
The project shall use `pytest` so tests can be executed with a single command.

### NFR4 — Reproducibility
The project shall include a `requirements.txt` file and setup instructions in the README so another user can run it easily.

### NFR5 — Simplicity
The first version shall prioritise a working command-line pipeline over a graphical interface.

## Event data schema

Each event record shall contain the following fields:

| Field | Description |
|------|-------------|
| `event_id` | Unique identifier for the event |
| `timestamp` | ISO-format timestamp of when the event occurred |
| `subsystem` | Source subsystem, such as NAV, COMMS, POWER, or SENSOR |
| `event_type` | Type of event, such as LINK_DOWN or HEARTBEAT |
| `severity` | Severity level: INFO, WARNING, ERROR, or CRITICAL |
| `status` | Current state of the event, such as NEW, ACK, or RESOLVED |
| `message` | Human-readable description of the event |
| `source_host` | Host or system that produced the event |
| `source_ip` | Optional IP address associated with the event |
| `priority_score` | Calculated urgency score |

## Current scope

The current version includes:
- CSV ingestion.
- Validation.
- Priority scoring.
- SQLite persistence.
- Querying top unresolved events.
- Initial automated tests.

## Out of scope for current version

The following items are intentionally excluded from the first version:
- Authentication and user accounts.
- Real-time streaming ingestion.
- Network APIs.
- Dashboard user interface.
- Advanced analytics or alert routing.

## Acceptance criteria

The first working version is complete when:
- The application reads `sample_events.csv`.
- Valid events are inserted into SQLite.
- Invalid events are rejected with clear messages.
- Events receive a priority score.
- The application prints the top unresolved events in priority order.
- The automated test suite passes successfully.