import pytest
from google.protobuf.json_format import MessageToDict
from grpc import StatusCode
from grpc.aio import AioRpcError, Metadata
from starlette.testclient import TestClient

from app.auth.schemas import UserRead
from app.main import app
from protos import auth_pb2
from tests.mocks import MockAuthClient


async def _run_register_test(mocker, response_callback):
    mocked_client = MockAuthClient()
    mocker.patch("app.auth.routes.grpc_clients", {"auth": mocked_client})

    mocked_client.stub.Register = mocker.AsyncMock(side_effect=response_callback)

    request_data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "password",
    }
    with TestClient(app=app) as client:
        response = client.post("/auth/register", json=request_data)

    expected_request = auth_pb2.RegisterRequest(**request_data)
    mocked_client.stub.Register.assert_called_once_with(expected_request)

    return response


@pytest.mark.asyncio
async def test_register_mocked_success(mocker):
    grpc_response = auth_pb2.UserResponse(
        id="b67764c6-0fb1-4927-9613-3138c226d94e",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        user_type=auth_pb2.UserType(name="user", scopes=["read", "write"]),
        is_active=True,
        is_verified=False,
    )

    response = await _run_register_test(mocker, lambda *_: grpc_response)

    assert response.status_code == 201
    grpc_response_dict = MessageToDict(
        grpc_response,
        preserving_proto_field_name=True,
        including_default_value_fields=True,
    )
    assert UserRead(**response.json()) == UserRead(**grpc_response_dict)


@pytest.mark.asyncio
async def test_register_mocked_error(mocker):
    async def create_rpc_error(*args, **kwargs):
        raise AioRpcError(
            code=StatusCode.ALREADY_EXISTS,
            initial_metadata=Metadata(),
            trailing_metadata=Metadata(),
            details="a user with this email already exists",
        )

    response = await _run_register_test(mocker, create_rpc_error)

    assert response.status_code == 400
    assert response.json() == {"detail": "a user with this email already exists"}
