import pytest


@pytest.mark.asyncio
async def test_sends_an_email(client, user, db_session, mocker):
    user.is_verified = False
    db_session.add(user)
    await db_session.commit()

    mocker.patch(
        "app.authentication.routes.auth.create_jwt",
        return_value="abc123",
    )
    mock = mocker.patch("app.authentication.routes.auth.generate_email")
    response = await client.post(
        "/auth/verify-request",
        json={"email": user.email},
    )
    assert response.status_code == 202
    mock.assert_called_once_with(
        to_address=user.email,
        subject="Complete your registration",
        template_context={
            "token": "abc123",
            "host": "http://localhost",
            "site_name": "Example Inc.",
        },
        template_name_text="verify_request.txt",
        template_name_html="verify_request.html",
    )
