from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    # Убираем дефолт, чтобы явно видеть ошибку, если переменная не найдена
    database_url: str
    
    model_config = SettingsConfigDict(
        # config.py лежит в user_service/app/
        # .parent -> user_service/app/
        # .parents[1] -> user_service/
        # .parents[2] -> TestsTask/ (корень проекта)
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

settings = Settings()