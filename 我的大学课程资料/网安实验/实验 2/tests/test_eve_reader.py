import json

from src.eve_reader import parse_eve_line, read_recent_alerts


def test_parse_eve_line_returns_normalized_alert():
    raw = json.dumps(
        {
            "timestamp": "2026-06-03T10:00:00.000000+0800",
            "event_type": "alert",
            "src_ip": "198.51.100.20",
            "src_port": 50123,
            "dest_ip": "10.0.0.2",
            "dest_port": 8080,
            "proto": "TCP",
            "alert": {
                "signature": "LAB-IPS SQL Injection Attempt",
                "category": "Web Application Attack",
                "action": "blocked",
                "severity": 1,
            },
        }
    )

    event = parse_eve_line(raw)

    assert event["signature"] == "LAB-IPS SQL Injection Attempt"
    assert event["action"] == "blocked"
    assert event["blocked"] is True
    assert event["src_ip"] == "198.51.100.20"
    assert event["dest_port"] == 8080


def test_parse_eve_line_ignores_non_alert_and_invalid_json():
    assert parse_eve_line('{"event_type":"flow"}') is None
    assert parse_eve_line("not-json") is None


def test_read_recent_alerts_returns_newest_first_and_skips_bad_lines(tmp_path):
    eve_path = tmp_path / "eve.json"
    eve_path.write_text(
        "\n".join(
            [
                '{"event_type":"flow"}',
                "bad-json",
                '{"timestamp":"1","event_type":"alert","alert":{"signature":"first","action":"allowed"}}',
                '{"timestamp":"2","event_type":"alert","alert":{"signature":"second","action":"blocked"}}',
            ]
        ),
        encoding="utf-8",
    )

    events = read_recent_alerts(eve_path, limit=10)

    assert [event["signature"] for event in events] == ["second", "first"]


def test_read_recent_alerts_handles_missing_file(tmp_path):
    assert read_recent_alerts(tmp_path / "missing.json") == []

