FROM        accent/python-uvicorn:3.12-slim AS base

ARG         ENVIRONMENT=production

WORKDIR     /app

COPY        ./src/pyproject.toml ./src/poetry.lock ./

RUN         pip install poetry \
            && poetry config virtualenvs.create false \
            && poetry install $(test "$ENVIRONMENT" = production && echo "--only main") --no-interaction --no-ansi \
            && rm -rf /root/.cache/pypoetry

FROM        base AS final

ENV         PYTHONDONTWRITEBYTECODE=1
ENV         PYTHONFAULTHANDLER=1
ENV         PYTHONPATH=/app

WORKDIR     /app

COPY        ./src .