"""Klien Bzzoiro Sports Data API berbasis httpx."""

from __future__ import annotations

import logging
import os
from datetime import date
from typing import Any

import httpx


LOGGER = logging.getLogger(__name__)


class FootballAPI:
    """Wrapper endpoint Bzzoiro untuk fixtures dan data pertandingan."""

    def __init__(self, timeout: float = 20.0) -> None:
        """Membaca API key dari environment dan menyiapkan client HTTP."""
        self.base_url = os.getenv("BZZOIRO_BASE_URL", "https://sports.bzzoiro.com/api/v2").rstrip("/")
        self.api_key = os.getenv("BZZOIRO_API_KEY", "")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def close(self) -> None:
        """Menutup koneksi HTTP client."""
        self.client.close()

    def _headers(self) -> dict[str, str]:
        """Membangun header autentikasi Bzzoiro."""
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Key": self.api_key,
        }

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any] | list[Any]:
        """Menjalankan GET API dan mengembalikan payload JSON."""
        if not self.api_key:
            raise RuntimeError("BZZOIRO_API_KEY wajib dikonfigurasi")
        try:
            response = self.client.get(f"{self.base_url}/{path.lstrip('/')}", headers=self._headers(), params=params or {})
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, (dict, list)):
                raise httpx.HTTPError("Response Bzzoiro bukan JSON object atau array")
            return payload
        except (httpx.HTTPError, ValueError) as exc:
            LOGGER.exception("Permintaan Bzzoiro gagal: %s", path)
            raise exc

    def fetch_todays_matches(self, target_date: date | None = None) -> dict[str, Any] | list[Any]:
        """Mengambil semua fixture pada tanggal tertentu, default hari ini."""
        selected_date = target_date or date.today()
        value = selected_date.isoformat()
        return self._get("events/", {"date_from": value, "date_to": value})

    def fetch_match_stats(self, match_id: str) -> dict[str, Any] | list[Any]:
        """Mengambil statistik pertandingan berdasarkan ID."""
        return self._get(f"events/{match_id}/stats/")

    def fetch_match_h2h(self, match_id: str) -> dict[str, Any] | list[Any]:
        """Mengambil data head-to-head
  pertandingan berdasarkan ID."""
        return self._get(f"events/{match_id}/h2h/")

    def fetch_match_odds(self, match_id: str) -> dict[str, Any] | list[Any]:
        """Mengambil odds pertandingan berdasarkan ID."""
        return self._get(f"events/{match_id}/odds/")


