"""Scoring, Hebrew explanations, red flags, seller questions, checklist."""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any

from backend.config import settings
from backend.models import CarListing, CarEvaluation, Recommendation, SearchProfile

WEIGHT_PRICE = 20
WEIGHT_MILEAGE = 20
WEIGHT_YEAR = 15
WEIGHT_FUEL = 15
WEIGHT_LOCATION = 10
WEIGHT_RELIABILITY = 10
WEIGHT_SELLER = 5
WEIGHT_RISK = 5

SUSPICIOUS_PHRASES = [
    "מציאה",
    "חייב להימכר מהר",
    "בלי בדיקה",
    "דחוף",
    "מחיר הזוי",
    "לא מתווך",
    "טסט עבר",
]


def _load_reliability() -> dict[str, Any]:
    path = settings.reliability_profiles_path
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"models": []}


def _match_reliability(make: str, model: str) -> dict[str, Any] | None:
    blob = f"{make} {model}".lower()
    for m in _load_reliability().get("models", []):
        key = m.get("make_model_key", "").lower()
        if key and key in blob:
            return m
    return None


def collect_red_flags(
    listing: CarListing,
    profile: SearchProfile,
    annual_mileage: float | None,
) -> list[str]:
    flags: list[str] = []
    text = f"{listing.title} {listing.description}".lower()

    if listing.price is not None and listing.price < profile.min_price - 3000:
        flags.append("מחיר נמוך מהצפוי לעומת השוק — לבדוק סיבה")
    if listing.price is not None and listing.price > 47000:
        flags.append("מחיר מעל טווח נוח לתקציב המוגדר")
    if listing.mileage is None:
        flags.append("חסר קילומטראז' — דגל אדום")
    if not listing.seller_phone and listing.seller_type == "private":
        flags.append("אין טלפון מוכר — קשה לוודא רצינות")
    if not (listing.location_text or listing.city):
        flags.append("מיקום לא ברור")
    if listing.ownership_type in ("leasing", "rental", "company"):
        flags.append("בעלות חברה/ליסינג/השכרה — לבדוק מצב ותיעוד")
    if listing.previous_owners and listing.previous_owners >= 4:
        flags.append("מספר בעלים קודמים גבוה")
    if annual_mileage and annual_mileage > 28000:
        flags.append("קילומטראז' שנתי גבוה מאוד")
    if annual_mileage is not None and listing.year and annual_mileage < 2000:
        flags.append("קילומטראז' שנתי חשוד נמוך לגיל הרכב")
    try:
        imgs = json.loads(listing.image_urls or "[]")
    except json.JSONDecodeError:
        imgs = []
    if not imgs:
        flags.append("אין תמונות במודעה")

    for ph in SUSPICIOUS_PHRASES:
        if ph.lower() in text:
            flags.append(f"ניסוח חשוד: {ph}")

    return flags


def score_price(price: float | None, profile: SearchProfile) -> tuple[float, list[str]]:
    notes: list[str] = []
    if price is None:
        return 2.0, ["חסר מחיר"]
    if profile.min_price <= price <= profile.max_price:
        return 20.0, []
    if 32000 <= price < profile.min_price:
        notes.append("זול מדי — לבדוק למה")
        return 12.0, notes
    if profile.max_price < price <= 47000:
        return 10.0, ["מעל תקציב מועדף אך עדיין אפשרי"]
    if price > 47000:
        return 4.0, ["מחיר גבוה משמעותית מהטווח"]
    return 6.0, notes


def score_mileage(mileage: int | None, profile: SearchProfile, year: int | None) -> tuple[float, float | None]:
    annual = None
    if mileage is not None and year:
        cy = datetime.utcnow().year
        denom = max(1, cy - year + 1)
        annual = mileage / denom
    if mileage is None:
        return 3.0, annual
    if mileage < 80000:
        return 20.0, annual
    if mileage <= profile.max_mileage_preferred:
        return 16.0, annual
    if mileage <= profile.max_mileage_absolute:
        return 10.0, annual
    return 4.0, annual


def score_year(year: int | None, profile: SearchProfile, price: float | None) -> float:
    if year is None:
        return 4.0
    if profile.min_year <= year <= min(2022, profile.max_year):
        return 15.0
    if year > 2022 and year <= profile.max_year:
        if price and price <= profile.max_price:
            return 14.0
        return 8.0
    if year < profile.min_year:
        return 5.0
    return 10.0


def score_fuel(fuel: str, preference: str) -> float:
    f = (fuel or "unknown").lower()
    if f == "hybrid" or f == "plugin_hybrid":
        return 15.0 if preference != "petrol_small_engine" else 13.0
    if f == "petrol":
        return 11.0 if preference in ("any", "petrol_small_engine") else 9.0
    if f == "diesel":
        return 9.0 if preference in ("any", "diesel_optional") else 7.0
    if f == "electric":
        return 10.0
    return 6.0


def score_location(distance_km: float | None, unknown: bool, beyond: bool) -> float:
    if beyond and distance_km is not None:
        return 2.0
    if unknown or distance_km is None:
        return 5.0
    if distance_km <= 10:
        return 10.0
    if distance_km <= 20:
        return 8.0
    if distance_km <= 30:
        return 6.0
    return 3.0


def score_reliability(listing: CarListing) -> float:
    hit = _match_reliability(listing.make, listing.model)
    if not hit:
        return 6.0
    hint = float(hit.get("reliability_hint", 0.7))
    return round(10.0 * hint, 2)


