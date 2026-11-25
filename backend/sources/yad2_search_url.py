"""Yad2: only emit legal search URLs — no scraping."""

from __future__ import annotations

from datetime import datetime
from urllib.parse import urlencode

from backend.models import SearchProfile
from backend.schemas import SearchResultDTO
from backend.services.geo import get_nearby_cities
from backend.sources.base import SourceAdapter


class Yad2SearchUrlSource(SourceAdapter):
    id = "yad2_search_url"
    name = "יד2 (קישור חיפוש)"

    @property
    def legal_mode(self) -> str:
        return "search_url"

    def build_urls(self, profile: SearchProfile) -> list[tuple[str, str]]:
        # Yad2 cars query params vary; this is a best-effort template for manual discovery.
        nearby = get_nearby_cities(
            profile.base_latitude,
            profile.base_longitude,
            profile.radius_km,
            limit=6,
        )
        cities = nearby or [profile.base_location_name]
        out: list[tuple[str, str]] = []
        for city in cities:
            params = {
                "price": f"{int(profile.min_price)}-{int(profile.max_price)}",
                "year": f"{profile.min_year}-{min(profile.max_year, 2022)}",
                "radius_km": int(profile.radius_km),
                "location_hint": city,
            }
            base = "https://www.yad2.co.il/vehicles/cars"
            out.append((city, f"{base}?{urlencode(params)}"))
        return out

    def search(self, session, profile: SearchProfile, extra_urls: list[str] | None = None) -> list[SearchResultDTO]:
        rows: list[SearchResultDTO] = []
        for city, url in self.build_urls(profile):
            rows.append(
                SearchResultDTO(
                    title=f"חיפוש יד2 — {city}",
                    url=url,
                    snippet=(
                        f"קישור חיפוש מוכן לפי מחיר/שנה ורדיוס {int(profile.radius_km)} ק״מ עבור {city}. "
                        "יש לפתוח ולבצע סינון ידני באתר. המערכת לא שולפת מודעות בניגוד לתנאי השימוש."
                    ),
                    source_name=self.name,
                    found_at=datetime.utcnow(),
                    raw_text=url,
                )
            )
        return rows
