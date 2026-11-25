from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import get_session
from backend.models import Dealership
from backend.schemas import DealershipCreate, DealershipRead, DealershipUpdate

router = APIRouter(prefix="/dealerships", tags=["dealerships"])


def _read(d: Dealership) -> DealershipRead:
    return DealershipRead(
        id=d.id or 0,
        name=d.name,
        website=d.website,
        phone=d.phone,
        city=d.city,
        address=d.address,
        latitude=d.latitude,
        longitude=d.longitude,
        notes=d.notes,
        trust_level=d.trust_level,
        last_checked=d.last_checked,
    )


@router.get("", response_model=list[DealershipRead])
def list_dealerships(session: Session = Depends(get_session)):
    rows = list(session.exec(select(Dealership)))
    return [_read(r) for r in rows]


@router.post("", response_model=DealershipRead)
def create_dealership(body: DealershipCreate, session: Session = Depends(get_session)):
    d = Dealership(**body.model_dump())
    session.add(d)
    session.commit()
    session.refresh(d)
    return _read(d)


@router.put("/{dealership_id}", response_model=DealershipRead)
def update_dealership(dealership_id: int, body: DealershipUpdate, session: Session = Depends(get_session)):
    d = session.get(Dealership, dealership_id)
    if not d:
        raise HTTPException(status_code=404, detail="סוכנות לא נמצאה")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(d, k, v)
    session.add(d)
    session.commit()
    session.refresh(d)
    return _read(d)


@router.delete("/{dealership_id}")
def delete_dealership(dealership_id: int, session: Session = Depends(get_session)):
    d = session.get(Dealership, dealership_id)
    if not d:
        raise HTTPException(status_code=404, detail="סוכנות לא נמצאה")
    session.delete(d)
    session.commit()
    return {"ok": True}
