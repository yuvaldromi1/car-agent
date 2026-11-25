from __future__ import annotations

import urllib.parse
from datetime import datetime

import httpx

from backend.config import settings
from backend.models import SearchProfile
from backend.schemas import SearchResultDTO
from backend.services.geo import get_nearby_cities
from backend.services.normalization import extract_mileage, extract_price, extract_year
from backend.sources.base import SourceAdapter


class GoogleProgrammableSearchSource(SourceAdapter):
    id = "google_cse"
    name = "Google Programmable Search"

    @property
    def legal_mode(self) -> str:
        return "api"

    def is_configured(self) -> bool:
        return bool(settings.google_api_key and settings.google_cse_id)

    def _radius_caps(self, radius_km: float) -> tuple[int, int]:
        if radius_km <= 15:
            return 3, 8
        if radius_km <= 30:
            return 6, 12
        return 10, 15

    def _queries(self, profile: SearchProfile) -> list[str]:
        max_cities, max_queries = self._radius_caps(profile.radius_km)
        nearby = get_nearby_cities(
            profile.base_latitude,
            profile.base_longitude,
            profile.radius_km,
            limit=max_cities,
        )
        if profile.base_location_name not in nearby:
            nearby = [profile.base_location_name, *nearby]

        ys = f"{profile.min_year} {min(profile.max_year, 2022)}"
        min_y = profile.min_year
        mx = int(profile.max_price)
        queries: list[str] = []

        for city in nearby:
            queries.extend(
                [
                    f"רכב משפחתי {ys} עד {mx} {city}",
                    f"רכב חסכוני משפחתי יד 2 {city} עד {mx}",
                    f"רכב משפחתי היברידי יד שניה {city} טרייד אין עד {mx}",
                    f"יונדאי איוניק {min_y} יד שניה {city} עד {mx}",
                    f"טויוטה קורולה {min_y} יד שניה {city} עד {mx}",
                    f"סוכנות רכב טרייד אין {city} רכבים עד {mx}",
                ]
            )

        # keep order, remove duplicates, and cap for quota protection
        deduped = list(dict.fromkeys(q.strip() for q in queries if q.strip()))
        return deduped[:max_queries]

    def search(self, session, profile: SearchProfile, extra_urls: list[str] | None = None) -> list[SearchResultDTO]:
        if not self.is_configured():
            return []
        out: list[SearchResultDTO] = []
        with httpx.Client(timeout=20.0) as client:
            for q in self._queries(profile):
                params = {
                    "key": settings.google_api_key,
                    "cx": settings.google_cse_id,
                    "q": q,
                    "num": 10,
                }
                r = client.get("https://www.googleapis.com/customsearch/v1", params=params)
                r.raise_for_status()
                data = r.json()
                for item in data.get("items", []) or []:
                    title = item.get("title", "")
                    url = item.get("link", "")
                    snippet = item.get("snippet", "")
                    blob = f"{title} {snippet}"
                    out.append(
                        SearchResultDTO(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source_name=self.name,
                            found_at=datetime.utcnow(),
                            possible_price=extract_price(blob),
                            possible_year=extract_year(blob),
                            possible_mileage=extract_mileage(blob),
                            raw_text=blob,
                        )
                    )
        return out
