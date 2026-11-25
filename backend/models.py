from __future__ import annotations

import json
from datetime import date, datetime
from enum import Enum
from typing import Any

from sqlalchemy import Column, Index, Text
from sqlmodel import Field, SQLModel


class SourceType(str, Enum):
    private_market = "private_market"
    dealership = "dealership"
    trade_in = "trade_in"
    manual = "manual"
    csv = "csv"
    unknown = "unknown"


class FuelType(str, Enum):
    petrol = "petrol"
    hybrid = "hybrid"
    diesel = "diesel"
    electric = "electric"
    plugin_hybrid = "plugin_hybrid"
    unknown = "unknown"


class ListingStatus(str, Enum):
    new = "new"
    checked = "checked"
    contacted = "contacted"
    rejected = "rejected"
    favorite = "favorite"
    scheduled_inspection = "scheduled_inspection"


class Recommendation(str, Enum):
    worth_checking = "כדאי לבדוק"
    possible = "אפשרי"
    caution = "להיזהר"
    not_recommended = "לא מומלץ"


class LegalMode(str, Enum):
    api = "api"
    search_url = "search_url"
    manual = "manual"
    csv = "csv"


class RunStatus(str, Enum):
    pending = "pending"
    running = "running"
    done = "done"
    error = "error"


class CarListing(SQLModel, table=True):
    __table_args__ = (
        Index("ix_listing_source_url", "source_url"),
        Index("ix_listing_plate", "license_plate"),
        Index("ix_listing_dedupe", "make", "model", "year", "price", "mileage"),
    )

    id: int | None = Field(default=None, primary_key=True)
    source_name: str = Field(index=True)
    source_type: str = Field(default=SourceType.unknown.value, index=True)
    source_url: str = Field(unique=True)
    external_id: str | None = None
    title: str
    make: str = ""
    model: str = ""
    trim: str | None = None
    year: int | None = None
    price: float | None = None
    mileage: int | None = None
    fuel_type: str = Field(default=FuelType.unknown.value)
    transmission: str = ""
    engine_size: str | None = None
    ownership_type: str = "unknown"
    previous_owners: int | None = None
    seller_type: str = "unknown"
    seller_name: str | None = None
    seller_phone: str | None = None
    location_text: str = ""
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance_from_kiryat_tivon_km: float | None = None
    location_unknown: bool = Field(default=False)
    description: str = ""
    image_urls: str = Field(default="[]", sa_column=Column(Text))  # JSON array as string
    date_found: datetime = Field(default_factory=datetime.utcnow)
    date_updated: datetime = Field(default_factory=datetime.utcnow)
    license_plate: str | None = None
    test_valid_until: date | None = None
    notes: str = ""
    status: str = Field(default=ListingStatus.new.value, index=True)
    incomplete: bool = Field(default=False)
    beyond_radius: bool = Field(default=False)
    is_duplicate: bool = Field(default=False, index=True)
    duplicate_of_id: int | None = Field(default=None, foreign_key="carlisting.id")


class CarEvaluation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    listing_id: int = Field(foreign_key="carlisting.id", unique=True, index=True)
    total_score: float = 0.0
    price_score: float = 0.0
    mileage_score: float = 0.0
    year_score: float = 0.0
    fuel_efficiency_score: float = 0.0
    reliability_score: float = 0.0
    location_score: float = 0.0
    seller_trust_score: float = 0.0
    risk_score: float = 0.0
    explanation_hebrew: str = ""
    red_flags: str = Field(default="[]", sa_column=Column(Text))
    recommendation: str = Recommendation.possible.value


class SearchProfile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = "ברירת מחדל"
    is_active: bool = Field(default=True, index=True)
    base_location_name: str = "קריית טבעון"
    base_latitude: float = 32.7142
    base_longitude: float = 35.1261
    radius_km: float = 30.0
    min_price: float = 35000.0
    max_price: float = 43000.0
    min_year: int = 2018
    max_year: int = 2026
    max_mileage_preferred: int = 110000
    max_mileage_absolute: int = 140000
    family_car_only: bool = True
    fuel_preference: str = "any"  # hybrid | petrol_small_engine | diesel_optional | any
    include_private_sellers: bool = True
    include_dealerships: bool = True
    include_trade_in: bool = True
    excluded_keywords: str = Field(default="[]", sa_column=Column(Text))
    preferred_models: str = Field(default="[]", sa_column=Column(Text))
    rejected_models: str = Field(default="[]", sa_column=Column(Text))


class SourceConfig(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    source_type: str = Field(default=SourceType.unknown.value)
    enabled: bool = Field(default=True)
    legal_mode: str = Field(default=LegalMode.manual.value)
    base_url: str = ""
    search_instructions: str = ""
    parser_available: bool = False
    notes: str = ""
    last_searched_at: datetime | None = None
    last_result_count: int = 0


class Dealership(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    website: str = ""
    phone: str = ""
    city: str = ""
    address: str = ""
    latitude: float | None = None
    longitude: float | None = None
    notes: str = ""
    trust_level: int = Field(default=3, ge=1, le=5)
    last_checked: datetime | None = None


class SearchRun(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    status: str = Field(default=RunStatus.pending.value, index=True)
    error_message_he: str | None = None
    profile_snapshot: str = Field(default="{}", sa_column=Column(Text))


class SearchRunSource(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="searchrun.id", index=True)
    source_id: str = Field(index=True)
    status: str = Field(default=RunStatus.pending.value)
    results_found: int = 0
    valid_listings: int = 0
    error_he: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class GeocodeCache(SQLModel, table=True):
    location_key: str = Field(primary_key=True)
    latitude: float
    longitude: float
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ManualSearchUrl(SQLModel, table=True):
    """User-saved URLs for manual_url adapter."""

    id: int | None = Field(default=None, primary_key=True)
    url: str = Field(unique=True)
    label: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)


def json_list_load(s: str) -> list[Any]:
    try:
        return json.loads(s) if s else []
    except json.JSONDecodeError:
        return []


def json_list_dump(data: list[Any]) -> str:
    return json.dumps(data, ensure_ascii=False)
