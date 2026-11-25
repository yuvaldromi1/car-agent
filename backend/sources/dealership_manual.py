"""Emit dealership home links for manual follow-up — no scraping."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import select

from backend.models import Dealership, SearchProfile
from backend.schemas import SearchResultDTO
from backend.sources.base import SourceAdapter


class DealershipManualSource(SourceAdapter):
    id = "dealership_manual"
    name = "סוכנויות (ידני)"

    @property
    def legal_mode(self) -> str:
        return "manual"

    def search(self, session, profile: SearchProfile, extra_urls: list[str] | None = None) -> list[SearchResultDTO]:
        dealers = list(session.exec(select(Dealership)))
        out: list[SearchResultDTO] = []
        for d in dealers:
            if not d.website:
                continue
            out.append(
                SearchResultDTO(
                    title=f"{d.name} — אתר",
                    url=d.website if d.website.startswith("http") else f"https://{d.website}",
                    snippet=f"סוכנות ב{d.city or 'לא צוין'}. בדיקה ידנית מותרת דרך הדפדפן.",
                    source_name=self.name,
                    found_at=datetime.utcnow(),
                    raw_text=d.notes or "",
                )
            )
        return out
