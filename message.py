import time
from collections import deque

from common import *


def put_message(qid, msg, replace=False):
    if qid not in queues:
        queues[qid] = deque()
    queues[qid].append(msg)


def get_message(qid):
    if qid not in queues:
        queues[qid] = deque()
    q = queues[qid]
    while True:
        msg = peek_message(qid)
        if msg:
            return msg
        time.sleep(0.001)

def peek_message(qid):
    if qid not in queues:
        queues[qid] = deque()
    q = queues[qid]
    return q.popleft() if q else None


queues = {}
