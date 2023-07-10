from typing import List, Optional

from pydantic import HttpUrl, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    allow_origins: List[str] = ["*"]
    allowed_hosts: List[str] = ["*"]
    auth_host: str = "auth"
    auth_port: int = 50051
    email_host: str = "email"
    email_port: int = 50051
    database_url: PostgresDsn
    email_from_address: str
    sentry_dsn: Optional[HttpUrl] = None


settings = Settings()
