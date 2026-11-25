from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class SearchResultDTO(BaseModel):
    title: str
    url: str
    snippet: str = ""
    source_name: str
    found_at: datetime = Field(default_factory=datetime.utcnow)
    possible_price: float | None = None
    possible_year: int | None = None
    possible_mileage: int | None = None
    possible_location: str | None = None
    raw_text: str = ""


class CarListingCreate(BaseModel):
    source_name: str = "ידני"
    source_type: str = "manual"
    source_url: str
    title: str
    make: str = ""
    model: str = ""
    trim: str | None = None
    year: int | None = None
    price: float | None = None
    mileage: int | None = None
    fuel_type: str = "unknown"
    transmission: str = ""
    engine_size: str | None = None
    ownership_type: str = "unknown"
    previous_owners: int | None = None
    seller_type: str = "private"
    seller_name: str | None = None
    seller_phone: str | None = None
    location_text: str = ""
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    description: str = ""
    image_urls: list[str] = Field(default_factory=list)
    license_plate: str | None = None
    test_valid_until: date | None = None
    notes: str = ""
    status: str = "new"


class CarListingUpdate(BaseModel):
    title: str | None = None
    make: str | None = None
    model: str | None = None
    trim: str | None = None
    year: int | None = None
    price: float | None = None
    mileage: int | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    engine_size: str | None = None
    ownership_type: str | None = None
    previous_owners: int | None = None
    seller_type: str | None = None
    seller_name: str | None = None
    seller_phone: str | None = None
    location_text: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    description: str | None = None
    image_urls: list[str] | None = None
    license_plate: str | None = None
    test_valid_until: date | None = None
    notes: str | None = None
    status: str | None = None


class CarEvaluationRead(BaseModel):
    total_score: float
    price_score: float
    mileage_score: float
    year_score: float
    fuel_efficiency_score: float
    reliability_score: float
    location_score: float
    seller_trust_score: float
    risk_score: float
    explanation_hebrew: str
    red_flags: list[str]
    recommendation: str


class CarListingRead(BaseModel):
    id: int
    source_name: str
    source_type: str
    source_url: str
    external_id: str | None
    title: str
    make: str
    model: str
    trim: str | None
    year: int | None
    price: float | None
    mileage: int | None
    fuel_type: str
    transmission: str
    engine_size: str | None
    ownership_type: str
    previous_owners: int | None
    seller_type: str
    seller_name: str | None
    seller_phone: str | None
    location_text: str
    city: str | None
    latitude: float | None
    longitude: float | None
    distance_from_kiryat_tivon_km: float | None
    location_unknown: bool
    description: str
    image_urls: list[str]
    date_found: datetime
    date_updated: datetime
    license_plate: str | None
    test_valid_until: date | None
    notes: str
    status: str
    incomplete: bool
    beyond_radius: bool
    is_duplicate: bool
    duplicate_of_id: int | None
    evaluation: CarEvaluationRead | None = None

    @staticmethod
    def from_orm_listing(
        listing: Any,
        evaluation: Any | None,
        image_urls: list[str],
        red_flags: list[str],
    ) -> CarListingRead:
        ev_read = None
        if evaluation:
            ev_read = CarEvaluationRead(
                total_score=evaluation.total_score,
                price_score=evaluation.price_score,
                mileage_score=evaluation.mileage_score,
                year_score=evaluation.year_score,
                fuel_efficiency_score=evaluation.fuel_efficiency_score,
                reliability_score=evaluation.reliability_score,
                location_score=evaluation.location_score,
                seller_trust_score=evaluation.seller_trust_score,
                risk_score=evaluation.risk_score,
                explanation_hebrew=evaluation.explanation_hebrew,
                red_flags=red_flags,
                recommendation=evaluation.recommendation,
            )
        return CarListingRead(
            id=listing.id,
            source_name=listing.source_name,
            source_type=listing.source_type,
            source_url=listing.source_url,
            external_id=listing.external_id,
            title=listing.title,
            make=listing.make,
            model=listing.model,
            trim=listing.trim,
            year=listing.year,
            price=listing.price,
            mileage=listing.mileage,
            fuel_type=listing.fuel_type,
            transmission=listing.transmission,
            engine_size=listing.engine_size,
            ownership_type=listing.ownership_type,
            previous_owners=listing.previous_owners,
            seller_type=listing.seller_type,
            seller_name=listing.seller_name,
            seller_phone=listing.seller_phone,
            location_text=listing.location_text,
            city=listing.city,
            latitude=listing.latitude,
            longitude=listing.longitude,
            distance_from_kiryat_tivon_km=listing.distance_from_kiryat_tivon_km,
            location_unknown=listing.location_unknown,
            description=listing.description,
            image_urls=image_urls,
            date_found=listing.date_found,
            date_updated=listing.date_updated,
            license_plate=listing.license_plate,
            test_valid_until=listing.test_valid_until,
            notes=listing.notes,
            status=listing.status,
            incomplete=listing.incomplete,
            beyond_radius=listing.beyond_radius,
            is_duplicate=listing.is_duplicate,
            duplicate_of_id=listing.duplicate_of_id,
            evaluation=ev_read,
        )


