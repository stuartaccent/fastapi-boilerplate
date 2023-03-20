import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from accentdatabase.services import BaseCRUDService
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.authentication.password import hash_password
from app.authentication.schemas import UserCreate, UserUpdate, UserUpdateFull
from app.database.tables import AccessToken, User


class UserService(BaseCRUDService[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def create(
        self,
        obj: UserCreate,
    ) -> User:
        user = User(
            **obj.dict(exclude={"password"}),
            hashed_password=hash_password(obj.password),
        )
        await self._commit(user)
        return user

    async def update(
        self,
        ident: UUID,
        obj: UserUpdate | UserUpdateFull,
    ) -> User:
        user = await self.get(ident, raise_not_found=True)
        for k, v in obj.dict(exclude_unset=True, exclude={"password"}).items():
            setattr(user, k, v)
        if obj.password:
            await self.set_password(user, obj.password)
        else:
            await self._commit(user)
        return user

    async def get_user_by_email(
        self,
        email: str,
    ) -> User | None:
        statement = select(User).where(func.lower(User.email) == func.lower(email))
        return await self.session.scalar(statement)

    async def get_user_by_token(
        self,
        token: str,
    ) -> User | None:
        now = datetime.now(timezone.utc)
        statement = (
            select(AccessToken)
            .where(AccessToken.token == token, AccessToken.expires_at >= now)
            .options(joinedload(AccessToken.user))
        )
        token = await self.session.scalar(statement)
        return token.user if token else None

    async def set_password(
        self,
        user: User,
        password: str,
    ) -> None:
        user.hashed_password = hash_password(password)
        await self._commit(user)

    async def create_token(
        self,
        user: User,
        minutes_to_expire: int,
    ) -> str:
        now = datetime.now(timezone.utc)
        expires_delta = timedelta(minutes=minutes_to_expire)
        expires_at = now + expires_delta
        access_token = AccessToken(
            token=secrets.token_urlsafe(64),
            user_id=user.id,
            created_at=now,
            expires_at=expires_at,
        )
        await self._commit(access_token)
        return access_token.token

    async def remove_token(
        self,
        token: str,
    ):
        if access_token := await self.session.get(AccessToken, token):
            await self.session.delete(access_token)
            await self.session.commit()

    async def _commit(self, instance) -> None:
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
