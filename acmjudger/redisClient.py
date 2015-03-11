#!/usr/bin/env python
# -*- coding:utf-8 -*-

import redis
import logging

from srvconf import redis_server
from srvconf import redis_port


"""
db=0 for submission_q
"""



class RedisClient(object):
    def __init__(self, host=redis_server, port=redis_port, db=0):
        try:
            pool = redis.ConnectionPool(host=host, port=port, db=db)
            self.conn = redis.Redis(connection_pool=pool)
            #self.pipe = self.conn.pipeline()
        except:
            logging.error("RedisClient init error")

    def lpush(self, list_key, value=None):
        try:
            self.conn.lpush(list_key, value)
        except:
            logging.error("RedisClient lpush error when " + str(list_key) + " " + str(value))

    def rpush(self, list_key, value=None):
        try:
            self.conn.rpush(list_key, value)
        except:
            logging.error("RedisClient rpush error when " + str(list_key) + " " + str(value))

    def rpop(self, list_key):
        try:
            return self.conn.rpop(list_key)
        except:
            logging.error("RedisClient rpop error when " + str(list_key))

    def brpop(self, list_key, timeout=0):
        try:
            return self.conn.brpop(list_key, timeout)
        except:
            logging.error("RedisClient brpop error when " + str(list_key))

    def set(self, string_key, value):
        try:
            self.conn.set(string_key, value)
        except:
            logging.error("RedisClient set error when " + str(string_key) + " " + str(value))

    def get(self, string_key):
        try:
            return self.conn.get(string_key)
        except:
            logging.error("RedisClient get error when " + str(string_key))

    def expire(self, key, timeout):
        try:
            self.conn.expire(key, timeout)
        except:
            logging.error("RedisClient set timeout error when " + str(key) + " " + str(timeout))

    def exists(self, key):
        try:
            return self.conn.exists(key)
        except:
            logging.error("RedisClient exist error when " + str(key))

    def delete(self, key):
        try:
            self.conn.delete(key)
        except:
            logging.error("RedisClient delete error when " + str(key))

    def sadd(self, set_key, value=None):
        try:
            self.conn.sadd(set_key, value)
        except:
            logging.error("RedisClient sadd error when " + str(set_key) + " " + str(value))

    def smembers(self, set_key):
        try:
            return self.conn.smembers(set_key)
        except:
            logging.error("RedisClient smember error when " + str(set_key))

    def srem(self, set_key, value=None):
        try:
            self.conn.srem(set_key, value)
        except:
            logging.error("RedisClient srem error when " + str(set_key) + " " + str(value))

    def spop(self, set_key):
        try:
            return self.conn.spop(set_key)
        except:
            logging.error("RedisClient spop error when " + str(set_key))

    def setbit(self, bitmap_key, offset, value):
        try:
            old_value = self.conn.setbit(bitmap_key, offset, value)
            return old_value
        except:
            logging.error("RedisClient setbit error when " + str(bitmap_key))

    def getbit(self, bitmap_key, offset):
        try:
            return self.conn.getbit(bitmap_key, offset)
        except:
            logging.error("RedisClient getbit error when " + str(bitmap_key))

