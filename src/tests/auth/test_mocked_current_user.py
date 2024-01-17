import pytest


@pytest.mark.anyio
async def test_raise_unauthenticated(client_unauthenticated):
    response = await client_unauthenticated.get("/users/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"


@pytest.mark.anyio
async def test_authenticated(client_authenticated):
    response = await client_authenticated.get("/users/me")

    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
