from typing import List, Optional

from pydantic import BaseSettings, HttpUrl


class Settings(BaseSettings):
    allow_origins: List[str] = ["*"]
    allowed_hosts: List[str] = ["*"]
    sentry_dsn: Optional[HttpUrl] = None


settings = Settings()
