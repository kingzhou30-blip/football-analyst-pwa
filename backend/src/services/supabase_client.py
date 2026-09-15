"""Klien REST Supabase berbasis httpx untuk backend Football Analyst PWA."""

from __future__ import annotations

import logging
import os
from datetime import date, timedelta
from typing import Any

import httpx


LOGGER = logging.getLogger(__name__)


class SupabaseClient:
    """Wrapper tipis untuk endpoint PostgREST Supabase."""

    def __init__(self, timeout: float = 15.0) -> None:
        """Membaca konfigurasi Supabase dari environment dan menyiapkan client."""
        self.base_url = os.getenv("SUPABASE_URL", "").rstrip("/")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY", "")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def close(self) -> None:
        """Menutup koneksi HTTP yang dipakai client."""
        self.client.close()

    def _headers(self) -> dict[str, str]:
        """Membangun header autentikasi REST Supabase."""
        return {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json",
        }

    def _request(self, table_or_view: str, params: dict[str, str]) -> list[dict[str, Any]]:
        """Menjalankan GET PostgREST dan mengembalikan list JSON."""
        if not self.base_url or not self.service_key:
            raise RuntimeError("SUPABASE_URL dan SUPABASE_SERVICE_KEY wajib dikonfigurasi")
        url = f"{self.base_url}/rest/v1/{table_or_view}"
        try:
            response = self.client.get(url, headers=self._headers(), params=params)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list):
                raise httpx.HTTPError("Response Supabase bukan array JSON")
            return payload
        except (httpx.HTTPError, ValueError) as exc:
            LOGGER.exception("Permintaan Supabase gagal untuk %s", table_or_view)
            raise exc

    def get_daily_predictions(self, target_date: str | None = None) -> list[dict[str, Any]]:
        """Mengambil pertandingan terpublikasi beserta seluruh analisisnya, memfilter tanggal bila diberikan."""
        params = {
            "select": "*,match_analyses(*)",
            "is_published": "eq.true",
            "order": "match_score.desc.nullslast,kickoff.asc",
        }
        if target_date:
            params["and"] = f"(kickoff.gte.{target_date}T00:00:00Z,kickoff.lt.{_next_date(target_date)}T00:00:00Z)"
        return self._request("daily_matches", params)

    def get_match_detail(self, match_id: str) -> dict[str, Any] | None:
        """Mengambil pertandingan berdasarkan UUID internal atau match_id eksternal."""
        rows = self._request("daily_matches", {"select": "*", "or": f"(id.eq.{match_id},match_id.eq.{match_id})", "limit": "1"})
        if not rows:
            return None
        match = rows[0]
        analyses = self._request("match_analyses", {"select": "*", "match_id": f"eq.{match['id']}", "order": "confidence.desc.nullslast"})
        match["analyses"] = analyses
        return match

    def get_accuracy_stats(self, days: int = 30) -> list[dict[str, Any]]:
        """Mengambil statistik akurasi dari view untuk rentang hari terakhir."""
        safe_days = max(1, min(days, 3650))
        start_date = (date.today() - timedelta(days=safe_days - 1)).isoformat()
        return self._request("view_accuracy_stats", {
            "select": "*",
            "day": f"gte.{start_date}",
            "order": 
"day.desc,category.asc",
        })


def _next_date(value: str) -> str:
    """Menghasilkan tanggal berikutnya dari string ISO YYYY-MM-DD."""
    return (date.fromisoformat(value) + timedelta(days=1)).isoformat()

