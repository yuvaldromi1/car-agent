from __future__ import annotations

import httpx

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.config import settings
from backend.database import get_session
from backend.models import ManualSearchUrl, SourceConfig
from backend.schemas import SourceConfigRead, SourceConfigUpdate, SourcePostBody
from backend.services.search_agent import ensure_source_configs

router = APIRouter(prefix="/sources", tags=["sources"])


def _read(sc: SourceConfig) -> SourceConfigRead:
    return SourceConfigRead(
        id=sc.id,
        name=sc.name,
        source_type=sc.source_type,
        enabled=sc.enabled,
        legal_mode=sc.legal_mode,
        base_url=sc.base_url,
        search_instructions=sc.search_instructions,
        parser_available=sc.parser_available,
        notes=sc.notes,
        last_searched_at=sc.last_searched_at,
        last_result_count=sc.last_result_count,
    )


@router.get("", response_model=list[SourceConfigRead])
def list_sources(session: Session = Depends(get_session)):
    ensure_source_configs(session)
    rows = list(session.exec(select(SourceConfig)))
    return [_read(r) for r in rows]


@router.post("", response_model=dict)
def post_source(body: SourcePostBody, session: Session = Depends(get_session)):
    ensure_source_configs(session)
    if body.manual_url:
        ex = session.exec(select(ManualSearchUrl).where(ManualSearchUrl.url == body.manual_url)).first()
        if ex:
            raise HTTPException(status_code=400, detail="הקישור כבר קיים")
        session.add(ManualSearchUrl(url=body.manual_url, label=body.manual_label or ""))
        session.commit()
        return {"ok": True, "message_he": "הקישור נשמר לחיפוש ידני"}
    if body.id and body.name:
        if session.get(SourceConfig, body.id):
            raise HTTPException(status_code=400, detail="מקור עם מזהה זה כבר קיים")
        session.add(
            SourceConfig(
                id=body.id,
                name=body.name,
                source_type=body.source_type or "unknown",
                legal_mode=body.legal_mode or "manual",
                base_url=body.base_url or "",
                search_instructions=body.search_instructions or "",
                parser_available=bool(body.parser_available),
                notes=body.notes or "",
                enabled=body.enabled if body.enabled is not None else True,
            )
        )
        session.commit()
        return {"ok": True, "message_he": "מקור חדש נוסף"}
    raise HTTPException(status_code=400, detail="יש לספק manual_url או id ושם למקור")


@router.put("/{source_id}", response_model=SourceConfigRead)
def put_source(source_id: str, body: SourceConfigUpdate, session: Session = Depends(get_session)):
    sc = session.get(SourceConfig, source_id)
    if not sc:
        raise HTTPException(status_code=404, detail="מקור לא נמצא")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(sc, k, v)
    session.add(sc)
    session.commit()
    session.refresh(sc)
    return _read(sc)


@router.post("/{source_id}/test", response_model=dict)
def test_source(source_id: str, session: Session = Depends(get_session)):
    ensure_source_configs(session)
    sc = session.get(SourceConfig, source_id)
    if not sc:
        raise HTTPException(status_code=404, detail="מקור לא נמצא")
    if source_id == "google_cse":
        if not settings.google_api_key or not settings.google_cse_id:
            return {"ok": False, "message_he": "חסרים מפתח API או מזהה מנוע חיפוש (CSE)"}
        try:
            with httpx.Client(timeout=10.0) as client:
                r = client.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params={
                        "key": settings.google_api_key,
                        "cx": settings.google_cse_id,
                        "q": "רכב משפחתי חיפה",
                        "num": 1,
                    },
                )
                r.raise_for_status()
            return {"ok": True, "message_he": "חיבור ל-Google CSE תקין"}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "message_he": f"בדיקה נכשלה: {e}"}
    if sc.base_url and sc.base_url.startswith("http"):
        try:
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                r = client.head(sc.base_url)
                if r.status_code >= 400:
                    return {"ok": False, "message_he": f"קוד תשובה {r.status_code}"}
            return {"ok": True, "message_he": "כתובת הבסיס נגישה"}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "message_he": f"בדיקה נכשלה: {e}"}
    return {"ok": True, "message_he": "אין בדיקת רשת למקור זה (מצב ידני/קישור)"}
