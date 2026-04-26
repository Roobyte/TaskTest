from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Literal


class Settings(BaseSettings):
    secret_key: str = Field(validation_alias=AliasChoices("AUTH_SECRET_KEY", "SECRET_KEY"))
    user_service_url: str = "http://localhost:8000"
    redis_host: str = "localhost"
    redis_port: int = 6379
    access_token_expire_minutes: int = 30
    session_cookie_name: str = "auth_session"
    session_cookie_secure: bool = False
    session_cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

settings = Settings()
