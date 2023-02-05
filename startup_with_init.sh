#!/bin/sh

python3 ./init_db.py
gunicorn app:serve --bind 0.0.0.0:8080 --worker-class aiohttp.GunicornWebWorker