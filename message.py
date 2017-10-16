import time
from collections import deque


def put_message(qid, msg):
    if qid not in queues:
        queues[qid] = deque()
    queues[qid].append(msg)


def get_message(qid):
    if qid not in queues:
        queues[qid] = deque()
    q = queues[qid]
    while not len(q):
        time.sleep(0.001)
    return q.popleft()


queues = {}