def score_seller(listing: CarListing) -> float:
    s = 3.0
    if listing.seller_phone:
        s += 1.5
    if listing.seller_name:
        s += 0.5
    if listing.seller_type == "dealership":
        s += 0.5
    return min(5.0, s)


def score_risk(red_flags: list[str]) -> float:
    """Higher score = lower risk (max 5)."""
    penalty = min(5.0, len(red_flags) * 0.8)
    return max(0.0, 5.0 - penalty)


def recommendation_from(total: float, red_flags: list[str]) -> str:
    if total >= 78 and len(red_flags) <= 1:
        return Recommendation.worth_checking.value
    if total >= 60:
        return Recommendation.possible.value
    if total >= 45:
        return Recommendation.caution.value
    return Recommendation.not_recommended.value


def build_explanation_hebrew(
    listing: CarListing,
    profile: SearchProfile,
    red_flags: list[str],
    sub: dict[str, float],
) -> str:
    parts: list[str] = []
    if listing.price and profile.min_price <= listing.price <= profile.max_price:
        parts.append("הרכב בטווח התקציב המוגדר.")
    elif listing.price:
        parts.append("המחיר מחוץ לטווח המועדף או דורש בדיקה מעמיקה.")
    else:
        parts.append("חסר מחיר ברור — חשוב לוודא מול המוכר.")

    if listing.distance_from_kiryat_tivon_km is not None:
        parts.append(f"מרחק משוער מקריית טבעון: כ-{listing.distance_from_kiryat_tivon_km:.1f} ק\"מ.")
    elif listing.location_unknown:
        parts.append("מיקום לא מדויק — כדאי לוודא מול המוכר.")

    if listing.year:
        parts.append(f"שנתון {listing.year}.")

    if listing.mileage is not None:
        parts.append(f"קילומטראז' {listing.mileage:,} ק\"מ — יש להשוות לגיל הרכב ולשימוש.")
    else:
        parts.append("חסר קילומטראז' במודעה — לבדוק ברישיון ובטסט.")

    if red_flags:
        parts.append("יש דגלי אזהרה: " + "; ".join(red_flags[:3]) + ".")
    else:
        parts.append("לא זוהו דגלי אזהרה אוטומטיים חריגים.")

    parts.append("מומלץ לבדוק היסטוריית טיפולים, בעלות קודמת ותוקף טסט לפני התקדמות.")
    return " ".join(parts)


def default_seller_questions() -> list[str]:
    return [
        "האם הרכב בבעלות פרטית?",
        "כמה בעלים קודמים היו?",
        "האם יש ספר טיפולים?",
        "האם הרכב עבר תאונות?",
        "האם יש שעבוד או עיקול?",
        "מתי הטסט הבא?",
        "למה הרכב נמכר?",
        "האם אפשר לקחת את הרכב לבדיקה במכון?",
        "האם הקילומטראז' מופיע ברישיון/טסט האחרון?",
        "האם המחיר גמיש?",
    ]


def default_purchase_checklist() -> list[str]:
    return [
        "בדיקת רישיון רכב",
        "בדיקת מספר שלדה ומספר רכב",
        "בדיקת טסט",
        "בדיקת בעלות קודמת",
        "בדיקת שעבודים ועיקולים",
        "בדיקת היסטוריית טיפולים",
        "בדיקה במכון לפני קנייה",
        "לא להעביר כסף לפני בדיקת מסמכים",
        "לא להסתמך רק על דברי המוכר",
        "להשוות למחיר שוק",
    ]


def evaluate_listing(listing: CarListing, profile: SearchProfile) -> CarEvaluation:
    annual = None
    if listing.mileage is not None and listing.year:
        annual = listing.mileage / max(1, datetime.utcnow().year - listing.year + 1)

    red_flags = collect_red_flags(listing, profile, annual)
    p_score, p_notes = score_price(listing.price, profile)
    m_score, _ = score_mileage(listing.mileage, profile, listing.year)
    y_score = score_year(listing.year, profile, listing.price)
    f_score = score_fuel(listing.fuel_type, profile.fuel_preference)
    l_score = score_location(listing.distance_from_kiryat_tivon_km, listing.location_unknown, listing.beyond_radius)
    r_score = score_reliability(listing)
    s_score = score_seller(listing)
    risk_component = score_risk(red_flags)

    total = p_score + m_score + y_score + f_score + l_score + r_score + s_score + risk_component
    total = min(100.0, round(total, 1))

    for note in p_notes:
        if note not in red_flags and ("זול" in note or "מחיר" in note):
            red_flags.append(note)

    sub = {
        "price": p_score,
        "mileage": m_score,
        "year": y_score,
        "fuel": f_score,
        "location": l_score,
        "reliability": r_score,
        "seller": s_score,
        "risk": risk_component,
    }
    explanation = build_explanation_hebrew(listing, profile, red_flags, sub)
    rec = recommendation_from(total, red_flags)

    return CarEvaluation(
        listing_id=listing.id or 0,
        total_score=total,
        price_score=p_score,
        mileage_score=m_score,
        year_score=y_score,
        fuel_efficiency_score=f_score,
        reliability_score=r_score,
        location_score=l_score,
        seller_trust_score=s_score,
        risk_score=risk_component,
        explanation_hebrew=explanation,
        red_flags=json.dumps(red_flags, ensure_ascii=False),
        recommendation=rec,
    )
