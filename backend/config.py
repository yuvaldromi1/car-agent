from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven settings. Create a `.env` in the project root for local runs."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(default="sqlite:///./car_agent.db", description="SQLAlchemy database URL (SQLite default).")
    google_cse_id: str | None = Field(
        default=None,
        description="Google Programmable Search Engine ID (query param `cx`). Without it, google_cse returns no results.",
    )
    google_api_key: str | None = Field(
        default=None,
        description="Google API key for Custom Search JSON API. Without it, google_cse returns no results.",
    )
    nominatim_user_agent: str = Field(
        default="CarAgentKiryatTivon/1.0 (contact: local-dev)",
        description="Required User-Agent when GEOCODING_ENABLED=true (Nominatim policy).",
    )
    geocoding_enabled: bool = Field(default=False, description="If true, resolve unknown locations via Nominatim (respect usage policy).")
    reliability_profiles_path: Path = Field(
        default=Path(__file__).resolve().parent / "reliability_profiles.json",
        description="JSON file with model reliability hints (not absolute truth).",
    )


settings = Settings()
