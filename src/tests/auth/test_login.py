import pytest
from grpc import StatusCode
from grpc.aio import AioRpcError, Metadata

from app.config import settings
from protos import auth_pb2
from tests.mocks import MockAuthClient


async def _run_login_test(mocker, client, response_callback):
    mocked_client = MockAuthClient()
    mocker.patch("app.auth.routes.grpc_clients", {"auth": mocked_client})

    mocked_client.BearerToken = mocker.AsyncMock(side_effect=response_callback)

    request_data = {"username": "email@example.com", "password": "password"}
    response = await client.post("/auth/token/login", data=request_data)

    expected_request = auth_pb2.BearerTokenRequest(
        email="email@example.com", password="password"
    )
    mocked_client.BearerToken.assert_called_once_with(
        expected_request,
        timeout=settings.grpc_timeout,
    )

    return response


@pytest.mark.anyio
async def test_login_mocked_success(mocker, client_unauthenticated):
    grpc_response = auth_pb2.BearerTokenResponse(
        access_token="test-token",
        token_type="bearer",
        expiry=3600,
    )

    async def response_callback(*args, **kwargs):
        assert kwargs["timeout"] == 5
        return grpc_response

    response = await _run_login_test(mocker, client_unauthenticated, response_callback)

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "test-token",
        "token_type": "bearer",
        "expiry": 3600,
    }


@pytest.mark.anyio
async def test_login_mocked_error(mocker, client_unauthenticated):
    async def create_rpc_error(*args, **kwargs):
        raise AioRpcError(
            code=StatusCode.UNAUTHENTICATED,
            initial_metadata=Metadata(),
            trailing_metadata=Metadata(),
            details="invalid credentials",
        )

    response = await _run_login_test(mocker, client_unauthenticated, create_rpc_error)

    assert response.status_code == 400
    assert response.json() == {"detail": "Incorrect login credentials"}
