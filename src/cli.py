import contextlib
from asyncio import run as aiorun

import typer
from accentdatabase.engine import engine
from accentdatabase.session import get_session
from sqlalchemy import text

from app.api.schemas import UserCreate
from app.database.tables import AccessToken
from app.users import get_user_db, get_user_manager

app = typer.Typer()


async def add_user(
    email: str,
    first_name: str,
    last_name: str,
    password: str,
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
                user.is_superuser = is_superuser
                user.is_verified = True
                db_session.add(user)
                await db_session.commit()
                return user


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
):
    coro = add_user(email, first_name, last_name, password, False)
    user = aiorun(coro)
    print(f"Created: {user.email}")


@app.command()
def create_super_user(
    email: str,
    first_name: str,
    last_name: str,
    password: str,
):
    coro = add_user(email, first_name, last_name, password, True)
    user = aiorun(coro)
    print(f"Created: {user.email}")


@app.command()
def remove_access_tokens():
    aiorun(remove_tokens())
    print("Completed")


if __name__ == "__main__":
    app()
