import sqlite3
import pandas as pd
import streamlit as st

from storage import get_connection, initialize_database, update_event_status

st.set_page_config(page_title="Mission Systems Event Tracker", layout="wide")


def load_dataframe(query: str, params: tuple = ()) -> pd.DataFrame:
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    initialize_database(conn)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return pd.DataFrame([dict(row) for row in rows])


def get_events_df() -> pd.DataFrame:
    df = load_dataframe("""
        SELECT event_id, timestamp, subsystem, event_type, severity,
               priority_score, status, message, operator, status_updated_at
        FROM events
        ORDER BY timestamp DESC
    """)
    if df.empty:
        return pd.DataFrame(
            columns=[
                "event_id", "timestamp", "subsystem", "event_type",
                "severity", "priority_score", "status", "message",
                "operator", "status_updated_at"
            ]
        )
    return df


def get_history_df() -> pd.DataFrame:
    df = load_dataframe("""
        SELECT event_id, old_status, new_status, operator, changed_at
        FROM event_status_history
        ORDER BY changed_at DESC
    """)
    if df.empty:
        return pd.DataFrame(
            columns=["event_id", "old_status", "new_status", "operator", "changed_at"]
        )
    return df


def apply_filters(
    df: pd.DataFrame,
    statuses: list[str],
    severities: list[str],
    subsystems: list[str],
    search_text: str,
) -> pd.DataFrame:
    filtered = df.copy()

    if statuses:
        filtered = filtered[filtered["status"].isin(statuses)]

    if severities:
        filtered = filtered[filtered["severity"].isin(severities)]

    if subsystems:
        filtered = filtered[filtered["subsystem"].isin(subsystems)]

    if search_text.strip():
        term = search_text.strip().lower()
        filtered = filtered[
            filtered["message"].fillna("").str.lower().str.contains(term) |
            filtered["event_type"].fillna("").str.lower().str.contains(term) |
            filtered["subsystem"].fillna("").str.lower().str.contains(term)
        ]

    return filtered


