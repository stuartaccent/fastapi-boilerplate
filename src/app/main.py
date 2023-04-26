from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes.root import router as root_router
from app.auth.routes import auth_router, user_router
from app.config import settings
from app.database import tables  # noqa: F401
from app.grpc import AuthGrpcClient, EmailGrpcClient, grpc_clients

if settings.sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    auth_client = AuthGrpcClient(settings.auth_host, settings.auth_port)
    email_client = EmailGrpcClient(settings.email_host, settings.email_port)

    async with auth_client as auth, email_client as email:
        grpc_clients["auth"] = auth
        grpc_clients["email"] = email
        yield

    grpc_clients.clear()


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
    lifespan=lifespan,
)

app.include_router(root_router)
app.include_router(auth_router)
app.include_router(user_router)
