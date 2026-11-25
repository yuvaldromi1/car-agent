from __future__ import annotations

import json

from sqlalchemy import desc

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select

from backend.database import engine, get_session
from backend.models import RunStatus, SearchProfile, SearchRun, SearchRunSource, SourceConfig, json_list_dump, json_list_load
from backend.schemas import (
    SearchProfileRead,
    SearchProfileUpdate,
    SearchRunCreateBody,
    SearchRunRead,
    SearchRunSourceRead,
)
from backend.services.search_agent import ensure_source_configs, run_search_agent, _active_profile

router = APIRouter(prefix="/search", tags=["search"])


def _profile_read(p: SearchProfile) -> SearchProfileRead:
    return SearchProfileRead(
        id=p.id or 0,
        name=p.name,
        is_active=p.is_active,
        base_location_name=p.base_location_name,
        base_latitude=p.base_latitude,
        base_longitude=p.base_longitude,
        radius_km=p.radius_km,
        min_price=p.min_price,
        max_price=p.max_price,
        min_year=p.min_year,
        max_year=p.max_year,
        max_mileage_preferred=p.max_mileage_preferred,
        max_mileage_absolute=p.max_mileage_absolute,
        family_car_only=p.family_car_only,
        fuel_preference=p.fuel_preference,
        include_private_sellers=p.include_private_sellers,
        include_dealerships=p.include_dealerships,
        include_trade_in=p.include_trade_in,
        excluded_keywords=json_list_load(p.excluded_keywords),
        preferred_models=json_list_load(p.preferred_models),
        rejected_models=json_list_load(p.rejected_models),
    )


@router.get("/profile", response_model=SearchProfileRead)
def get_profile(session: Session = Depends(get_session)):
    p = _active_profile(session)
    return _profile_read(p)


@router.put("/profile", response_model=SearchProfileRead)
def put_profile(body: SearchProfileUpdate, session: Session = Depends(get_session)):
    p = _active_profile(session)
    data = body.model_dump(exclude_unset=True)
    if "excluded_keywords" in data and data["excluded_keywords"] is not None:
        p.excluded_keywords = json_list_dump(data.pop("excluded_keywords"))
    if "preferred_models" in data and data["preferred_models"] is not None:
        p.preferred_models = json_list_dump(data.pop("preferred_models"))
    if "rejected_models" in data and data["rejected_models"] is not None:
        p.rejected_models = json_list_dump(data.pop("rejected_models"))
    for k, v in data.items():
        setattr(p, k, v)
    session.add(p)
    session.commit()
    session.refresh(p)
    return _profile_read(p)


def _run_task(run_id: int, extras: list[str] | None) -> None:
    from sqlmodel import Session

    with Session(engine) as session:
        run_search_agent(session, run_id, extras)


@router.post("/run")
def post_run(
    background_tasks: BackgroundTasks,
    body: SearchRunCreateBody = SearchRunCreateBody(),
    session: Session = Depends(get_session),
):
    ensure_source_configs(session)
    profile = _active_profile(session)
    snapshot = _profile_read(profile).model_dump()
    run = SearchRun(
        status=RunStatus.pending.value,
        profile_snapshot=json.dumps(snapshot, ensure_ascii=False),
    )
    session.add(run)
    session.commit()
    session.refresh(run)

    for sc in list(session.exec(select(SourceConfig))):
        session.add(
            SearchRunSource(
                run_id=run.id,
                source_id=sc.id,
                status=RunStatus.pending.value,
            )
        )
    session.commit()
    extras = body.extra_manual_urls
    background_tasks.add_task(_run_task, run.id, extras or None)
    return {"run_id": run.id, "message_he": "החיפוש התחיל ברקע"}


def _run_read(session: Session, run: SearchRun) -> SearchRunRead:
    srcs = list(session.exec(select(SearchRunSource).where(SearchRunSource.run_id == run.id)))
    return SearchRunRead(
        id=run.id or 0,
        started_at=run.started_at,
        completed_at=run.completed_at,
        status=run.status,
        error_message_he=run.error_message_he,
        sources=[
            SearchRunSourceRead(
                id=s.id or 0,
                source_id=s.source_id,
                status=s.status,
                results_found=s.results_found,
                valid_listings=s.valid_listings,
                error_he=s.error_he,
                started_at=s.started_at,
                completed_at=s.completed_at,
            )
            for s in srcs
        ],
    )


@router.get("/runs", response_model=list[SearchRunRead])
def list_runs(session: Session = Depends(get_session), limit: int = 20):
    rows = list(session.exec(select(SearchRun).order_by(desc(SearchRun.id)).limit(limit)))
    return [_run_read(session, r) for r in rows]


@router.get("/runs/{run_id}", response_model=SearchRunRead)
def get_run(run_id: int, session: Session = Depends(get_session)):
    run = session.get(SearchRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="ריצת חיפוש לא נמצאה")
    return _run_read(session, run)
