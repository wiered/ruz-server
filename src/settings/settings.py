from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT / ".env"),   # ЯВНО указываем .env
        env_file_encoding="utf-8",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    valid_api_key: str
    postgresql_uri: str
    logging_level: str
    logging_format: str
    host: str = "0.0.0.0"
    port: int = 2201
    reload: bool = False
    workers: int = 1
    log_level: str = "info"
    env: str = "prod"

settings = Settings()  # бросит ValidationError, если ключа нет
print(settings.postgresql_uri)
