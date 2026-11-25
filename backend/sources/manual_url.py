"""Manual URLs stored in DB + optional per-run extras."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import select

from backend.models import ManualSearchUrl, SearchProfile
from backend.schemas import SearchResultDTO
from backend.sources.base import SourceAdapter


class ManualUrlSource(SourceAdapter):
    id = "manual_url"
    name = "קישורים ידניים"

    @property
    def legal_mode(self) -> str:
        return "manual"

    def search(self, session, profile: SearchProfile, extra_urls: list[str] | None = None) -> list[SearchResultDTO]:
        rows = list(session.exec(select(ManualSearchUrl)))
        urls = [r.url for r in rows]
        if extra_urls:
            urls.extend(extra_urls)
        seen: set[str] = set()
        out: list[SearchResultDTO] = []
        for u in urls:
            if u in seen:
                continue
            seen.add(u)
            out.append(
                SearchResultDTO(
                    title=f"קישור שמור: {u}",
                    url=u,
                    snippet="ייבוא ידני — יש להשלים פרטים מהאתר או לעדכן את הרישום.",
                    source_name=self.name,
                    found_at=datetime.utcnow(),
                    raw_text=u,
                )
            )
        return out
