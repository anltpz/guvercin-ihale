from decimal import Decimal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Uygulama ayarları — .env dosyasından yüklenir."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/guvercin"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me"
    PAYMENT_PROVIDER: str = "stub"
    CORS_ORIGINS: str = "http://localhost:8000"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


settings = Settings()

# İhale sabitleri
AUCTION_DURATION_SECONDS: int = 120
EXTENSION_THRESHOLD: int = 10
EXTENSION_SECONDS: int = 10
MIN_BID_INCREMENT: Decimal = Decimal("50")

# WebSocket hata kodları
WS_ERROR_CODES: dict[str, str] = {
    "BID_TOO_LOW": "BID_TOO_LOW",
    "AUCTION_ENDED": "AUCTION_ENDED",
    "FORBIDDEN_BID": "FORBIDDEN_BID",
    "INVALID_TOKEN": "INVALID_TOKEN",
    "INVALID_MESSAGE": "INVALID_MESSAGE",
}
