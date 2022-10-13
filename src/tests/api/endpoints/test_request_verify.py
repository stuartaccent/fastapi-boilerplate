import pytest

pytestmark = pytest.mark.asyncio


async def test_sends_an_email(client, user, db_session, mocker):
    user.is_verified = False
    db_session.add(user)
    await db_session.commit()

    mock = mocker.patch("app.users.generate_email")
    response = await client.post(
        "/auth/request-verify-token", json={"email": user.email}
    )
    assert response.status_code == 202
    mock.assert_called_once()
