from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from backend.core.path_conf import ENV_FILE_PATH


class Settings(BaseSettings):
    """Global settings.

    Every value the backend reads from the environment is declared here; no module
    calls ``os.getenv`` directly. Missing required values fail at import time rather
    than at the first request that happens to need them.
    """

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=True,
    )

    # Environment
    ENVIRONMENT: Literal['dev', 'prod'] = 'dev'
    PORT: int = 3001

    # FastAPI
    FASTAPI_API_V1_PATH: str = '/api/v1'
    FASTAPI_TITLE: str = 'CareerBridge API'
    FASTAPI_DESCRIPTION: str = 'CareerBridge REST API'
    FASTAPI_DOCS_URL: str | None = '/docs'
    FASTAPI_REDOC_URL: str | None = '/redoc'
    FASTAPI_OPENAPI_URL: str | None = '/openapi.json'
    FASTAPI_SERVE_FRONTEND: bool = True

    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str = ''
    SUPABASE_JWKS_TTL_SECONDS: int = 3600

    # Direct Postgres connection, used only by backend/scripts/migrate.py
    DATABASE_URL: str = ''

    # Redis
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ''
    REDIS_DATABASE: int = 0
    REDIS_TIMEOUT: int = 5
    REDIS_MAX_CONNECTIONS: int = 20
    REDIS_POOL_TIMEOUT: int = 5
    REDIS_KEY_PREFIX: str = 'cb'

    # Cache TTLs (seconds)
    CACHE_BAN_TTL: int = 60
    CACHE_JWKS_TTL: int = 3600

    # CORS
    CORS_ALLOWED_ORIGINS: list[str] = Field(default_factory=lambda: ['http://localhost:5173'])
    CORS_EXPOSE_HEADERS: list[str] = Field(default_factory=lambda: ['X-Request-ID'])

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = '100/minute'
    RATE_LIMIT_SUBMISSION: str = '5/hour'
    RATE_LIMIT_FLAG: str = '10/hour'
    # Empty means an in-process store: correct only for a single worker.
    # Set to settings.REDIS_URL (or any limits-supported URI) in deployment.
    RATE_LIMIT_STORAGE_URI: str = ''

    # Pagination
    PAGINATION_DEFAULT_SIZE: int = 20
    PAGINATION_MAX_SIZE: int = 50

    # Email (Resend SMTP)
    SMTP_HOST: str = 'smtp.resend.com'
    SMTP_PORT: int = 465
    SMTP_USER: str = 'resend'
    SMTP_PASS: str = ''
    EMAIL_FROM: str = 'noreply@careerbridge.pk'

    # Resume analyzer
    GEMINI_API_KEY: str = ''
    GEMINI_MODEL: str = 'gemini-2.0-flash'

    # Logging
    LOG_LEVEL: str = 'INFO'
    LOG_TO_FILE: bool = False
    LOG_FILE_NAME: str = 'careerbridge.log'

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        """Connection string, used by slowapi's Redis storage backend."""
        auth = f':{self.REDIS_PASSWORD}@' if self.REDIS_PASSWORD else ''
        return f'redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DATABASE}'

    @computed_field
    @property
    def SUPABASE_JWKS_URL(self) -> str:
        return f'{self.SUPABASE_URL.rstrip("/")}/auth/v1/.well-known/jwks.json'


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings: Settings = get_settings()
