"""Orchestrates enabled sources → listings → geo → dedupe → evaluation."""

from __future__ import annotations

import json
from datetime import datetime

from sqlmodel import Session, select

from backend.models import (
    CarEvaluation,
    CarListing,
    LegalMode,
    RunStatus,
    SearchProfile,
    SearchRun,
    SearchRunSource,
    SourceConfig,
    SourceType,
)
from backend.schemas import SearchResultDTO
from backend.services import deduplication, evaluation, normalization
from backend.services.geo import haversine_km, resolve_coordinates
from backend.services.source_registry import get_adapter


def _active_profile(session: Session) -> SearchProfile:
    row = session.exec(select(SearchProfile).where(SearchProfile.is_active == True)).first()  # noqa: E712
    if row:
        return row
    p = SearchProfile()
    session.add(p)
    session.commit()
    session.refresh(p)
    return p


def _upsert_listing(session: Session, listing: CarListing) -> CarListing:
    existing = session.exec(select(CarListing).where(CarListing.source_url == listing.source_url)).first()
    if existing:
        for field in [
            "title",
            "make",
            "model",
            "trim",
            "year",
            "price",
            "mileage",
            "fuel_type",
            "description",
            "location_text",
            "city",
            "incomplete",
            "source_name",
            "source_type",
        ]:
            val = getattr(listing, field, None)
            if val is not None and val != "":
                setattr(existing, field, val)
        existing.date_updated = datetime.utcnow()
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    session.add(listing)
    session.commit()
    session.refresh(listing)
    return listing


def _apply_geo_and_radius(session: Session, listing: CarListing, profile: SearchProfile) -> None:
    lat, lon, _ = resolve_coordinates(
        session,
        listing.location_text,
        listing.city,
        listing.latitude,
        listing.longitude,
    )
    if lat is None or lon is None:
        listing.location_unknown = True
        listing.distance_from_kiryat_tivon_km = None
        listing.beyond_radius = False
    else:
        listing.latitude = lat
        listing.longitude = lon
        listing.location_unknown = False
        d = haversine_km(lat, lon, profile.base_latitude, profile.base_longitude)
        listing.distance_from_kiryat_tivon_km = round(d, 2)
        listing.beyond_radius = d > profile.radius_km


def _evaluate_save(session: Session, listing: CarListing, profile: SearchProfile) -> None:
    if not listing.id:
        return
    ev = evaluation.evaluate_listing(listing, profile)
    ev.listing_id = listing.id
    old = session.exec(select(CarEvaluation).where(CarEvaluation.listing_id == listing.id)).first()
    if old:
        for k, v in ev.model_dump(exclude={"id"}).items():
            if k == "listing_id":
                continue
            setattr(old, k, v)
        session.add(old)
    else:
        session.add(ev)
    session.commit()


def ensure_source_configs(session: Session) -> None:
    defaults: list[tuple[str, str, str, str, str, str, bool, str]] = [
        (
            "google_cse",
            "Google Programmable Search",
            SourceType.unknown.value,
            LegalMode.api.value,
            "https://www.googleapis.com/customsearch/v1",
            "דורש GOOGLE_CSE_ID ו-GOOGLE_API_KEY בקובץ .env",
            False,
            "חיפוש חוקי דרך API של גוגל",
        ),
        (
            "yad2_search_url",
            "יד2 (קישור חיפוש)",
            SourceType.private_market.value,
            LegalMode.search_url.value,
            "https://www.yad2.co.il/",
            "נוצר קישור חיפוש — יש לפתוח ידנית",
            False,
            "ללא שאיבת אתר; רק קישור מוכן",
        ),
        (
            "carwiz_search_url",
            "Carwiz (קישור)",
            SourceType.trade_in.value,
            LegalMode.search_url.value,
            "https://www.carwiz.co.il/",
            "קישור לאתר הסוכנות",
            False,
            "ללא שאיבה אוטומטית",
        ),
        (
            "manual_url",
            "קישורים ידניים",
            SourceType.manual.value,
            LegalMode.manual.value,
            "",
            "הוסיפו קישורים בעמוד המקורות או בזמן חיפוש",
            False,
            "מקורות שהמשתמש מזין",
        ),
        (
            "dealership_manual",
            "סוכנויות (ידני)",
            SourceType.dealership.value,
            LegalMode.manual.value,
            "",
            "מבוסס על סוכנויות שמורות במערכת",
            False,
            "קישורים לאתרי סוכנויות בלבד",
        ),
    ]
    for sid, name, st, lm, base, instr, parser, notes in defaults:
        row = session.get(SourceConfig, sid)
        if not row:
            session.add(
                SourceConfig(
                    id=sid,
                    name=name,
                    source_type=st,
                    enabled=True,
                    legal_mode=lm,
                    base_url=base,
                    search_instructions=instr,
                    parser_available=parser,
                    notes=notes,
                )
            )
    session.commit()


