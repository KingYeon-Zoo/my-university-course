"""A deliberately non-vulnerable HTTP service for the IPS lab."""

from __future__ import annotations

import argparse

from flask import Flask, jsonify


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    @app.get("/search")
    @app.get("/download")
    @app.get("/api/run")
    def reached():
        return jsonify(
            {
                "message": "request reached the lab service",
                "note": "This service never executes or reflects supplied payloads.",
            }
        )

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the harmless ECS HTTP lab service")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    create_app().run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()

