import contextlib
from asyncio import run as aiorun

import typer
from sqlalchemy import text

from app.api.schemas.user import UserCreate
from app.database.engine import engine
from app.database.session import get_session
from app.database.tables import AccessToken
from app.users import get_user_db, get_user_manager

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
    get_user_db_ctx = contextlib.asynccontextmanager(get_user_db)
    get_user_manager_ctx = contextlib.asynccontextmanager(get_user_manager)
    async with get_session_ctx() as db_session:
        async with get_user_db_ctx(db_session) as user_db:
            async with get_user_manager_ctx(user_db) as user_manager:
                user = await user_manager.create(
                    UserCreate(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        password=password,
                    )
                )
                return await user_db.update(
                    user,
                    {
                        "is_superuser": is_superuser,
                        "is_verified": is_verified,
                    },
                )


async def remove_tokens():
    async with engine.begin() as conn:
        tbl = AccessToken.__tablename__
        statement = text(f"truncate table {tbl};")
        await conn.execute(statement)


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


@app.command()
def remove_access_tokens():
    coro = remove_tokens()
    aiorun(coro)
    print("Completed")


if __name__ == "__main__":
    app()
