import pytest
from starlette import status

pytestmark = pytest.mark.asyncio


async def test_ok(client):
    response = await client.get("/")
    assert response.status_code == status.HTTP_200_OK
