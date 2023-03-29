FROM        accent/python-uvicorn-gunicorn:3.11-slim as base

ARG         ENVIRONMENT=production

WORKDIR     /app

COPY        ./src/pyproject.toml ./src/poetry.lock ./

RUN         pip install --upgrade pip poetry wheel \
            && poetry config virtualenvs.create false \
            && poetry install $(test "$ENVIRONMENT" = production && echo "--only main") --no-interaction --no-ansi \
            && rm -rf /root/.cache/pypoetry

FROM        base as final

ENV         PYTHONDONTWRITEBYTECODE=1
ENV         PYTHONFAULTHANDLER=1
ENV         PYTHONPATH=/app

WORKDIR     /app

COPY        ./src .