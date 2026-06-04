import csv

from main import export_rows_to_csv


def make_export_row(
    event_id="EVT-TEST-400",
    subsystem="COMMS",
    event_type="LINK_DOWN",
    severity="CRITICAL",
    priority_score=100,
    status="ACK",
):
    return {
        "event_id": event_id,
        "timestamp": "2026-06-04T08:03:00Z",
        "subsystem": subsystem,
        "event_type": event_type,
        "severity": severity,
        "priority_score": priority_score,
        "status": status,
        "message": f"Test message for {event_id}",
        "source_host": "test-host",
        "source_ip": "10.0.0.1",
        "operator": "tinashe",
        "status_updated_at": "2026-06-04 19:40:00",
    }


def test_export_rows_to_csv_creates_file(tmp_path):
    rows = [make_export_row()]
    output_file = tmp_path / "exports" / "ack_events.csv"

    exported_count = export_rows_to_csv(rows, output_file)

    assert exported_count == 1
    assert output_file.exists()


def test_export_rows_to_csv_writes_expected_header_and_row(tmp_path):
    rows = [make_export_row(event_id="EVT-TEST-401", subsystem="NAV", status="ACK")]
    output_file = tmp_path / "exports" / "ack_events.csv"

    export_rows_to_csv(rows, output_file)

    with output_file.open(mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        loaded_rows = list(reader)

    assert "event_id" in reader.fieldnames
    assert "status" in reader.fieldnames
    assert "priority_score" in reader.fieldnames
    assert len(loaded_rows) == 1
    assert loaded_rows[0]["event_id"] == "EVT-TEST-401"
    assert loaded_rows[0]["subsystem"] == "NAV"
    assert loaded_rows[0]["status"] == "ACK"


def test_export_rows_to_csv_returns_zero_for_empty_rows(tmp_path):
    output_file = tmp_path / "exports" / "empty.csv"

    exported_count = export_rows_to_csv([], output_file)

    assert exported_count == 0
    assert not output_file.exists()


def test_export_rows_to_csv_writes_multiple_rows(tmp_path):
    rows = [
        make_export_row(event_id="EVT-TEST-402", subsystem="COMMS"),
        make_export_row(event_id="EVT-TEST-403", subsystem="SENSOR"),
    ]
    output_file = tmp_path / "exports" / "multiple.csv"

    exported_count = export_rows_to_csv(rows, output_file)

    with output_file.open(mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        loaded_rows = list(reader)

    assert exported_count == 2
    assert len(loaded_rows) == 2
    assert loaded_rows[0]["event_id"] == "EVT-TEST-402"
    assert loaded_rows[1]["event_id"] == "EVT-TEST-403"

def test_export_rows_to_csv_raises_runtime_error_on_write_failure(tmp_path, monkeypatch):
    rows = [make_export_row()]
    output_file = tmp_path / "exports" / "ack_events.csv"

    def fake_open(*args, **kwargs):
        raise OSError("Disk full")

    monkeypatch.setattr(type(output_file), "open", fake_open)

    try:
        export_rows_to_csv(rows, output_file)
        assert False, "Expected RuntimeError to be raised"
    except RuntimeError as exc:
        assert "Failed to export CSV" in str(exc)
        assert "Disk full" in str(exc)