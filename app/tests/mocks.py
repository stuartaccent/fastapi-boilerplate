from unittest.mock import MagicMock

import grpc

from app.auth.exceptions import Unauthorized
from app.protos.auth_pb2_grpc import AuthenticationStub


class MockAuthClient(AuthenticationStub):
    def __init__(self):
        self.channel = MagicMock(spec=grpc.aio.Channel)
        super().__init__(self.channel)

    async def __aenter__(self) -> "MockAuthClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass


async def raise_unauthenticated():
    """mock the current user so that is raises Unauthorized"""
    raise Unauthorized()
