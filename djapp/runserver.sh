#!/bin/sh

echo "run MODE: $SERVICE_MODE"

WEB_PORT=${WEB_PORT:=8000}

WEB_CONCURRENCY=${WEB_CONCURRENCY:=3}

MAX_REQUESTS=${MAX_REQUESTS:=5000}

if [ "asgi" = "$SERVICE_MODE" ]; then
    gunicorn djapp.asgi -b :$WEB_PORT -k uvicorn.workers.UvicornWorker -w $WEB_CONCURRENCY --max-requests $MAX_REQUESTS
elif [ "django" = "$SERVICE_MODE" ]; then
    ./manage.py runserver 0:$WEB_PORT
else
    echo "unknown mode: $SERVICE_MODE"
fi
