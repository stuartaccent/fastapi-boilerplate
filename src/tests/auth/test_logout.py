import pytest
from grpc import StatusCode
from grpc.aio import AioRpcError, Metadata

from app.main import app
from protos import auth_pb2
from tests.mocks import MockAuthClient


async def _run_logout_test(mocker, client, response_callback):
    mocked_client = MockAuthClient()
    mocker.patch("app.auth.routes.grpc_clients", {"auth": mocked_client})

    mocked_client.RevokeBearerToken = mocker.AsyncMock(side_effect=response_callback)

    response = client.post(
        "/auth/token/logout",
        headers={"Authorization": "Bearer test-token"},
    )

    expected_request = auth_pb2.Token(token="test-token")
    mocked_client.RevokeBearerToken.assert_called_once_with(expected_request, timeout=5)

    app.dependency_overrides = {}

    return response


@pytest.mark.asyncio
async def test_logout_mocked_success(mocker, client_authenticated):
    grpc_response = auth_pb2.Empty()

    async def response_callback(*args, **kwargs):
        assert kwargs["timeout"] == 5
        return grpc_response

    response = await _run_logout_test(mocker, client_authenticated, response_callback)

    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.asyncio
async def test_logout_mocked_error(mocker, client_authenticated):
    async def create_rpc_error(*args, **kwargs):
        raise AioRpcError(
            code=StatusCode.INTERNAL,
            initial_metadata=Metadata(),
            trailing_metadata=Metadata(),
            details="unknown issue",
        )

    response = await _run_logout_test(mocker, client_authenticated, create_rpc_error)

    assert response.status_code == 200
    assert response.json() is None
