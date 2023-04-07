from unittest.mock import MagicMock

import grpc

from protos.auth_pb2_grpc import AuthenticationStub


class MockAuthClient:
    client = MagicMock(spec=grpc.aio.Channel)
    stub: AuthenticationStub = AuthenticationStub(client)

    async def __aenter__(self) -> "MockAuthClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass

    async def __call__(self, method: str, *args, **kwargs):
        return await getattr(self.stub, method)(*args, **kwargs)
