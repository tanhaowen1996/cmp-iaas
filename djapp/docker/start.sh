#!/bin/bash

WEB_PORT=${WEB_PORT:=8000}
WEB_CONCURRENCY=${WEB_CONCURRENCY:=3}
MAX_REQUESTS=${MAX_REQUESTS:=5000}

cd /app


if [ $# -eq 0 ]; then
  echo "Usage: start.sh [PROCESS_TYPE](server/beat/worker)"
else
  PROCESS_TYPE=$1
fi

function start_server() {
    echo "Start server..."

    if [ "$DEBUG" = "1" ]; then
      python manage.py runserver 0.0.0.0:$WEB_PORT
    else
      gunicorn cmp_iaas.asgi \
        -b :$WEB_PORT \
        -k uvicorn.workers.UvicornWorker \
        -w $WEB_CONCURRENCY \
        --max-requests $MAX_REQUESTS
    fi
}

function start_beat() {
  echo "Start celery beat ..."

  celery \
    --app cmp_iaas.celery_app \
    beat \
    --loglevel INFO \
    --scheduler django_celery_beat.schedulers:DatabaseScheduler
}

function start_worker() {
  echo "Start celery worker ..."

  celery \
    --app cmp_iaas.celery_app \
    worker \
    --loglevel INFO
}


function main() {
  case "$PROCESS_TYPE" in
    "beat")
      start_beat
      ;;
    "worker")
      start_worker
      ;;
    *)
      start_worker
      ;;
  esac
}

main
