from typing import List, Optional

from pydantic import BaseSettings, HttpUrl, SecretStr


class Settings(BaseSettings):
    access_token_expire_minutes: int = 60 * 8
    allow_origins: List[str] = ["*"]
    allowed_hosts: List[str] = ["*"]
    email_from_address: str
    reset_token_expire_minutes: int = 60
    # to get a string like this run: openssl rand -hex 32
    secret_key: SecretStr
    sentry_dsn: Optional[HttpUrl] = None
    verify_token_expire_minutes: int = 60


settings = Settings()