class SearchProfileRead(BaseModel):
    id: int
    name: str
    is_active: bool
    base_location_name: str
    base_latitude: float
    base_longitude: float
    radius_km: float
    min_price: float
    max_price: float
    min_year: int
    max_year: int
    max_mileage_preferred: int
    max_mileage_absolute: int
    family_car_only: bool
    fuel_preference: str
    include_private_sellers: bool
    include_dealerships: bool
    include_trade_in: bool
    excluded_keywords: list[str]
    preferred_models: list[str]
    rejected_models: list[str]


class SearchProfileUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None
    base_location_name: str | None = None
    base_latitude: float | None = None
    base_longitude: float | None = None
    radius_km: float | None = None
    min_price: float | None = None
    max_price: float | None = None
    min_year: int | None = None
    max_year: int | None = None
    max_mileage_preferred: int | None = None
    max_mileage_absolute: int | None = None
    family_car_only: bool | None = None
    fuel_preference: str | None = None
    include_private_sellers: bool | None = None
    include_dealerships: bool | None = None
    include_trade_in: bool | None = None
    excluded_keywords: list[str] | None = None
    preferred_models: list[str] | None = None
    rejected_models: list[str] | None = None


class SearchRunSourceRead(BaseModel):
    id: int
    source_id: str
    status: str
    results_found: int
    valid_listings: int
    error_he: str | None
    started_at: datetime | None
    completed_at: datetime | None


class SearchRunRead(BaseModel):
    id: int
    started_at: datetime
    completed_at: datetime | None
    status: str
    error_message_he: str | None
    sources: list[SearchRunSourceRead] = Field(default_factory=list)


class SourceConfigRead(BaseModel):
    id: str
    name: str
    source_type: str
    enabled: bool
    legal_mode: str
    base_url: str
    search_instructions: str
    parser_available: bool
    notes: str
    last_searched_at: datetime | None
    last_result_count: int


class SourceConfigUpdate(BaseModel):
    enabled: bool | None = None
    notes: str | None = None
    base_url: str | None = None
    search_instructions: str | None = None


class SourcePostBody(BaseModel):
    """POST /sources: either seed a manual URL or create a custom source row."""

    manual_url: str | None = None
    manual_label: str = ""
    id: str | None = None
    name: str | None = None
    source_type: str | None = None
    legal_mode: str | None = None
    base_url: str | None = None
    search_instructions: str | None = None
    parser_available: bool | None = None
    notes: str | None = None
    enabled: bool | None = True


class SourceConfigCreate(BaseModel):
    id: str
    name: str
    source_type: str = "unknown"
    legal_mode: str = "manual"
    base_url: str = ""
    search_instructions: str = ""
    parser_available: bool = False
    notes: str = ""
    enabled: bool = True


class DealershipCreate(BaseModel):
    name: str
    website: str = ""
    phone: str = ""
    city: str = ""
    address: str = ""
    latitude: float | None = None
    longitude: float | None = None
    notes: str = ""
    trust_level: int = 3


class DealershipUpdate(BaseModel):
    name: str | None = None
    website: str | None = None
    phone: str | None = None
    city: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    notes: str | None = None
    trust_level: int | None = None
    last_checked: datetime | None = None


class DealershipRead(BaseModel):
    id: int
    name: str
    website: str
    phone: str
    city: str
    address: str
    latitude: float | None
    longitude: float | None
    notes: str
    trust_level: int
    last_checked: datetime | None


class ListingDetailExtra(BaseModel):
    seller_questions: list[str]
    purchase_checklist: list[str]


class CarListingDetailRead(CarListingRead):
    seller_questions: list[str] = Field(default_factory=list)
    purchase_checklist: list[str] = Field(default_factory=list)


class ManualUrlCreate(BaseModel):
    url: str
    label: str = ""


class SearchRunCreateBody(BaseModel):
    """Optional body for POST /search/run — e.g. extra manual URLs for this run."""

    extra_manual_urls: list[str] = Field(default_factory=list)


def parse_image_urls(raw: str) -> list[str]:
    try:
        data = json.loads(raw) if raw else []
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def parse_red_flags(raw: str) -> list[str]:
    try:
        data = json.loads(raw) if raw else []
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []
