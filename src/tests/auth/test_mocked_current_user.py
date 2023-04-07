import pytest


@pytest.mark.asyncio
async def test_raise_unauthenticated(client_unauthenticated):
    response = client_unauthenticated.get("/users/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "INVALID_AUTH_CREDENTIALS"


@pytest.mark.asyncio
async def test_authenticated(client_authenticated):
    response = client_authenticated.get("/users/me")

    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
