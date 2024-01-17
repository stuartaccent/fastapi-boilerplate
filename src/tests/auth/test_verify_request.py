import pytest
from grpc import StatusCode
from grpc.aio import AioRpcError, Metadata

from app.config import settings
from protos import auth_pb2
from tests.mocks import MockAuthClient


async def _run_verify_request_test(mocker, client, response_callback):
    mocked_client = MockAuthClient()
    mocker.patch("app.auth.routes.grpc_clients", {"auth": mocked_client})

    mocked_client.VerifyUserToken = mocker.AsyncMock(side_effect=response_callback)

    request_data = {"email": "test@example.com"}
    response = await client.post("/auth/verify-request", json=request_data)

    expected_request = auth_pb2.VerifyUserTokenRequest(**request_data)
    mocked_client.VerifyUserToken.assert_called_once_with(
        expected_request,
        timeout=settings.grpc_timeout,
    )

    return response


@pytest.mark.anyio
async def test_verify_request_mocked_success(mocker, client_unauthenticated):
    mocked_mail = mocker.patch("app.auth.routes.send_email")

    grpc_response = auth_pb2.TokenWithEmail(
        token="verify-token",
        email="test@example.com",
        first_name="Some",
        last_name="One",
    )

    async def response_callback(*args, **kwargs):
        assert kwargs["timeout"] == 5
        return grpc_response

    response = await _run_verify_request_test(
        mocker, client_unauthenticated, response_callback
    )

    assert response.status_code == 202
    assert response.json() is None

    mocked_mail.assert_called_once_with(
        to_address="test@example.com",
        subject="Complete your registration",
        template_context={
            "token": "verify-token",
            "host": settings.site_url,
            "site_name": settings.site_name,
        },
        template_name_text="verify_request.txt",
        template_name_html="verify_request.html",
    )


@pytest.mark.anyio
async def test_verify_request_mocked_error(mocker, client_unauthenticated):
    mocked_mail = mocker.patch("app.auth.routes.send_email")

    async def create_rpc_error(*args, **kwargs):
        raise AioRpcError(
            code=StatusCode.FAILED_PRECONDITION,
            initial_metadata=Metadata(),
            trailing_metadata=Metadata(),
            details="user is already verified",
        )

    response = await _run_verify_request_test(
        mocker, client_unauthenticated, create_rpc_error
    )

    assert response.status_code == 202
    assert response.json() is None

    mocked_mail.assert_not_called()
