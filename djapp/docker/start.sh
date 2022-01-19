#!/bin/bash

WEB_PORT=${WEB_PORT:=8000}
WEB_CONCURRENCY=${WEB_CONCURRENCY:=3}
MAX_REQUESTS=${MAX_REQUESTS:=5000}

cd /app


if [ $# -eq 0 ]; then
  echo "Usage: start.sh [PROCESS_TYPE](server/worker/notification_listener)"
else
  PROCESS_TYPE=$1
fi

function start_server() {
    echo "Start server..."

    if [ "$DEBUG" = "1" ]; then
      python manage.py runserver 0.0.0.0:$WEB_PORT
    else
      gunicorn djapp.asgi \
        -b :$WEB_PORT \
        -k uvicorn.workers.UvicornWorker \
        -w $WEB_CONCURRENCY \
        --max-requests $MAX_REQUESTS
    fi
}

function start_notification_listener() {
  echo "Start openstack notification listener ..."

  python manage.py run_notification_listener
}

function start_worker() {
  echo "Start celery worker ..."

  celery \
    --app djapp.celery_app \
    worker \
    --loglevel INFO
}


function main() {
  case "$PROCESS_TYPE" in
    "notification_listener")
      start_notification_listener
      ;;
    "worker")
      start_worker
      ;;
    *)
      start_server
      ;;
  esac
}

main
