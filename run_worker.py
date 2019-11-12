#!/usr/bin/env python3
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from rq import Connection, Queue, Worker

if __name__ == '__main__':
    # Tell rq what Redis connection to use
    with Connection():
        q = Queue()
        Worker(q).work()
