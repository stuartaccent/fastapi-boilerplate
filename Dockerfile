FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.4.7 /uv /bin/uv

ARG ENVIRONMENT=prod

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
    --frozen \
    --no-install-project \
    $(if [ "$ENVIRONMENT" = "prod" ]; then echo "--no-dev"; fi)

ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync \
    --frozen \
    $(if [ "$ENVIRONMENT" = "prod" ]; then echo "--no-dev"; fi)

ENV PATH="/app/.venv/bin:$PATH"

CMD ["/app/start.sh"]