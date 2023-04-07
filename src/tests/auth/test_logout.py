import pytest
from grpc import StatusCode
from grpc.aio import AioRpcError, Metadata
from starlette.testclient import TestClient

from app.auth.dependencies import current_user
from app.main import app
from protos import auth_pb2
from tests.mocks import MockAuthClient


async def _run_logout_test(mocker, mock_current_user, response_callback):
    app.dependency_overrides[current_user] = lambda: mock_current_user

    mocked_client = MockAuthClient()
    mocker.patch("app.auth.routes.grpc_clients", {"auth": mocked_client})

    mocked_client.stub.RevokeBearerToken = mocker.AsyncMock(
        side_effect=response_callback
    )

    with TestClient(app=app) as client:
        response = client.post(
            "/auth/token/logout",
            headers={"Authorization": "Bearer test-token"},
        )

    expected_request = auth_pb2.Token(token="test-token")
    mocked_client.stub.RevokeBearerToken.assert_called_once_with(expected_request)

    app.dependency_overrides = {}

    return response


@pytest.mark.asyncio
async def test_logout_mocked_success(mocker, mock_current_user):
    grpc_response = auth_pb2.Empty()

    response = await _run_logout_test(
        mocker, mock_current_user, lambda *_: grpc_response
    )

    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.asyncio
async def test_logout_mocked_error(mocker, mock_current_user):
    async def create_rpc_error(*args, **kwargs):
        raise AioRpcError(
            code=StatusCode.INTERNAL,
            initial_metadata=Metadata(),
            trailing_metadata=Metadata(),
            details="unknown issue",
        )

    response = await _run_logout_test(mocker, mock_current_user, create_rpc_error)

    assert response.status_code == 200
    assert response.json() is None
