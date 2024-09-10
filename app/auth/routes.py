import contextlib

import grpc
from fastapi import APIRouter, status
from google.protobuf.json_format import MessageToDict
from starlette.background import BackgroundTasks

from app.auth import schemas
from app.auth.dependencies import CurrentActiveUser, CurrentUser, Oauth2Form, Token
from app.auth.exceptions import BadRequest, IncorrectLoginCredentials
from app.config import settings
from app.grpc import grpc_clients
from app.protos import auth_pb2
from app.smtp.send import send_email

auth_router = APIRouter(prefix="/auth", tags=["auth"])
user_router = APIRouter(prefix="/users", tags=["users"])


@auth_router.post("/token/login")
async def login(data: Oauth2Form) -> schemas.BearerResponse:
    try:
        request = auth_pb2.BearerTokenRequest(
            email=data.username,
            password=data.password,
        )
        response = await grpc_clients["auth"].BearerToken(
            request,
            timeout=settings.grpc_timeout,
        )
        return MessageToDict(response, preserving_proto_field_name=True)
    except grpc.aio.AioRpcError as e:
        raise IncorrectLoginCredentials() from e


@auth_router.post("/token/logout")
async def logout(_: CurrentUser, token: Token) -> None:
    with contextlib.suppress(grpc.aio.AioRpcError):
        request = auth_pb2.Token(token=token)
        await grpc_clients["auth"].RevokeBearerToken(
            request,
            timeout=settings.grpc_timeout,
        )


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: schemas.UserCreate) -> schemas.UserRead:
    try:
        request = auth_pb2.RegisterRequest(**data.model_dump())
        response = await grpc_clients["auth"].Register(
            request,
            timeout=settings.grpc_timeout,
        )
        return MessageToDict(
            response,
            always_print_fields_with_no_presence=True,
            preserving_proto_field_name=True,
        )
    except grpc.aio.AioRpcError as e:
        raise BadRequest(e.details()) from e


@auth_router.post("/verify-request", status_code=status.HTTP_202_ACCEPTED)
async def verify_request(
    data: schemas.VerifyRequest,
    background_tasks: BackgroundTasks,
) -> None:
    with contextlib.suppress(grpc.aio.AioRpcError):
        request = auth_pb2.VerifyUserTokenRequest(email=data.email)
        response = await grpc_clients["auth"].VerifyUserToken(
            request,
            timeout=settings.grpc_timeout,
        )

        print("Success: VerifyUserToken")
        print("-" * 60)
        print(response)

        async def send_mail(email, token):
            await send_email(
                to_address=email,
                subject="Complete your registration",
                template_context={
                    "token": token,
                    "host": settings.site_url,
                    "site_name": settings.site_name,
                },
                template_name_text="verify_request.txt",
                template_name_html="verify_request.html",
            )

        background_tasks.add_task(send_mail, response.email, response.token)


@auth_router.post("/verify")
async def verify(data: schemas.VerifyToken) -> schemas.UserRead:
    try:
        request = auth_pb2.Token(token=data.token)
        response = await grpc_clients["auth"].VerifyUser(
            request,
            timeout=settings.grpc_timeout,
        )
        return MessageToDict(
            response,
            always_print_fields_with_no_presence=True,
            preserving_proto_field_name=True,
        )
    except grpc.aio.AioRpcError as e:
        raise BadRequest(e.details()) from e


@auth_router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    data: schemas.ForgotPassword,
    background_tasks: BackgroundTasks,
) -> None:
    with contextlib.suppress(grpc.aio.AioRpcError):
        request = auth_pb2.ResetPasswordTokenRequest(email=data.email)
        response = await grpc_clients["auth"].ResetPasswordToken(
            request,
            timeout=settings.grpc_timeout,
        )

        print("Success: ResetPasswordToken")
        print("-" * 60)
        print(response)

        async def send_mail(email, token):
            await send_email(
                to_address=email,
                subject="Reset your password",
                template_context={
                    "token": token,
                    "host": settings.site_url,
                    "site_name": settings.site_name,
                },
                template_name_text="forgot_password.txt",
                template_name_html="forgot_password.html",
            )

        background_tasks.add_task(send_mail, response.email, response.token)


@auth_router.post("/reset-password")
async def reset_password(data: schemas.ResetPassword) -> None:
    try:
        request = auth_pb2.ResetPasswordRequest(
            token=data.token,
            password=data.password,
        )
        await grpc_clients["auth"].ResetPassword(
            request,
            timeout=settings.grpc_timeout,
        )
    except grpc.aio.AioRpcError as e:
        raise BadRequest(e.details()) from e


@user_router.get("/me")
async def get_current_user(user: CurrentActiveUser) -> schemas.UserRead:
    return user


@user_router.patch("/me")
async def update_current_user(
    data: schemas.UserUpdate,
    token: Token,
    _: CurrentActiveUser,
) -> schemas.UserRead:
    try:
        request = auth_pb2.UpdateUserRequest(
            token=token, **data.model_dump(exclude_unset=True)
        )
        response = await grpc_clients["auth"].UpdateUser(
            request,
            timeout=settings.grpc_timeout,
        )
        return MessageToDict(
            response,
            always_print_fields_with_no_presence=True,
            preserving_proto_field_name=True,
        )
    except grpc.aio.AioRpcError as e:
        raise BadRequest(e.details()) from e
