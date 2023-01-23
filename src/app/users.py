import uuid
from typing import Any, Optional

from accentdatabase.session import get_session
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication.strategy import AccessTokenDatabase, DatabaseStrategy
from fastapi_users.authentication.transport.bearer import (
    BearerResponse as FBearerResponse,
)
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.password import PasswordHelper
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from app.config import settings
from app.database.tables import AccessToken, User
from app.notifications.email import generate_email


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.secret_key
    verification_token_secret = settings.secret_key

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
    ):
        print("on_after_register", user.id)

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ):
        await generate_email(
            to_address=user.email,
            subject="Reset your password",
            template_context={
                "token": token,
                "host": "http://localhost",
                "site_name": "Example Inc.",
            },
            template_name_text="forgot_password.txt",
            template_name_html="forgot_password.html",
        )

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ):
        await generate_email(
            to_address=user.email,
            subject="Complete your registration",
            template_context={
                "token": token,
                "host": "http://localhost",
                "site_name": "Example Inc.",
            },
            template_name_text="verify_request.txt",
            template_name_html="verify_request.html",
        )


password_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
password_helper = PasswordHelper(password_context)


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)


async def get_token_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db, password_helper)


class BearerResponse(FBearerResponse):
    expiry: int


class Transport(BearerTransport):
    async def get_login_response(self, token: str, response: Response) -> Any:
        return BearerResponse(
            access_token=token,
            token_type="bearer",
            expiry=settings.access_token_expire_seconds,
        )

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        return {
            status.HTTP_200_OK: {
                "model": BearerResponse,
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "some-token",
                            "token_type": "bearer",
                            "expiry": 3600,
                        }
                    }
                },
            },
        }


bearer_transport = Transport(tokenUrl="auth/token/login")


def get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessToken] = Depends(get_token_db),
) -> DatabaseStrategy:
    return DatabaseStrategy(
        access_token_db,
        lifetime_seconds=settings.access_token_expire_seconds,
    )


auth_backend = AuthenticationBackend(
    name="token",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
current_active_verified_user = fastapi_users.current_user(active=True, verified=True)
