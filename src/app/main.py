# isort: off

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings
from app.database import tables  # dont remove

from app.api.routes.root import router as root_router
from app.api.schemas import UserCreate, UserRead, UserUpdate
from app.users import auth_backend, fastapi_users

if settings.sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.starlette import StarletteIntegration
    from sentry_sdk.integrations.fastapi import FastApiIntegration

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[
            StarletteIntegration(),
            FastApiIntegration(),
        ],
    )
    print("Sentry enabled")

else:
    print("Sentry not enabled as no SENTRY_DSN environment variable")


middleware = [
    Middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    ),
    Middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
]

app = FastAPI(
    title="myapi",
    middleware=middleware,
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url="/redocs",
)

app.include_router(root_router)
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/token",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
