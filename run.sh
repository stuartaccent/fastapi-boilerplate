#! /usr/bin/env sh

docker compose run \
--rm \
--volume $(pwd):/app \
--volume /app/.venv \
-it \
app \
"$@"