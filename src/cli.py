import contextlib
from asyncio import run as aiorun

import typer
from accentdatabase.session import get_session

from app.authentication.dependencies import get_user_service
from app.authentication.schemas import UserCreate, UserUpdateFull

app = typer.Typer()


async def add_user(
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    is_verified: bool,
    is_superuser: bool,
):
    get_session_ctx = contextlib.asynccontextmanager(get_session)
    get_user_service_ctx = contextlib.asynccontextmanager(get_user_service)
    async with get_session_ctx() as db_session:
        async with get_user_service_ctx(db_session) as user_service:
            user = await user_service.create(
                UserCreate(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    password=password,
                )
            )
            return await user_service.update(
                user.id,
                UserUpdateFull(is_superuser=is_superuser, is_verified=is_verified),
            )


@app.command()
def create_user(
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    verified: bool = False,
    superuser: bool = False,
):
    coro = add_user(
        email,
        first_name,
        last_name,
        password,
        verified,
        superuser,
    )
    user = aiorun(coro)
    print(f"Created: {user.email}")


if __name__ == "__main__":
    app()
