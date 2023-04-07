import pytest


@pytest.mark.asyncio
async def test_get(client_unauthenticated):
    response = client_unauthenticated.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "hunky dory"}
