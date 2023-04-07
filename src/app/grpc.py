import asyncio
from typing import TypedDict

import grpc

from protos.auth_pb2_grpc import AuthenticationStub


class GrpcClientBase:
    """
    gRPC client base with automatic retry
    on UNAVAILABLE and DEADLINE_EXCEEDED status codes.
    """

    def __init__(self, host: str, port: int, max_retries: int, retry_interval: int):
        self._host = host
        self._port = port
        self._max_retries = max_retries
        self._retry_interval = retry_interval
        self._channel = grpc.aio.insecure_channel(f"{self._host}:{self._port}")

    async def __aenter__(self) -> "GrpcClientBase":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._channel.close()

    async def _retry_on_unavailable(self, call, *args, **kwargs):
        retries = 0
        error = None
        while retries <= self._max_retries:
            try:
                return await call(*args, **kwargs)
            except grpc.aio.AioRpcError as e:
                error = e
                if error.code() in (
                    grpc.StatusCode.UNAVAILABLE,
                    grpc.StatusCode.DEADLINE_EXCEEDED,
                ):
                    retries += 1
                    await asyncio.sleep(self._retry_interval)
                else:
                    raise
        raise error

    def __getattribute__(self, name):
        try:
            orig_attr = super().__getattribute__(name)
        except AttributeError:
            return super().__getattribute__(name)

        if callable(orig_attr) and not name.startswith("_"):

            async def wrapped_call(*args, **kwargs):
                return await self._retry_on_unavailable(orig_attr, *args, **kwargs)

            return wrapped_call
        return orig_attr


class AuthGrpcClient(GrpcClientBase, AuthenticationStub):
    def __init__(
        self, host: str, port: int, max_retries: int = 3, retry_interval: int = 1
    ):
        GrpcClientBase.__init__(self, host, port, max_retries, retry_interval)
        AuthenticationStub.__init__(self, self._channel)


class GrpcClients(TypedDict, total=False):
    auth: AuthGrpcClient


grpc_clients: GrpcClients = {}