def run_search_agent(session: Session, run_id: int, extra_manual_urls: list[str] | None = None) -> None:
    profile = _active_profile(session)
    run = session.get(SearchRun, run_id)
    if not run:
        return
    run.status = RunStatus.running.value
    session.add(run)
    session.commit()

    sources_rows = list(session.exec(select(SourceConfig)))

    google_missing_config = False
    google_empty_results = False
    try:
        for sc in sources_rows:
            srs_row = session.exec(
                select(SearchRunSource).where(SearchRunSource.run_id == run_id, SearchRunSource.source_id == sc.id)
            ).first()
            if not srs_row:
                continue
            srs_row.started_at = datetime.utcnow()
            if not sc.enabled:
                srs_row.status = RunStatus.done.value
                srs_row.results_found = 0
                srs_row.valid_listings = 0
                srs_row.error_he = "מקור מושבת"
                srs_row.completed_at = datetime.utcnow()
                session.add(srs_row)
                session.commit()
                continue

            adapter = get_adapter(sc.id)
            if not adapter:
                srs_row.status = RunStatus.error.value
                srs_row.error_he = "אין מתאם למקור זה"
                srs_row.completed_at = datetime.utcnow()
                session.add(srs_row)
                session.commit()
                continue

            srs_row.status = RunStatus.running.value
            session.add(srs_row)
            session.commit()
            try:
                results: list[SearchResultDTO] = adapter.search(
                    session, profile, extra_urls=extra_manual_urls if sc.id == "manual_url" else None
                )
                if sc.id == "google_cse":
                    is_configured = bool(getattr(adapter, "is_configured", lambda: True)())
                    if not is_configured:
                        google_missing_config = True
                    if is_configured and len(results) == 0:
                        google_empty_results = True
                valid = 0
                for sr in results:
                    listing = normalization.search_result_to_listing(sr, sc.name)
                    listing = _upsert_listing(session, listing)
                    _apply_geo_and_radius(session, listing, profile)
                    session.add(listing)
                    session.commit()
                    session.refresh(listing)
                    _evaluate_save(session, listing, profile)
                    if (not listing.beyond_radius) and (not listing.is_duplicate):
                        valid += 1
                srs_row.results_found = len(results)
                srs_row.valid_listings = valid
                srs_row.status = RunStatus.done.value
                if sc.id == "google_cse" and google_missing_config:
                    srs_row.error_he = "Google CSE לא מוגדר (.env חסר/חלקי) — הופעל fallback חוקי ממקורות ידניים."
                elif sc.id == "google_cse" and google_empty_results:
                    srs_row.error_he = "Google CSE הוגדר אך החזיר 0 תוצאות בריצה זו — הופעל fallback חוקי."
                else:
                    srs_row.error_he = None
                sc.last_searched_at = datetime.utcnow()
                sc.last_result_count = len(results)
                session.add(sc)
            except Exception as e:  # noqa: BLE001
                srs_row.status = RunStatus.error.value
                srs_row.error_he = f"שגיאה במקור {sc.name}: {e}"
                srs_row.results_found = 0
                srs_row.valid_listings = 0
            srs_row.completed_at = datetime.utcnow()
            session.add(srs_row)
            session.commit()

        # Explicitly mark fallback sources as boosted when Google is unavailable/empty.
        if google_missing_config or google_empty_results:
            reason_he = (
                "Google לא מוגדר — fallback פעיל"
                if google_missing_config
                else "Google החזיר 0 תוצאות — fallback פעיל"
            )
            for sid in ("yad2_search_url", "carwiz_search_url", "manual_url", "dealership_manual"):
                row = session.exec(
                    select(SearchRunSource).where(SearchRunSource.run_id == run_id, SearchRunSource.source_id == sid)
                ).first()
                if row and row.status == RunStatus.done.value and not row.error_he:
                    row.error_he = reason_he
                    session.add(row)
            session.commit()

        deduplication.deduplicate_session(session)
        listings = list(session.exec(select(CarListing).where(CarListing.is_duplicate == False)))  # noqa: E712
        for lst in listings:
            _apply_geo_and_radius(session, lst, profile)
            session.add(lst)
            session.commit()
            session.refresh(lst)
            _evaluate_save(session, lst, profile)

        run.status = RunStatus.done.value
        run.completed_at = datetime.utcnow()
        session.add(run)
        session.commit()
    except Exception as e:  # noqa: BLE001
        run.status = RunStatus.error.value
        run.error_message_he = f"החיפוש נכשל: {e}"
        run.completed_at = datetime.utcnow()
        session.add(run)
        session.commit()
