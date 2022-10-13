import pytest

pytestmark = pytest.mark.asyncio


async def test_sends_an_email(client, user, mocker):
    mock = mocker.patch("app.users.generate_email")
    response = await client.post("/auth/forgot-password", json={"email": user.email})
    assert response.status_code == 202
    mock.assert_called_once()
