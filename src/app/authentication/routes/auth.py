from datetime import timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError

from app.authentication.dependencies import CurrentUser, GetUserService
from app.authentication.exceptions import BadRequest, Unauthorized
from app.authentication.oauth import oauth2_scheme
from app.authentication.password import verify_password
from app.authentication.schemas import (
    BearerResponse,
    ForgotPassword,
    ResetPassword,
    UserCreate,
    UserRead,
    UserUpdateFull,
    VerifyRequest,
    VerifyToken,
)
from app.authentication.utils import create_jwt, decode_jwt
from app.config import settings
from app.notifications.email import generate_email

router = APIRouter()


@router.post(
    "/token/login",
    response_model=BearerResponse,
)
async def login(
    user_service: GetUserService,
    data: OAuth2PasswordRequestForm = Depends(),
):
    user = await user_service.get_user_by_email(data.username)
    if not user or not verify_password(data.password, user.hashed_password):
        raise Unauthorized("Incorrect email or password")
    access_token = await user_service.create_token(
        user,
        settings.access_token_expire_minutes,
    )
    return BearerResponse(access_token=access_token, token_type="bearer")


@router.post("/token/logout")
async def logout(
    user_service: GetUserService,
    _: CurrentUser,
    token: str = Depends(oauth2_scheme),
):
    await user_service.remove_token(token)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    user_service: GetUserService,
):
    user = await user_service.get_user_by_email(data.email)
    if user:
        raise BadRequest("REGISTER_USER_ALREADY_EXISTS")
    return await user_service.create(data)


@router.post(
    "/verify-request",
    status_code=status.HTTP_202_ACCEPTED,
)
async def verify_request(
    data: VerifyRequest,
    background_tasks: BackgroundTasks,
    user_service: GetUserService,
):
    user = await user_service.get_user_by_email(data.email)
    if not user or not user.is_active or user.is_verified:
        return None

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "aud": "accent-design:verify",
    }
    verify_token_expires = timedelta(minutes=settings.verify_token_expire_minutes)
    verify_token = create_jwt(
        data=token_data,
        expires_delta=verify_token_expires,
    )

    background_tasks.add_task(
        generate_email,
        to_address=user.email,
        subject="Complete your registration",
        template_context={
            "token": verify_token,
            "host": "http://localhost",
            "site_name": "Example Inc.",
        },
        template_name_text="verify_request.txt",
        template_name_html="verify_request.html",
    )


@router.post(
    "/verify",
    response_model=UserRead,
)
async def verify(
    data: VerifyToken,
    user_service: GetUserService,
):
    try:
        decoded = decode_jwt(
            data.token,
            audience="accent-design:verify",
        )
    except JWTError as e:
        raise BadRequest("VERIFY_USER_BAD_TOKEN") from e

    if not decoded.get("sub") or not decoded.get("email"):
        raise BadRequest("VERIFY_USER_BAD_TOKEN")

    user = await user_service.get_user_by_email(decoded["email"])
    if not user or str(user.id) != decoded["sub"]:
        raise BadRequest("VERIFY_USER_BAD_TOKEN")

    if user.is_verified:
        raise BadRequest("VERIFY_USER_ALREADY_VERIFIED")

    await user_service.update(user.id, UserUpdateFull(is_verified=True))
    return user


@router.post(
    "/forgot-password",
    status_code=status.HTTP_202_ACCEPTED,
)
async def forgot_password(
    data: ForgotPassword,
    background_tasks: BackgroundTasks,
    user_service: GetUserService,
):
    user = await user_service.get_user_by_email(data.email)
    if not user:
        return None
    if not user.is_active:
        return None

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "aud": "accent-design:reset",
    }
    reset_token_expires = timedelta(minutes=settings.reset_token_expire_minutes)
    reset_token = create_jwt(
        data=token_data,
        expires_delta=reset_token_expires,
    )

    background_tasks.add_task(
        generate_email,
        to_address=user.email,
        subject="Reset your password",
        template_context={
            "token": reset_token,
            "host": "http://localhost",
            "site_name": "Example Inc.",
        },
        template_name_text="forgot_password.txt",
        template_name_html="forgot_password.html",
    )


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
)
async def reset_password(
    data: ResetPassword,
    user_service: GetUserService,
):
    try:
        decoded = decode_jwt(
            data.token,
            audience="accent-design:reset",
        )
    except JWTError as e:
        raise BadRequest("RESET_PASSWORD_BAD_TOKEN") from e

    if not decoded.get("sub") or not decoded.get("email"):
        raise BadRequest("RESET_PASSWORD_BAD_TOKEN")

    user = await user_service.get_user_by_email(decoded["email"])
    if not user or str(user.id) != decoded["sub"]:
        raise BadRequest("RESET_PASSWORD_BAD_TOKEN")

    await user_service.set_password(user, data.password)
