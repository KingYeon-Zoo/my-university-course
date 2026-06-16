"""Browser dashboard for recent Suricata alerts."""

from __future__ import annotations

import argparse
from pathlib import Path

from flask import Flask, jsonify, render_template

from src.eve_reader import read_recent_alerts


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVE_PATH = Path("/var/log/suricata/eve.json")


def create_app(eve_path: str | Path = DEFAULT_EVE_PATH) -> Flask:
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "templates"),
        static_folder=str(PROJECT_ROOT / "static"),
    )
    app.config["EVE_PATH"] = Path(eve_path)

    @app.get("/")
    def index():
        return render_template("dashboard.html")

    @app.get("/api/alerts")
    def alerts():
        events = read_recent_alerts(app.config["EVE_PATH"], limit=200)
        return jsonify(
            {
                "events": events,
                "total": len(events),
                "blocked": sum(event["blocked"] for event in events),
                "eve_path": str(app.config["EVE_PATH"]),
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "eve_path": str(app.config["EVE_PATH"])})

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Suricata EVE alert dashboard")
    parser.add_argument("--eve", default=str(DEFAULT_EVE_PATH))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8090)
    args = parser.parse_args()
    create_app(args.eve).run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()

