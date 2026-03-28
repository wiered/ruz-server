from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# TODO(refactor): replace fixed parents index with robust repo-root discovery
# (e.g., walk parents until pyproject.toml is found) after src-layout migration stabilizes.
ROOT = Path(__file__).resolve().parents[3]

from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    """
    Settings class for Ruz Server configuration.

    This class uses Pydantic BaseSettings for loading environment variables
    and provides configuration for application settings such as API keys,
    database URIs, logging, host/port, refresh schedule, and environment type.

    Args:
        valid_api_key (str): API key for authentication.
        postgresql_uri (str): URI for connecting to the PostgreSQL database.
        logging_level (str): Logging level for the application.
        logging_format (str): Format for log messages.
        host (str, optional): Host address to bind the server. Defaults to "0.0.0.0".
        port (int, optional): Port number for the server. Defaults to 2201.
        reload (bool, optional): Enable hot-reload for development. Defaults to False.
        workers (int, optional): Number of worker processes for server. Defaults to 1.
        log_level (str, optional): Log level for Uvicorn server. Defaults to "info".
        env (str, optional): Application environment type (e.g., "prod"). Defaults to "prod".
        doupdate (bool, optional): Whether to update on startup. Defaults to False.
        refresh_hour (int, optional): Hour of day for data refresh. Defaults to 2.
        refresh_minute (int, optional): Minute of the hour for data refresh. Defaults to 0.
        refresh_timezone (str, optional): Timezone for scheduler. Defaults to "Europe/Moscow".
        refresh_lock_file (str, optional): Path to the refresh lock file.

    Returns:
        Settings: An instance of the application settings.

    Raises:
        ValidationError: If required environment variables are missing or invalid.
    """
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
    doupdate: bool = Field(default=False, alias="DOUPDATE")
    refresh_hour: int = 2
    refresh_minute: int = 0
    refresh_timezone: str = "Europe/Moscow"
    refresh_lock_file: str = str(ROOT / "logs" / "refresh.lock")

settings = Settings()
