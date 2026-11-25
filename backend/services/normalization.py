"""Normalize SearchResult / CSV rows into CarListing fields."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from backend.models import CarListing, SourceType
from backend.schemas import SearchResultDTO


_PRICE_RE = re.compile(r"(?:₪|ש(?:\"|׳)?ח|ILS|NIS)?\s*([\d]{1,3}(?:[,\s][\d]{3})+|[\d]{4,7})\s*(?:₪|ש(?:\"|׳)?ח)?", re.I)
_YEAR_RE = re.compile(r"\b(20[12][0-9])\b")
_MILEAGE_RE = re.compile(r"([\d]{1,3}(?:[,\s][\d]{3})*)\s*(?:ק[\"׳]?מ|קמ|km|קילומטר)", re.I)


def extract_price(text: str) -> float | None:
    for m in _PRICE_RE.finditer(text):
        raw = m.group(1).replace(",", "").replace(" ", "")
        try:
            val = float(raw)
            if 5000 <= val <= 500000:
                return val
        except ValueError:
            continue
    return None


def extract_year(text: str) -> int | None:
    m = _YEAR_RE.search(text)
    if m:
        return int(m.group(1))
    return None


def extract_mileage(text: str) -> int | None:
    m = _MILEAGE_RE.search(text)
    if m:
        raw = m.group(1).replace(",", "").replace(" ", "")
        try:
            v = int(raw)
            if 0 <= v <= 900000:
                return v
        except ValueError:
            return None
    return None


def guess_make_model_from_title(title: str) -> tuple[str, str]:
    parts = [p for p in re.split(r"[\|\-/]", title) if p.strip()]
    if not parts:
        return "", ""
    head = parts[0].strip()
    tokens = head.split()
    if len(tokens) >= 2:
        return tokens[0], " ".join(tokens[1:6])
    return head, ""


def infer_source_type_from_url(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if "yad2" in host:
        return SourceType.private_market.value
    if "carwiz" in host or "trade" in host:
        return SourceType.trade_in.value
    return SourceType.unknown.value


def search_result_to_listing(sr: SearchResultDTO, source_name: str) -> CarListing:
    blob = f"{sr.title}\n{sr.snippet}\n{sr.raw_text}"
    price = sr.possible_price or extract_price(blob)
    year = sr.possible_year or extract_year(blob)
    mileage = sr.possible_mileage or extract_mileage(blob)
    make, model = guess_make_model_from_title(sr.title)
    loc = sr.possible_location or ""
    incomplete = price is None or year is None or mileage is None

    return CarListing(
        source_name=source_name,
        source_type=infer_source_type_from_url(sr.url),
        source_url=sr.url,
        title=sr.title[:500],
        make=make[:120],
        model=model[:120],
        year=year,
        price=price,
        mileage=mileage,
        location_text=(loc or sr.possible_location or "")[:500],
        description=(sr.snippet or "")[:8000],
        date_found=sr.found_at,
        date_updated=datetime.utcnow(),
        incomplete=incomplete,
        notes="חלק מהשדות חולצו אוטומטית וייתכן שיהיו חסרים — מומלץ לעדכן ידנית." if incomplete else "",
    )


def csv_row_to_listing(row: dict[str, Any]) -> CarListing:
    """Flexible CSV keys (Hebrew or English)."""

    def g(*keys: str) -> Any:
        for k in keys:
            if k in row and row[k] not in (None, ""):
                return row[k]
        return None

    title = str(g("title", "כותרת", "שם") or "מודעה מיובאת")
    url = str(g("source_url", "url", "קישור") or f"csv://import/{hash(title)}")
    return CarListing(
        source_name=str(g("source_name", "מקור") or "csv"),
        source_type=str(g("source_type", "סוג_מקור") or SourceType.csv.value),
        source_url=url,
        title=title,
        make=str(g("make", "יצרן") or ""),
        model=str(g("model", "דגם") or ""),
        trim=g("trim", "גימור"),
        year=int(g("year", "שנה")) if g("year", "שנה") not in (None, "") else None,
        price=float(str(g("price", "מחיר")).replace(",", "")) if g("price", "מחיר") else None,
        mileage=int(str(g("mileage", "קילומטראז")).replace(",", "")) if g("mileage", "קילומטראז") else None,
        fuel_type=str(g("fuel_type", "דלק") or "unknown"),
        transmission=str(g("transmission", "הילוכים") or ""),
        location_text=str(g("location_text", "מיקום", "עיר") or ""),
        city=g("city", "ישוב"),
        description=str(g("description", "תיאור") or ""),
        seller_phone=g("seller_phone", "טלפון"),
        license_plate=g("license_plate", "מספר_רכב"),
        image_urls=json.dumps([], ensure_ascii=False),
        incomplete=not (g("price", "מחיר") and g("year", "שנה")),
    )


def listing_image_urls_set(listing: CarListing, urls: list[str]) -> None:
    listing.image_urls = json.dumps(urls, ensure_ascii=False)
