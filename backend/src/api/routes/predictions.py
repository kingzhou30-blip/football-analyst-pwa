"""
Blueprint untuk endpoint prediksi pertandingan sepak bola.

Menyediakan endpoint:
- GET /api/v1/daily              -> daftar 5-7 rekomendasi hari ini
- GET /api/v1/daily?date=...     -> rekomendasi untuk tanggal tertentu
- GET /api/v1/match/<match_id>   -> detail analisis 1 pertandingan
- GET /api/v1/accuracy           -> statistik akurasi model
- GET /api/v1/accuracy?days=30   -> akurasi N hari terakhir
"""

import logging
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from src.services.supabase_client import SupabaseClient
from src.services.football_api import FootballAPI

# Inisialisasi logger
LOGGER = logging.getLogger(__name__)

# Buat blueprint
predictions_bp = Blueprint("predictions", __name__, url_prefix="/api/v1")

# Inisialisasi service (singleton)
supabase_client = SupabaseClient()
football_api = FootballAPI()


def _error(message: str, status_code: int = 400) -> tuple:
    """
    Helper untuk mengembalikan response error dalam format JSON.

    Args:
        message: pesan error
        status_code: HTTP status code

    Returns:
        Tuple (response, status_code)
    """
    return jsonify({"error": message, "status": status_code}), status_code


@predictions_bp.route("/daily", methods=["GET"])
def get_daily():
    """
    Endpoint untuk mengambil daftar rekomendasi pertandingan harian.

    Query params:
        date (opsional): format YYYY-MM-DD. Default: hari ini.

    Returns:
        JSON dengan struktur:
        {
            "date": "2026-09-14",
            "count": 5,
            "matches": [...]
        }
    """
    try:
        target_date = request.args.get("date") or datetime.now(timezone.utc).date().isoformat()

        # Validasi format tanggal kalau ada
        if target_date:
            try:
                datetime.strptime(target_date, "%Y-%m-%d")
            except ValueError:
                return _error("Format date harus YYYY-MM-DD", 400)

        # Ambil dari Supabase
        matches = supabase_client.get_daily_predictions(target_date)

        return jsonify({
            "date": target_date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "count": len(matches),
            "matches": matches,
        })

    except Exception as exc:
        LOGGER.exception("Gagal mengambil rekomendasi harian")
        return _error(f"Gagal mengambil rekomendasi harian: {exc}", 502)


@predictions_bp.route("/match/<match_id>", methods=["GET"])
def get_match_detail(match_id: str):
    """
    Endpoint untuk mengambil detail analisis 1 pertandingan.

    Args:
        match_id: UUID atau string ID pertandingan

    Returns:
        JSON detail pertandingan + analisis 5 kategori
    """
    try:
        if not match_id:
            return _error("match_id wajib diisi", 400)

        match = supabase_client.get_match_detail(match_id)

        if not match:
            return _error(f"Pertandingan dengan id {match_id} tidak ditemukan", 404)

        return jsonify(match)

    except Exception as exc:
        LOGGER.exception("Gagal mengambil detail pertandingan")
        return _error(f"Gagal mengambil detail pertandingan: {exc}", 502)


@predictions_bp.route("/accuracy", methods=["GET"])
def get_accuracy():
    """
    Endpoint untuk mengambil statistik akurasi model.

    Query params:
        days (opsional): jumlah hari terakhir. Default: 30. Range: 1-3650.

    Returns:
        JSON dengan statistik akurasi per kategori
    """
    raw_days = request.args.get("days", "30")

    try:
        days = int(raw_days)
        if days < 1 or days > 3650:
            raise ValueError
    except ValueError:
        return _error("Parameter days harus berupa bilangan bulat antara 1 dan 3650", 400)

    try:
        stats = supabase_client.get_accuracy_stats(days)
        return jsonify({"days": days, "count": len(stats), "stats": stats})
    except Exception as exc:
        LOGGER.exception("Gagal mengambil statistik akurasi")
        return _error(f"Gagal mengambil statistik akurasi: {exc}", 502)


@predictions_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check untuk blueprint predictions.

    Returns:
        JSON status OK
    """
    return jsonify({"status": "ok", "service": "predictions"})
