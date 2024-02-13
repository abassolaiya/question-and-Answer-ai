#!/usr/bin/env bash

echo "Starting app......\n"
echo "Env is $ENV"

echo "Starting service is development mode\n"
exec python manage.py runserver 0.0.0.0:$PORT
