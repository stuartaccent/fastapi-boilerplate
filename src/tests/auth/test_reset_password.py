import pytest
from grpc import StatusCode
from grpc.aio import AioRpcError, Metadata

from app.config import settings
from protos import auth_pb2
from tests.mocks import MockAuthClient


async def _run_reset_password_test(mocker, client, response_callback):
    mocked_client = MockAuthClient()
    mocker.patch("app.auth.routes.grpc_clients", {"auth": mocked_client})

    mocked_client.ResetPassword = mocker.AsyncMock(side_effect=response_callback)

    request_data = {"token": "reset-token", "password": "password"}
    response = await client.post("/auth/reset-password", json=request_data)

    expected_request = auth_pb2.ResetPasswordRequest(**request_data)
    mocked_client.ResetPassword.assert_called_once_with(
        expected_request,
        timeout=settings.grpc_timeout,
    )

    return response


@pytest.mark.anyio
async def test_reset_password_mocked_success(mocker, client_unauthenticated):
    grpc_response = auth_pb2.Empty()

    async def response_callback(*args, **kwargs):
        assert kwargs["timeout"] == 5
        return grpc_response

    response = await _run_reset_password_test(
        mocker, client_unauthenticated, response_callback
    )

    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.anyio
async def test_reset_password_mocked_error(mocker, client_unauthenticated):
    async def create_rpc_error(*args, **kwargs):
        raise AioRpcError(
            code=StatusCode.INVALID_ARGUMENT,
            initial_metadata=Metadata(),
            trailing_metadata=Metadata(),
            details="invalid token",
        )

    response = await _run_reset_password_test(
        mocker, client_unauthenticated, create_rpc_error
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "invalid token"}
