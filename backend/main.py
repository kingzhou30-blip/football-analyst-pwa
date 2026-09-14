"""Entry point aplikasi Flask untuk backend Football Analyst PWA."""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from src.api.routes.health import health_bp
from src.api.routes.predictions import predictions_bp


load_dotenv()
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
LOGGER = logging.getLogger(__name__)


def create_app() -> Flask:
    """Membuat dan mengonfigurasi instance Flask."""
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.register_blueprint(health_bp)
    app.register_blueprint(predictions_bp)

    @app.errorhandler(404)
    def not_found(_error):
        """Mengembalikan error 404 dalam format JSON."""
        return jsonify({"error": "Endpoint tidak ditemukan"}), 404

    @app.errorhandler(500)
    def internal_error(_error):
        """Mengembalikan error 500 dalam format JSON."""
        LOGGER.exception("Kesalahan internal tidak tertangani")
        return jsonify({"error": "Kesalahan internal server"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=os.getenv("FLASK_DEBUG", "true").lower() == "true")
