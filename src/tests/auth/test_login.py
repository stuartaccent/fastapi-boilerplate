import pytest
from grpc import StatusCode
from grpc.aio import AioRpcError, Metadata
from starlette.testclient import TestClient

from app.main import app
from protos import auth_pb2
from tests.mocks import MockAuthClient


async def _run_login_test(mocker, response_callback):
    mocked_client = MockAuthClient()
    mocker.patch("app.auth.routes.grpc_clients", {"auth": mocked_client})

    mocked_client.stub.BearerToken = mocker.AsyncMock(side_effect=response_callback)

    request_data = {"username": "email@example.com", "password": "password"}
    with TestClient(app=app) as client:
        response = client.post("/auth/token/login", data=request_data)

    expected_request = auth_pb2.BearerTokenRequest(
        email="email@example.com", password="password"
    )
    mocked_client.stub.BearerToken.assert_called_once_with(expected_request)

    return response


@pytest.mark.asyncio
async def test_login_mocked_success(mocker):
    grpc_response = auth_pb2.BearerTokenResponse(
        access_token="test-token",
        token_type="bearer",
        expiry=3600,
    )

    response = await _run_login_test(mocker, lambda *_: grpc_response)

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "test-token",
        "token_type": "bearer",
        "expiry": 3600,
    }


@pytest.mark.asyncio
async def test_login_mocked_error(mocker):
    async def create_rpc_error(*args, **kwargs):
        raise AioRpcError(
            code=StatusCode.UNAUTHENTICATED,
            initial_metadata=Metadata(),
            trailing_metadata=Metadata(),
            details="invalid credentials",
        )

    response = await _run_login_test(mocker, create_rpc_error)

    assert response.status_code == 400
    assert response.json() == {"detail": "INCORRECT_LOGIN_CREDENTIALS"}
