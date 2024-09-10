import pytest
from google.protobuf.json_format import MessageToDict
from grpc import StatusCode
from grpc.aio import AioRpcError, Metadata

from app.auth.schemas import UserRead
from app.config import settings
from app.protos import auth_pb2
from app.tests.mocks import MockAuthClient


async def _run_register_test(mocker, client, response_callback):
    mocked_client = MockAuthClient()
    mocker.patch("app.auth.routes.grpc_clients", {"auth": mocked_client})

    mocked_client.Register = mocker.AsyncMock(side_effect=response_callback)

    request_data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "password": "password",
    }
    response = await client.post("/auth/register", json=request_data)

    expected_request = auth_pb2.RegisterRequest(**request_data)
    mocked_client.Register.assert_called_once_with(
        expected_request,
        timeout=settings.grpc_timeout,
    )

    return response


@pytest.mark.anyio
async def test_register_mocked_success(mocker, client_unauthenticated):
    grpc_response = auth_pb2.UserResponse(
        id="b67764c6-0fb1-4927-9613-3138c226d94e",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        user_type=auth_pb2.UserType(name="user", scopes=["read", "write"]),
        is_active=True,
        is_verified=False,
    )

    async def response_callback(*args, **kwargs):
        assert kwargs["timeout"] == 5
        return grpc_response

    response = await _run_register_test(
        mocker, client_unauthenticated, response_callback
    )

    assert response.status_code == 201
    grpc_response_dict = MessageToDict(
        grpc_response,
        always_print_fields_with_no_presence=True,
        preserving_proto_field_name=True,
    )
    assert UserRead(**response.json()) == UserRead(**grpc_response_dict)


@pytest.mark.anyio
async def test_register_mocked_error(mocker, client_unauthenticated):
    async def create_rpc_error(*args, **kwargs):
        raise AioRpcError(
            code=StatusCode.ALREADY_EXISTS,
            initial_metadata=Metadata(),
            trailing_metadata=Metadata(),
            details="a user with this email already exists",
        )

    response = await _run_register_test(
        mocker, client_unauthenticated, create_rpc_error
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "a user with this email already exists"}
