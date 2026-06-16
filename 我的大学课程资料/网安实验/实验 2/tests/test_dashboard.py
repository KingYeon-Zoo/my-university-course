import json

from src.dashboard import create_app


def test_dashboard_api_reads_alerts_from_configured_eve_file(tmp_path):
    eve_path = tmp_path / "eve.json"
    eve_path.write_text(
        json.dumps(
            {
                "timestamp": "2026-06-03T10:00:00+0800",
                "event_type": "alert",
                "src_ip": "198.51.100.20",
                "dest_ip": "10.0.0.2",
                "dest_port": 8080,
                "alert": {
                    "signature": "LAB-IPS XSS Attempt",
                    "category": "Web Application Attack",
                    "action": "blocked",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    client = create_app(eve_path).test_client()

    response = client.get("/api/alerts")

    assert response.status_code == 200
    assert response.get_json()["events"][0]["blocked"] is True

