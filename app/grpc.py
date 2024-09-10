import asyncio
from typing import TypedDict

import grpc

from app.protos.auth_pb2_grpc import AuthenticationStub
from app.protos.email_pb2_grpc import EmailServiceStub


class GrpcClientBase:
    """
    gRPC client base with automatic retry
    on UNAVAILABLE and DEADLINE_EXCEEDED status codes.
    """

    SERVICE_STUB = None

    def __init__(
        self,
        host: str,
        port: int,
        max_retries: int = 3,
        retry_interval: int = 1,
    ):
        self._host = host
        self._port = port
        self._max_retries = max_retries
        self._retry_interval = retry_interval
        self._channel = grpc.aio.insecure_channel(f"{self._host}:{self._port}")
        if self.SERVICE_STUB:
            self.SERVICE_STUB.__init__(self, self._channel)
        else:
            raise NotImplementedError("Subclasses should define a SERVICE_STUB.")

    async def __aenter__(self) -> "GrpcClientBase":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._channel.close()

    async def _retry_on_unavailable(self, call, *args, **kwargs):
        retries = 0
        last_error = None
        while retries <= self._max_retries:
            try:
                return await call(*args, **kwargs)
            except grpc.aio.AioRpcError as e:
                last_error = e
                if e.code() in (
                    grpc.StatusCode.UNAVAILABLE,
                    grpc.StatusCode.DEADLINE_EXCEEDED,
                ):
                    retries += 1
                    await asyncio.sleep(self._retry_interval)
                else:
                    raise
        raise last_error

    def __getattribute__(self, name):
        orig_attr = object.__getattribute__(self, name)
        if not callable(orig_attr) or name.startswith("__"):
            return orig_attr

        # don't wrap this classes attributes
        if name in dir(GrpcClientBase):
            return orig_attr

        # wrap calls on the stub classes with retry logic
        async def wrapped_call(*args, **kwargs):
            return await self._retry_on_unavailable(orig_attr, *args, **kwargs)

        return wrapped_call


class AuthGrpcClient(GrpcClientBase, AuthenticationStub):
    SERVICE_STUB = AuthenticationStub


class EmailGrpcClient(GrpcClientBase, EmailServiceStub):
    SERVICE_STUB = EmailServiceStub


class GrpcClients(TypedDict, total=False):
    auth: AuthGrpcClient
    email: EmailGrpcClient


grpc_clients: GrpcClients = {}
