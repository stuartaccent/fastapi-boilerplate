FROM        accent/python-uvicorn-gunicorn:3.11-slim

ARG         ENVIRONMENT=production

ENV         ENVIRONMENT=${ENVIRONMENT}
ENV         PYTHONDONTWRITEBYTECODE=1
ENV         PYTHONFAULTHANDLER=1

RUN         pip install --upgrade pip poetry wheel

COPY        src /app
WORKDIR     /app

RUN         poetry config virtualenvs.create false \
            && poetry install $(test "$ENVIRONMENT" == production && echo "--no-dev") --no-interaction --no-ansi
