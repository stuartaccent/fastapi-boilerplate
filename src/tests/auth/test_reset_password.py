import pytest
from grpc import StatusCode
from grpc.aio import AioRpcError, Metadata
from starlette.testclient import TestClient

from app.main import app
from protos import auth_pb2
from tests.mocks import MockAuthClient


async def _run_reset_password_test(mocker, response_callback):
    mocked_client = MockAuthClient()
    mocker.patch("app.auth.routes.grpc_clients", {"auth": mocked_client})

    mocked_client.stub.ResetPassword = mocker.AsyncMock(side_effect=response_callback)

    request_data = {"token": "reset-token", "password": "password"}
    with TestClient(app=app) as client:
        response = client.post("/auth/reset-password", json=request_data)

    expected_request = auth_pb2.ResetPasswordRequest(**request_data)
    mocked_client.stub.ResetPassword.assert_called_once_with(expected_request)

    return response


@pytest.mark.asyncio
async def test_reset_password_mocked_success(mocker):
    grpc_response = auth_pb2.Empty()

    response = await _run_reset_password_test(mocker, lambda *_: grpc_response)

    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.asyncio
async def test_reset_password_mocked_error(mocker):
    async def create_rpc_error(*args, **kwargs):
        raise AioRpcError(
            code=StatusCode.INVALID_ARGUMENT,
            initial_metadata=Metadata(),
            trailing_metadata=Metadata(),
            details="invalid token",
        )

    response = await _run_reset_password_test(mocker, create_rpc_error)

    assert response.status_code == 400
    assert response.json() == {"detail": "invalid token"}
