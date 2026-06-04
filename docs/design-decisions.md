# Design Decisions

This document records the main technical decisions made during development of the Mission Systems Event Tracker. It focuses on why each decision was made, the alternatives that were considered, and the consequences for the project.

## Decision 1: Use SQLite for persistence

**Status:** Accepted  
**Context:** The project needed persistent storage for events, status updates, summaries, and exports, but it also needed to stay simple to run locally for a portfolio reviewer.

**Decision:** Use SQLite as the primary database for the project.

**Why this was chosen:**
- SQLite is included with Python’s standard library through `sqlite3`.
- It requires no separate database server setup.
- It supports realistic relational queries for filtering, summaries, and audit history.
- It keeps the project easy to clone and run for recruiters or hiring managers.

**Alternatives considered:**
- In-memory Python data structures; easier at first, but not realistic for persistence or querying.
- PostgreSQL; more production-like, but adds setup complexity that is unnecessary for this project stage.

**Consequences:**
- The project is easy to run locally and easy to test.
- SQL queries can be demonstrated directly in the storage layer.
- The design can later be migrated to PostgreSQL if a more production-style deployment is needed.

## Decision 2: Separate validation, rules, storage, and CLI logic

**Status:** Accepted  
**Context:** A single-file script would be faster to start, but it would become harder to test, maintain, and explain as features were added.

**Decision:** Split the application into focused modules for validation, business rules, storage, and command-line orchestration.

**Why this was chosen:**
- Improves readability and maintainability.
- Makes unit testing easier.
- Allows business logic to be changed without rewriting database or CLI code.
- Demonstrates cleaner software engineering structure for portfolio purposes.

**Alternatives considered:**
- Keeping all logic in `main.py`; simpler initially, but harder to scale and explain.

**Consequences:**
- The codebase is easier to navigate.
- Tests can target individual modules directly.
- The project better demonstrates engineering discipline rather than just scripting ability.

## Decision 3: Store current event state in `events` and history in `event_status_history`

**Status:** Accepted  
**Context:** The system needed to show both the current status of an event and the history of status transitions over time.

**Decision:** Keep the latest event state in the `events` table and record status changes in a separate `event_status_history` table.

**Why this was chosen:**
- The `events` table stays simple and efficient for current-state queries.
- The history table preserves traceability for operator actions.
- This mirrors a realistic audit-trail pattern used in operational systems.

**Alternatives considered:**
- Store only the latest status in the main table; simpler, but loses auditability.
- Duplicate the full event row on every change; preserves history, but adds unnecessary redundancy for this project.

**Consequences:**
- The project now supports audit-history queries.
- Status changes are traceable by operator and timestamp.
- The database design is slightly more complex, but much more realistic.

## Decision 4: Build a CLI before building a dashboard

**Status:** Accepted  
**Context:** The project needed a usable interface, but the first priority was proving the application logic and data flow.

**Decision:** Start with a command-line interface for loading, listing, updating, summarising, and exporting events.

**Why this was chosen:**
- Faster to implement and test.
- Keeps focus on core functionality first.
- Makes feature development incremental and verifiable.
- Provides a strong engineering foundation before adding visual polish.

**Alternatives considered:**
- Build a dashboard first; better visually, but risks hiding weak backend structure behind UI work.

**Consequences:**
- Core functionality was completed earlier.
- Commands are easy to demonstrate in the terminal.
- A dashboard can still be added later without replacing the core logic.

## Decision 5: Export filtered results to CSV

**Status:** Accepted  
**Context:** Users may need to take filtered event data into other tools for reporting or further analysis.

**Decision:** Add an export command that writes filtered results to CSV.

**Why this was chosen:**
- CSV is simple, portable, and widely supported.
- Exporting filtered records makes the tool more realistic.
- It connects the software engineering workflow to analysis and reporting use cases.

**Alternatives considered:**
- JSON export; useful for systems integration, but less immediately readable for manual review.
- No export support; simpler, but less practical.

**Consequences:**
- The tool is more useful for downstream workflows.
- Export logic required additional testing and error handling.
- The project now demonstrates both application logic and data portability.

## Decision 6: Add automated tests as features are introduced

**Status:** Accepted  
**Context:** As the project grew, manual testing alone became too fragile and time-consuming.

**Decision:** Add pytest-based tests for validation, rules, storage, summaries, export, and audit history.

**Why this was chosen:**
- Protects against regressions.
- Makes refactoring safer.
- Demonstrates professional development habits.
- Gives confidence that features behave correctly.

**Alternatives considered:**
- Manual testing only; faster at the start, but unreliable as the project expands.

**Consequences:**
- The project is easier to extend safely.
- Bugs are caught earlier.
- The repository provides clearer evidence of engineering quality.