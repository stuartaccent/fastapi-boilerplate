from typing import Annotated

from accentdatabase.session import get_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.authentication.exceptions import Unauthorized
from app.authentication.oauth import oauth2_scheme
from app.authentication.services import UserService
from app.database.tables import User


async def get_user_service(
    session: AsyncSession = Depends(get_session),
) -> UserService:
    yield UserService(session)


GetUserService = Annotated[UserService, Depends(get_user_service)]


async def current_user(
    user_service: GetUserService,
    token: str = Depends(oauth2_scheme),
) -> User:
    if user := await user_service.get_user_by_token(token):
        return user
    raise Unauthorized("Could not validate credentials")


CurrentUser = Annotated[User, Depends(current_user)]


async def current_active_user(user: CurrentUser) -> User:
    if not user.is_active:
        raise Unauthorized("Could not validate credentials")
    return user


CurrentActiveUser = Annotated[User, Depends(current_active_user)]
