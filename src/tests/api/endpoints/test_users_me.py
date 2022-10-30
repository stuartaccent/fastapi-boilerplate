import json

import pytest

from app.api.schemas import UserRead


@pytest.mark.asyncio
async def test_get(client, user, login_token):
    headers = {"Authorization": f"bearer {login_token}"}
    response = await client.get("/users/me", headers=headers)
    assert response.status_code == 200

    expected = UserRead.from_orm(user).json()
    assert response.json() == json.loads(expected)
