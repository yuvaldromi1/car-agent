from __future__ import annotations

import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import CarEvaluation, CarListing, SearchProfile
from backend.schemas import (
    CarListingCreate,
    CarListingDetailRead,
    CarListingRead,
    CarListingUpdate,
    parse_image_urls,
    parse_red_flags,
)
from backend.services import deduplication, evaluation, normalization
from backend.services.search_agent import _active_profile, _apply_geo_and_radius, _evaluate_save

router = APIRouter(prefix="/listings", tags=["listings"])


def _to_read(session: Session, listing: CarListing) -> CarListingRead:
    ev = session.exec(select(CarEvaluation).where(CarEvaluation.listing_id == listing.id)).first()
    flags = parse_red_flags(ev.red_flags) if ev else []
    return CarListingRead.from_orm_listing(listing, ev, parse_image_urls(listing.image_urls), flags)


@router.get("")
def list_listings(
    session: Session = Depends(get_session),
    hide_duplicates: bool = True,
    hide_beyond_radius: bool = False,
    min_score: float | None = None,
):
    q = select(CarListing)
    if hide_duplicates:
        q = q.where(CarListing.is_duplicate == False)  # noqa: E712
    if hide_beyond_radius:
        q = q.where(CarListing.beyond_radius == False)  # noqa: E712
    rows = list(session.exec(q))
    out: list[CarListingRead] = []
    for lst in rows:
        read = _to_read(session, lst)
        if min_score is not None and read.evaluation and read.evaluation.total_score < min_score:
            continue
        out.append(read)
    out.sort(key=lambda r: (r.evaluation.total_score if r.evaluation else 0), reverse=True)
    return out


@router.get("/{listing_id}")
def get_listing(listing_id: int, session: Session = Depends(get_session)):
    lst = session.get(CarListing, listing_id)
    if not lst:
        raise HTTPException(status_code=404, detail="המודעה לא נמצאה")
    base = _to_read(session, lst)
    ev = session.exec(select(CarEvaluation).where(CarEvaluation.listing_id == lst.id)).first()
    flags = parse_red_flags(ev.red_flags) if ev else []
    return CarListingDetailRead(
        **base.model_dump(),
        seller_questions=evaluation.default_seller_questions(),
        purchase_checklist=evaluation.default_purchase_checklist(),
    )


@router.post("")
def create_listing(body: CarListingCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(CarListing).where(CarListing.source_url == body.source_url)).first()
    if existing:
        raise HTTPException(status_code=400, detail="כבר קיימת מודעה עם אותו קישור")
    lst = CarListing(
        source_name=body.source_name,
        source_type=body.source_type,
        source_url=body.source_url,
        title=body.title,
        make=body.make,
        model=body.model,
        trim=body.trim,
        year=body.year,
        price=body.price,
        mileage=body.mileage,
        fuel_type=body.fuel_type,
        transmission=body.transmission,
        engine_size=body.engine_size,
        ownership_type=body.ownership_type,
        previous_owners=body.previous_owners,
        seller_type=body.seller_type,
        seller_name=body.seller_name,
        seller_phone=body.seller_phone,
        location_text=body.location_text,
        city=body.city,
        latitude=body.latitude,
        longitude=body.longitude,
        description=body.description,
        image_urls=json.dumps(body.image_urls, ensure_ascii=False),
        license_plate=body.license_plate,
        test_valid_until=body.test_valid_until,
        notes=body.notes,
        status=body.status,
        incomplete=not (body.price and body.year),
    )
    session.add(lst)
    session.commit()
    session.refresh(lst)
    profile = _active_profile(session)
    _apply_geo_and_radius(session, lst, profile)
    session.add(lst)
    session.commit()
    session.refresh(lst)
    _evaluate_save(session, lst, profile)
    return _to_read(session, lst)


@router.put("/{listing_id}")
def update_listing(listing_id: int, body: CarListingUpdate, session: Session = Depends(get_session)):
    lst = session.get(CarListing, listing_id)
    if not lst:
        raise HTTPException(status_code=404, detail="המודעה לא נמצאה")
    data = body.model_dump(exclude_unset=True)
    if "image_urls" in data and data["image_urls"] is not None:
        data["image_urls"] = json.dumps(data["image_urls"], ensure_ascii=False)
    for k, v in data.items():
        setattr(lst, k, v)
    lst.date_updated = datetime.utcnow()
    session.add(lst)
    session.commit()
    session.refresh(lst)
    profile = _active_profile(session)
    _apply_geo_and_radius(session, lst, profile)
    session.add(lst)
    session.commit()
    session.refresh(lst)
    _evaluate_save(session, lst, profile)
    return _to_read(session, lst)


@router.delete("/{listing_id}")
def delete_listing(listing_id: int, session: Session = Depends(get_session)):
    lst = session.get(CarListing, listing_id)
    if not lst:
        raise HTTPException(status_code=404, detail="המודעה לא נמצאה")
    ev = session.exec(select(CarEvaluation).where(CarEvaluation.listing_id == listing_id)).first()
    if ev:
        session.delete(ev)
    session.delete(lst)
    session.commit()
    return {"ok": True}


@router.post("/import-csv")
async def import_csv(file: UploadFile = File(...), session: Session = Depends(get_session)):
    raw = await file.read()
    text = raw.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    profile = _active_profile(session)
    count = 0
    for row in reader:
        try:
            lst = normalization.csv_row_to_listing(row)
            ex = session.exec(select(CarListing).where(CarListing.source_url == lst.source_url)).first()
            if ex:
                continue
            session.add(lst)
            session.commit()
            session.refresh(lst)
            _apply_geo_and_radius(session, lst, profile)
            session.add(lst)
            session.commit()
            session.refresh(lst)
            _evaluate_save(session, lst, profile)
            count += 1
        except Exception:  # noqa: BLE001
            continue
    return {"imported": count, "message_he": f"יובאו {count} מודעות מהקובץ"}


@router.post("/{listing_id}/evaluate")
def evaluate_one(listing_id: int, session: Session = Depends(get_session)):
    lst = session.get(CarListing, listing_id)
    if not lst:
        raise HTTPException(status_code=404, detail="המודעה לא נמצאה")
    profile = _active_profile(session)
    _evaluate_save(session, lst, profile)
    return _to_read(session, lst)


@router.post("/deduplicate")
def dedupe(session: Session = Depends(get_session)):
    n = deduplication.deduplicate_session(session)
    profile = _active_profile(session)
    for lst in list(session.exec(select(CarListing).where(CarListing.is_duplicate == False))):  # noqa: E712
        _evaluate_save(session, lst, profile)
    return {"marked_duplicates": n, "message_he": "סימון כפילויות הושלם"}
