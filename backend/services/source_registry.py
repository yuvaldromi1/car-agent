from __future__ import annotations

from backend.sources.base import SourceAdapter
from backend.sources.carwiz_search_url import CarwizSearchUrlSource
from backend.sources.dealership_manual import DealershipManualSource
from backend.sources.google_search import GoogleProgrammableSearchSource
from backend.sources.manual_url import ManualUrlSource
from backend.sources.yad2_search_url import Yad2SearchUrlSource

_ADAPTERS: dict[str, SourceAdapter] = {
    GoogleProgrammableSearchSource.id: GoogleProgrammableSearchSource(),
    Yad2SearchUrlSource.id: Yad2SearchUrlSource(),
    CarwizSearchUrlSource.id: CarwizSearchUrlSource(),
    ManualUrlSource.id: ManualUrlSource(),
    DealershipManualSource.id: DealershipManualSource(),
}


def all_adapters() -> list[SourceAdapter]:
    return list(_ADAPTERS.values())


def get_adapter(source_id: str) -> SourceAdapter | None:
    return _ADAPTERS.get(source_id)
