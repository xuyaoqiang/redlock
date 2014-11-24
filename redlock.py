#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: xuyaoqiang
@contact: xuyaoqiang@gmail.com
@date: 2014-08-13 00:15
@version: 0.0.0
@license:
@copyright:

"""

import redis
import time

connectionPools = {}

def getRedis(**kwargs):
    """
    Match up the provided kwargs with an existing connection pool.
    In cases where you may want a lot of queues, the redis library will
    by default open at least one connection for each. This uses redis'
    connection pool mechanism to keep the number of open file descriptors
    tractable.
    """
    key = ':'.join((repr(key) + '=>' + repr(value)) for key, value in kwargs.items())
    try:
        return redis.Redis(connection_pool=connectionPools[key])
    except KeyError:
        cp = redis.ConnectionPool(**kwargs)
        connectionPools[key] = cp
        return redis.Redis(connection_pool=cp)


class RedLock(object):
    def __init__(self, key, host='localhost', port=6379, ttl=60):
        self.redis_host = host 
        self.redis_port = port
        self.redis = getRedis(host=self.redis_host, port=self.redis_port)
        self.key = "redlock:%s" % key
        self.ttl = ttl 
        self.locked = False
        self.expiration = None 
        self.wait_delay = 0.0001

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, type, value, traceback):
        self.release()

    def acquire(self, blocking=False):
        expiration = self._new_expiration
        self.lock = self.redis.setnx(self.key, expiration)
        if self.locked:
            self.expiration = expiration
        elif self._exipred:
            self.locked = self._update_expiration()
        if blocking:
            self.wait()
        return self.locked

    def release(self):
        if not self._locking:
            return False
        return self.redis.delete(self.key)

    def wait(self):
        while not self.locked:
            time.sleep(self._time_to_expire + self.wait_delay)
            self.locked = self.acquire()
        return True

    def _update_expiration(self):
        expiration = self._new_expiration
        old_expiration = float(self.redis.getset(self.key, expiration) or 0)
        if old_expiration < time.time() or old_expiration == self.expiration:
            self.expiration = expiration
            return True
        return False

    @property
    def _locking(self):
        return self.locked and time.time() < self.expiration and not self._exipred

    @property
    def _time_to_expire(self):
        timestamp = self.redis.get(self.key)
        if not timestamp:
            return 0
        return max(float(timestamp) - time.time(), 0)

    @property
    def _exipred(self):
        return self._time_to_expire == 0

    @property
    def _new_expiration(self):
        return time.time() + self.ttl


