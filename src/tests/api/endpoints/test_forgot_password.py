import pytest


@pytest.mark.asyncio
async def test_sends_an_email(client, user, mocker):
    mocker.patch("fastapi_users.manager.generate_jwt", return_value="abc123")
    mock = mocker.patch("app.users.generate_email")
    response = await client.post(
        "/auth/forgot-password",
        json={"email": user.email},
    )
    assert response.status_code == 202
    mock.assert_called_once_with(
        to_address=user.email,
        subject="Reset your password",
        template_context={
            "host": "http://localhost",
            "site_name": "Example Inc.",
            "token": "abc123",
        },
        template_name_html="forgot_password.html",
        template_name_text="forgot_password.txt",
    )
