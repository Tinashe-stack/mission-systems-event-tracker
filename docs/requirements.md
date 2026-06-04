# Mission Systems Event Tracker Requirements

## 1. Purpose

The Mission Systems Event Tracker is a Python-based application for ingesting, validating, storing, querying, updating, summarising, and exporting mission-style event data. The project is intended to demonstrate software engineering skills through a realistic operational monitoring workflow.

## 2. Scope

The system shall:

- Load structured event data from a CSV file.
- Validate incoming event records before storage.
- Assign or store a priority score for each event.
- Persist valid events in a SQLite database.
- Allow users to query and filter stored events.
- Allow users to update event status values.
- Maintain an audit history of status changes.
- Summarise the event set through aggregate reporting.
- Export filtered event data to CSV.

The system is a local command-line application and does not currently include multi-user authentication, network deployment, or a web interface.

## 3. Intended users

The intended users are:

- A developer or reviewer assessing the software engineering quality of the project.
- A technical user running the tool locally from the command line.
- A future analyst or operator who needs to inspect event records, update their status, and export filtered results.

## 4. Assumptions and constraints

- The system runs locally in Python 3.
- SQLite is used as the persistence layer.
- Input data is provided in CSV format.
- The current interface is command-line based.
- The project prioritises simplicity, traceability, and testability over production-scale deployment concerns.

## 5. Functional requirements

### FR-1 Load events from CSV

The system shall load event records from a CSV input file.

**Acceptance criteria:**
- A valid CSV file can be read from the expected location.
- Each input row is parsed into an event record.
- Valid rows are inserted into the database.
- Invalid rows are rejected without crashing the application.

### FR-2 Validate event records

The system shall validate required event fields before insertion.

**Acceptance criteria:**
- Required fields must be present.
- Severity values must be from the allowed set.
- Timestamps must be in a valid format.
- Invalid records must not be inserted.

### FR-3 Persist events in SQLite

The system shall store valid events in a SQLite database.

**Acceptance criteria:**
- Inserted events can be retrieved after loading.
- Stored fields match the inserted event data.
- The database schema is created automatically if it does not already exist.

### FR-4 Query and filter events

The system shall allow users to list events with optional filters.

**Acceptance criteria:**
- Users can filter by status.
- Users can filter by severity.
- Users can filter by subsystem.
- Users can limit the number of returned rows.

### FR-5 Update event status

The system shall allow users to update the status of an event.

**Acceptance criteria:**
- A valid event ID can be updated from the command line.
- Updated events reflect the new status.
- The operator making the change is stored.
- The update timestamp is stored.

### FR-6 Maintain status audit history

The system shall maintain a history of status changes for each event.

**Acceptance criteria:**
- Each status update creates a history record.
- A history record stores the old status, new status, operator, and timestamp.
- History entries can be retrieved for a given event ID.
- History entries are returned in chronological order.

### FR-7 Show summary reporting

The system shall provide a summary command for aggregate reporting.

**Acceptance criteria:**
- The summary includes total event count.
- The summary includes counts by status.
- The summary includes counts by severity.
- The summary includes counts by subsystem.
- The summary includes top open events.

### FR-8 Export filtered events to CSV

The system shall export filtered event data to CSV.

**Acceptance criteria:**
- Users can export filtered results to a chosen file path.
- Exported files contain a header row.
- Exported files contain only matching rows.
- Export failures are handled with a clear error message.

### FR-9 Inspect event history

The system shall provide a history command for a single event.

**Acceptance criteria:**
- Users can request history for an event ID.
- Existing history is printed in a readable format.
- If no history exists, the user receives a clear message.

## 6. Non-functional requirements

### NFR-1 Usability

The system should be easy to run locally by a reviewer or developer.

**Acceptance criteria:**
- Setup requires only Python and the listed dependencies.
- Commands are documented in the README.
- Command names are descriptive and consistent.

### NFR-2 Maintainability

The system should be structured for readability and extension.

**Acceptance criteria:**
- Validation, storage, rules, export, and CLI concerns are separated logically.
- Code is organised into modules rather than one large script.
- Project documentation explains the main design decisions.

### NFR-3 Testability

The system should support automated testing.

**Acceptance criteria:**
- Core logic is covered by pytest tests.
- New features are accompanied by tests.
- Tests can run locally without external services.

### NFR-4 Reliability

The system should fail safely when encountering invalid data or export errors.

**Acceptance criteria:**
- Invalid event rows do not crash the application.
- Missing query results are handled clearly.
- File export errors raise understandable exceptions or messages.

### NFR-5 Portability

The system should run on a typical developer machine with minimal setup.

**Acceptance criteria:**
- The application runs using Python 3 on local machines.
- No separate database server is required.
- The project can be cloned and run with documented steps.

## 7. Out of scope

The following are currently out of scope:

- Web deployment.
- Multi-user login and authentication.
- Real-time streaming ingestion from live systems.
- Distributed or cloud-based storage.
- Role-based permissions.
- Graphical dashboard interface, for now.

## 8. Success criteria

The project will be considered successful at the current stage if:

- A reviewer can clone the repository and run the application locally.
- Events can be loaded, queried, updated, summarised, and exported.
- Status history is preserved for updated events.
- Automated tests pass successfully.
- Documentation explains both usage and design choices.

## 9. Future enhancements

Potential future enhancements include:

- A lightweight dashboard layer.
- More detailed audit history for other field changes.
- Timestamped export filenames.
- Additional analytics views and charts.
- Migration to a more production-style database if needed.