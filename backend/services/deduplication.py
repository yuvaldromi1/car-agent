"""Mark duplicate listings (soft): URL, plate, composite key, similar title+price."""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from sqlmodel import Session, select

from backend.models import CarListing


def _norm_title(t: str) -> str:
    t = t.lower()
    t = re.sub(r"\s+", " ", t)
    return t.strip()[:80]


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def deduplicate_session(session: Session) -> int:
    rows = list(session.exec(select(CarListing)))
    rows.sort(key=lambda r: (r.id is None, r.id or 0))
    by_url: dict[str, CarListing] = {}
    by_plate: dict[str, CarListing] = {}
    by_key: dict[tuple, CarListing] = {}
    marked = 0

    def mark_dup(child: CarListing, parent: CarListing) -> None:
        nonlocal marked
        if child.id is None or parent.id is None or child.id == parent.id:
            return
        if child.is_duplicate:
            return
        child.is_duplicate = True
        child.duplicate_of_id = parent.id
        marked += 1

    for row in rows:
        if row.is_duplicate:
            continue

        if row.source_url in by_url:
            mark_dup(row, by_url[row.source_url])
            continue
        by_url[row.source_url] = row

        if row.license_plate:
            plate = row.license_plate.strip().upper()
            if plate in by_plate:
                mark_dup(row, by_plate[plate])
                continue
            by_plate[plate] = row

        key_ok = row.year is not None and row.price is not None and row.mileage is not None
        key = (
            (row.make or "").lower(),
            (row.model or "").lower(),
            row.year,
            row.price,
            row.mileage,
            (row.city or row.location_text or "").lower()[:40],
        )
        if key_ok:
            if key in by_key:
                mark_dup(row, by_key[key])
                continue
            by_key[key] = row

    active = [r for r in rows if not r.is_duplicate and r.id is not None]
    for i, a in enumerate(active):
        for b in active[i + 1 :]:
            if a.price and b.price and abs(a.price - b.price) < 500:
                if similarity(_norm_title(a.title), _norm_title(b.title)) > 0.88:
                    # keep lower id as parent
                    parent, child = (a, b) if (a.id and b.id and a.id < b.id) else (b, a)
                    mark_dup(child, parent)

    session.commit()
    return marked
