FROM        accent/python-uvicorn-gunicorn:3.11-slim

ARG         ENVIRONMENT=production

ENV         ENVIRONMENT=${ENVIRONMENT}
ENV         PYTHONDONTWRITEBYTECODE=1
ENV         PYTHONFAULTHANDLER=1

COPY        ./src/pyproject.toml ./src/poetry.lock /

RUN         pip install --upgrade pip poetry wheel \
            && poetry config virtualenvs.create false \
            && poetry install $(test "$ENVIRONMENT" = production && echo "--only main") --no-interaction --no-ansi \
            && rm -rf /root/.cache/pypoetry

WORKDIR     /app
COPY        src .
