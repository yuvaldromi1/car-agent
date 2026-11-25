"""Carwiz: search URL helper — no scraping."""

from __future__ import annotations

from datetime import datetime
from urllib.parse import urlencode

from backend.models import SearchProfile
from backend.schemas import SearchResultDTO
from backend.services.geo import get_nearby_cities
from backend.sources.base import SourceAdapter


class CarwizSearchUrlSource(SourceAdapter):
    id = "carwiz_search_url"
    name = "Carwiz (קישור)"

    @property
    def legal_mode(self) -> str:
        return "search_url"

    def build_urls(self, profile: SearchProfile) -> list[tuple[str, str]]:
        nearby = get_nearby_cities(
            profile.base_latitude,
            profile.base_longitude,
            profile.radius_km,
            limit=6,
        )
        cities = nearby or [profile.base_location_name]
        out: list[tuple[str, str]] = []
        for city in cities:
            params = urlencode(
                {
                    "q": f"טרייד אין {city}",
                    "max_price": int(profile.max_price),
                    "min_year": profile.min_year,
                    "radius_km": int(profile.radius_km),
                }
            )
            url = f"https://www.carwiz.co.il/?{params}"
            out.append((city, url))
        return out

    def search(self, session, profile: SearchProfile, extra_urls: list[str] | None = None) -> list[SearchResultDTO]:
        results: list[SearchResultDTO] = []
        for city, url in self.build_urls(profile):
            results.append(
                SearchResultDTO(
                    title=f"Carwiz — טרייד אין {city}",
                    url=url,
                    snippet=(
                        f"קישור חיפוש חוקי עבור {city} (רדיוס {int(profile.radius_km)} ק״מ, עד {int(profile.max_price)} ₪). "
                        "יש להשלים סינון ידני באתר, ללא שאיבת HTML אוטומטית."
                    ),
                    source_name=self.name,
                    found_at=datetime.utcnow(),
                    raw_text=url,
                )
            )
        return results
