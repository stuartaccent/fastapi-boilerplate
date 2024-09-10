#! /usr/bin/env sh

set -e

alembic upgrade head

HOST=${HOST:-"0.0.0.0"}
PORT=${PORT:-80}
WORKERS=${WORKERS:-2}
LIFESPAN=${LIFESPAN:-"auto"}
LOG_LEVEL=${LOG_LEVEL:-"info"}
PROXY_HEADERS=${PROXY_HEADERS:-"on"}
FORWARDED_ALLOW_IPS=${FORWARDED_ALLOW_IPS:-"127.0.0.1"}
LIMIT_MAX_REQUESTS=${LIMIT_MAX_REQUESTS:-1000}
SSL_KEYFILE=${SSL_KEYFILE:-""}
SSL_CERTFILE=${SSL_CERTFILE:-""}
APP_MODULE=${APP_MODULE:-"app.main:app"}

echo "Uvicorn settings:"
echo "HOST: $HOST"
echo "PORT: $PORT"
echo "WORKERS: $WORKERS"
echo "LIFESPAN: $LIFESPAN"
echo "LOG_LEVEL: $LOG_LEVEL"
echo "PROXY_HEADERS: $PROXY_HEADERS" 
echo "FORWARDED_ALLOW_IPS: $FORWARDED_ALLOW_IPS"
echo "LIMIT_MAX_REQUESTS: $LIMIT_MAX_REQUESTS"
echo "SSL_KEYFILE: $SSL_KEYFILE"
echo "SSL_CERTFILE: $SSL_CERTFILE"
echo "APP_MODULE: $APP_MODULE"
echo ""

exec uvicorn \
--host $HOST \
--port $PORT \
--workers $WORKERS \
--lifespan "$LIFESPAN" \
--log-level $LOG_LEVEL \
$( [ "$PROXY_HEADERS" = "on" ] && echo "--proxy-headers" ) \
--forwarded-allow-ips "$FORWARDED_ALLOW_IPS" \
--limit-max-requests $LIMIT_MAX_REQUESTS \
$( [ -n "$SSL_KEYFILE" ] && echo "--ssl-keyfile $SSL_KEYFILE" ) \
$( [ -n "$SSL_CERTFILE" ] && echo "--ssl-certfile $SSL_CERTFILE" ) \
"$APP_MODULE" \
"$@"