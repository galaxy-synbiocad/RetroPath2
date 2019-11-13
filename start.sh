#!/bin/bash

export LC_ALL=C.UTF-8
export LANG=C.UTF-8


redis-cli flushall
supervisord -c /home/rqworker.conf &
python3 /home/flask_rq.py
