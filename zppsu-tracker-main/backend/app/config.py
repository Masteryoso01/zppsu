from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    store: str = "memory"  # "sheets" | "memory"
    apps_script_url: str = ""
    apps_script_secret: str = ""
    sheets_refresh_seconds: int = 60  # how often the cache re-reads the sheet (picks up manual edits); 0 = never

    jwt_secret: str = "dev-only-change-me"
    jwt_expire_hours: int = 12
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    timezone: str = "Asia/Manila"
    late_after: str = "08:15"

    superadmin_email: str = "sysadmin@geotrack.io"
    superadmin_password: str = "change-me-now"

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
