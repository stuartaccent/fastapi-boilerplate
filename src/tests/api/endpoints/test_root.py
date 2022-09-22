import pytest
from starlette import status

from app.database.tables import User

pytestmark = pytest.mark.asyncio


async def test_no_token_no_access(client):
    response = await client.get("/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_inactive_no_access(client, user, db, login_token):
    await db.update(User, user.id, {"is_active": False})
    headers = {"Authorization": f"bearer {login_token}"}
    response = await client.get("/", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_ok(client, login_token):
    headers = {"Authorization": f"bearer {login_token}"}
    response = await client.get("/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
