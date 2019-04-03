# -*- coding: utf-8 -*-
from collections import deque
"""repeat function"""
q = deque(maxlen=3)
dic = {}
count = 0


def get_in(msg: str) -> str:
    global count
    count += 1
    if count > q.maxlen:
        count -= 1
        tmp = q.popleft()
        if tmp in dic.keys():
            dic[tmp] -= 1
            if dic[tmp] == 0:
                del dic[tmp]
    q.append(msg)
    if msg not in dic.keys():
        dic.setdefault(msg, 1)
    else:
        dic[msg] += 1
        if dic[msg] >= q.maxlen - 1:
            count -= q.maxlen - 1
            del dic[msg]
            return msg


"""function end"""
