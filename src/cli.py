from asyncio import run as aiorun

import typer

from app.config import settings
from app.grpc import AuthGrpcClient
from protos import auth_pb2

app = typer.Typer()


async def _create_user(
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    verified: bool,
):
    timeout = 5
    async with AuthGrpcClient(settings.auth_host, settings.auth_port) as client:
        # create the user
        request = auth_pb2.RegisterRequest(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user = await client.Register(request, timeout=timeout)
        print(f"user created: {user.email}")

        if not verified:
            return

        # request a token
        request = auth_pb2.VerifyUserTokenRequest(email=user.email)
        token = await client.VerifyUserToken(request, timeout=timeout)
        print(f"verification token: {token.token}")

        # verify
        request = auth_pb2.Token(token=token.token)
        verify = await client.VerifyUser(request, timeout=timeout)
        print(f"user verified: {verify.is_verified}")


@app.command()
def create_user(
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    verified: bool = False,
):
    coro = _create_user(
        email,
        first_name,
        last_name,
        password,
        verified,
    )
    aiorun(coro)
    print("completed")


@app.command()
def hello():
    print("hello")


if __name__ == "__main__":
    app()
