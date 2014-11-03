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

_config = {"redis": None}

def config(host='localhost', port=6379, timeout=10, exipre=10, retry_interval=0.01):
    _config['redis']  = redis.Redis(host, port)
    _config['timeout'] = timeout
    _config['exipre'] = exipre
    _config['retry_interval'] = retry_interval

def getRedis():




class RedLock(object):

    def __init__(self, key="default"):
        self.redis_client = _config.get('redis') 
        self.lock_key = "redlock:%s" % key


    def __enter__(self):
        self.accquire()

    def __exit__(self):
        self.release()

    def __del__(self):
        self.release()

    def accquire():
        pass

    def release():
        pass
