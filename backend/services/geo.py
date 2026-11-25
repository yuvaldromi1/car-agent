"""Haversine distance and fallback coordinates for northern Israel."""

from __future__ import annotations

import math
import re
import unicodedata
import httpx
from sqlmodel import Session

from backend.config import settings
from backend.models import GeocodeCache

# Approximate centroids for fallback when geocoding is off or fails (not for hard filtering by name)
FALLBACK_CITY_COORDS: dict[str, tuple[float, float]] = {
    "קריית טבעון": (32.7142, 35.1261),
    "רמת ישי": (32.7047, 35.1697),
    "יקנעם": (32.6539, 35.1034),
    "יקנעם עילית": (32.6539, 35.1034),
    "נשר": (32.7648, 35.0493),
    "חיפה": (32.7940, 34.9896),
    "הקריות": (32.8258, 35.0853),
    "קריית מוצקין": (32.8382, 35.0795),
    "קריית ביאליק": (32.8275, 35.0889),
    "קריית אתא": (32.8056, 35.1026),
    "מגדל העמק": (32.6775, 35.2400),
    "נהלל": (32.6317, 35.1980),
    "עפולה": (32.6074, 35.2899),
    "זבולון": (32.7210, 35.1200),
}


def _normalize_city_key(text: str) -> str:
    t = text.strip().lower()
    t = unicodedata.normalize("NFKC", t)
    return re.sub(r"\s+", " ", t)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(min(1.0, a)))


def get_nearby_cities(
    base_lat: float,
    base_lon: float,
    radius_km: float,
    limit: int = 8,
) -> list[str]:
    """Return nearby fallback cities sorted by distance from base point."""
    max_limit = max(1, min(limit, 20))
    rows: list[tuple[str, float]] = []
    for city_name, (lat, lon) in FALLBACK_CITY_COORDS.items():
        dist = haversine_km(base_lat, base_lon, lat, lon)
        if dist <= radius_km:
            rows.append((city_name, dist))
    rows.sort(key=lambda x: x[1])
    return [city for city, _ in rows[:max_limit]]


def lookup_fallback_coords(location_text: str, city: str | None) -> tuple[float, float] | None:
    blob = _normalize_city_key(f"{location_text} {city or ''}")
    combined = location_text + " " + (city or "")
    for name, coords in FALLBACK_CITY_COORDS.items():
        nk = _normalize_city_key(name)
        if nk in blob or name in combined:
            return coords
    return None


def geocode_cache_get(session: Session, key: str) -> tuple[float, float] | None:
    row = session.get(GeocodeCache, key)
    if row:
        return row.latitude, row.longitude
    return None


def geocode_cache_put(session: Session, key: str, lat: float, lon: float) -> None:
    row = GeocodeCache(location_key=key, latitude=lat, longitude=lon)
    session.merge(row)


def nominatim_geocode(query: str) -> tuple[float, float] | None:
    if not settings.geocoding_enabled:
        return None
    params = {"format": "json", "q": query, "limit": 1}
    headers = {"User-Agent": settings.nominatim_user_agent}
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get("https://nominatim.openstreetmap.org/search", params=params, headers=headers)
            r.raise_for_status()
            data = r.json()
            if data and isinstance(data, list):
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        return None
    return None


def resolve_coordinates(
    session: Session,
    location_text: str,
    city: str | None,
    explicit_lat: float | None,
    explicit_lon: float | None,
) -> tuple[float | None, float | None, bool]:
    """Returns (lat, lon, used_fallback_or_unknown)."""
    if explicit_lat is not None and explicit_lon is not None:
        return explicit_lat, explicit_lon, False

    key = _normalize_city_key(f"{city or ''}|{location_text}")[:200]
    cached = geocode_cache_get(session, key)
    if cached:
        return cached[0], cached[1], False

    coords = lookup_fallback_coords(location_text, city)
    if coords:
        geocode_cache_put(session, key, coords[0], coords[1])
        return coords[0], coords[1], True

    if settings.geocoding_enabled:
        q = f"{city or ''} {location_text} ישראל".strip()
        nom = nominatim_geocode(q)
        if nom:
            geocode_cache_put(session, key, nom[0], nom[1])
            return nom[0], nom[1], False

    return None, None, True
