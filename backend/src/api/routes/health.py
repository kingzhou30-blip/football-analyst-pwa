"""Blueprint endpoint pemeriksaan kesehatan backend."""

from datetime import datetime, timezone

from flask import Blueprint, jsonify


health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def health() -> tuple:
    """Mengembalikan status hidup server dan timestamp UTC."""
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})