def render_metrics(df: pd.DataFrame) -> None:
    total_events = len(df)
    open_events = 0 if df.empty else int((df["status"] != "RESOLVED").sum())
    resolved_events = 0 if df.empty else int((df["status"] == "RESOLVED").sum())
    high_priority_open = (
        0 if df.empty else int(((df["priority_score"] >= 80) & (df["status"] != "RESOLVED")).sum())
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total events", total_events)
    col2.metric("Open events", open_events)
    col3.metric("Resolved events", resolved_events)
    col4.metric("High priority open", high_priority_open)


def render_chart_section(df: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Events by status")
        if df.empty:
            st.info("No events match the selected filters.")
        else:
            status_counts = (
                df.groupby("status")
                .size()
                .reset_index(name="count")
                .set_index("status")
            )
            st.bar_chart(status_counts, width="stretch")

    with col2:
        st.subheader("Events by severity")
        if df.empty:
            st.info("No events match the selected filters.")
        else:
            severity_counts = (
                df.groupby("severity")
                .size()
                .reset_index(name="count")
                .set_index("severity")
            )
            st.bar_chart(severity_counts, width="stretch")


def render_distribution_tables(df: pd.DataFrame) -> None:
    status_df = (
        df.groupby("status")
        .size()
        .reset_index(name="count")
        .sort_values(["count", "status"], ascending=[False, True])
        if not df.empty else pd.DataFrame(columns=["status", "count"])
    )

    severity_df = (
        df.groupby("severity")
        .size()
        .reset_index(name="count")
        .sort_values(["count", "severity"], ascending=[False, True])
        if not df.empty else pd.DataFrame(columns=["severity", "count"])
    )

    subsystem_df = (
        df.groupby("subsystem")
        .size()
        .reset_index(name="count")
        .sort_values(["count", "subsystem"], ascending=[False, True])
        if not df.empty else pd.DataFrame(columns=["subsystem", "count"])
    )

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.subheader("By status")
        st.dataframe(status_df, width="stretch", hide_index=True)

    with col_b:
        st.subheader("By severity")
        st.dataframe(severity_df, width="stretch", hide_index=True)

    with col_c:
        st.subheader("By subsystem")
        st.dataframe(subsystem_df, width="stretch", hide_index=True)


def render_top_events(df: pd.DataFrame) -> None:
    st.subheader("Top filtered open events")

    if df.empty:
        st.info("No events match the selected filters.")
        return

    top_open_df = (
        df[df["status"] != "RESOLVED"]
        .sort_values(["priority_score", "timestamp"], ascending=[False, False])
        .head(10)
    )

    if top_open_df.empty:
        st.info("There are no open events in the current selection.")
    else:
        st.dataframe(top_open_df, width="stretch", hide_index=True)


def render_history(history_df: pd.DataFrame, selected_event_ids: list) -> None:
    st.subheader("Recent status history")

    filtered_history = history_df.copy()
    if selected_event_ids:
        filtered_history = filtered_history[filtered_history["event_id"].isin(selected_event_ids)]

    filtered_history = filtered_history.head(10)

    if filtered_history.empty:
        st.info("No matching history records found.")
    else:
        st.dataframe(filtered_history, width="stretch", hide_index=True)

def render_status_update_panel(df: pd.DataFrame) -> None:
    st.subheader("Update event status")

    if df.empty:
        st.info("No events available for update in the current filter selection.")
        return

    open_for_update = df.sort_values(["priority_score", "timestamp"], ascending=[False, False])

    event_options = open_for_update["event_id"].tolist()
    selected_event_id = st.selectbox("Select event", options=event_options)

    selected_row = open_for_update[open_for_update["event_id"] == selected_event_id].iloc[0]

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Subsystem:** {selected_row['subsystem']}")
        st.write(f"**Type:** {selected_row['event_type']}")
        st.write(f"**Severity:** {selected_row['severity']}")
    with col2:
        st.write(f"**Current status:** {selected_row['status']}")
        st.write(f"**Priority score:** {selected_row['priority_score']}")
        st.write(f"**Timestamp:** {selected_row['timestamp']}")

    with st.form("update_status_form"):
        new_status = st.selectbox("New status", options=["NEW", "ACK", "RESOLVED"])
        operator = st.text_input("Operator", placeholder="e.g. tinashe")
        submitted = st.form_submit_button("Apply status update")

        if submitted:
            if not operator.strip():
                st.error("Operator is required.")
            elif new_status == selected_row["status"]:
                st.warning("Selected status is the same as the current status.")
            else:
                conn = get_connection()
                initialize_database(conn)

                updated_rows = update_event_status(
                    conn,
                    event_id=selected_event_id,
                    new_status=new_status,
                    operator=operator.strip()
                )
                conn.close()

                if updated_rows == 0:
                    st.error("No event was updated.")
                else:
                    st.success(f"Updated {selected_event_id} to {new_status}.")
                    st.rerun()


def main() -> None:
    st.title("Mission Systems Event Tracker Dashboard")
    st.caption("Interactive monitoring view for mission-style event data stored in SQLite.")

    events_df = get_events_df()
    history_df = get_history_df()

    st.sidebar.header("Filters")

    if st.sidebar.button("Refresh data"):
        st.rerun()

    status_options = sorted(events_df["status"].dropna().unique().tolist()) if not events_df.empty else []
    severity_options = sorted(events_df["severity"].dropna().unique().tolist()) if not events_df.empty else []
    subsystem_options = sorted(events_df["subsystem"].dropna().unique().tolist()) if not events_df.empty else []

    selected_statuses = st.sidebar.multiselect(
        "Status",
        options=status_options,
        default=status_options
    )

    selected_severities = st.sidebar.multiselect(
        "Severity",
        options=severity_options,
        default=severity_options
    )

    selected_subsystems = st.sidebar.multiselect(
        "Subsystem",
        options=subsystem_options,
        default=subsystem_options
    )

    search_text = st.sidebar.text_input("Search message, type, or subsystem")

    filtered_events = apply_filters(
        events_df,
        selected_statuses,
        selected_severities,
        selected_subsystems,
        search_text,
    )

    selected_event_ids = [] if filtered_events.empty else filtered_events["event_id"].tolist()

    render_metrics(filtered_events)
    st.divider()

    render_chart_section(filtered_events)
    st.divider()

    render_distribution_tables(filtered_events)
    st.divider()

    st.subheader("Filtered events")
    if filtered_events.empty:
        st.info("No events match the current filters.")
    else:
        st.dataframe(filtered_events, width="stretch", hide_index=True)

    st.divider()
    render_top_events(filtered_events)
    st.divider()
    render_status_update_panel(filtered_events)
    st.divider()
    render_history(history_df, selected_event_ids)
    
       
if __name__ == "__main__":
    main()