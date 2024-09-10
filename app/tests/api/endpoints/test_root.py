import pytest


@pytest.mark.anyio
async def test_get(client_unauthenticated):
    response = await client_unauthenticated.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "hunky dory"}
