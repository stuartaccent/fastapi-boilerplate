from typing import List, Optional

from pydantic import BaseSettings, HttpUrl, SecretStr


class Settings(BaseSettings):
    access_token_expire_seconds: int = 60 * 60
    allow_origins: List[str] = ["*"]
    allowed_hosts: List[str] = ["*"]
    email_from_address: str
    # to get a string like this run: openssl rand -hex 32
    secret_key: SecretStr
    sentry_dsn: Optional[HttpUrl] = None


settings = Settings()
