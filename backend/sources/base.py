from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from sqlmodel import Session

from backend.models import SearchProfile
from backend.schemas import SearchResultDTO


class SourceAdapter(ABC):
    id: str
    name: str

    @property
    def legal_mode(self) -> str:
        return "manual"

    @abstractmethod
    def search(self, session: Session, profile: SearchProfile, extra_urls: list[str] | None = None) -> list[SearchResultDTO]:
        raise NotImplementedError
