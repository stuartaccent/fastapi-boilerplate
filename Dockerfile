ARG         PIPENV_INSTALL_OPTIONS=--deploy
FROM        accent/python-uvicorn-gunicorn:3.10-slim

ENV         PYTHONDONTWRITEBYTECODE 1
ENV         PYTHONFAULTHANDLER 1

RUN         apt update && apt install git gcc -y

RUN         pip install pipenv

COPY        src /app
WORKDIR     /app

# Generate the Pipfile.lock during the image build process, then immediately remove the venv.
# RUN         pipenv lock && pipenv --clear && pipenv --rm

ARG         PIPENV_INSTALL_OPTIONS
RUN         pipenv install --system $PIPENV_INSTALL_OPTIONS
