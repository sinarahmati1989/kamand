"""
Application Settings
خواندن از .env با pydantic-settings
"""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """تنظیمات کل برنامه"""
    
    # ══════════ Database ══════════
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5432)
    DB_NAME: str = Field(default="device_manufacturing")
    DB_USER: str = Field(default="postgres")
    DB_PASSWORD: str = Field(default="")
    
    # ══════════ App ══════════
    APP_NAME: str = Field(default="Device Manufacturing System")
    APP_VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=True)
    SECRET_KEY: str = Field(default="change-me")
    
    # ══════════ Logging ══════════
    LOG_LEVEL: str = Field(default="DEBUG")
    LOG_DIR: str = Field(default="logs")
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    @property
    def DATABASE_URL(self) -> str:
        """URL اتصال به دیتابیس"""
        from urllib.parse import quote_plus
        pwd = quote_plus(self.DB_PASSWORD)
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{pwd}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    @property
    def LOG_PATH(self) -> Path:
        """مسیر پوشه لاگ"""
        path = BASE_DIR / self.LOG_DIR
        path.mkdir(exist_ok=True)
        return path


# Singleton
settings = Settings()