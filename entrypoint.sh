#!/bin/bash
set -e

python3 -u bot.py >  /var/log/bot.log 2>&1 &

cd ctfdash
exec gunicorn --bind 0.0.0.0:5050 ctfdash.wsgi:application
