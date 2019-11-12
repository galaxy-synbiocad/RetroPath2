#!/bin/bash

supervisord -c /home/rqworker.conf &
python /home/flask_rq.py
