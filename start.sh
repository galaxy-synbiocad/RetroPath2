#!/bin/bash

supervisord -c rqworker.conf &
python flask_rq.py
