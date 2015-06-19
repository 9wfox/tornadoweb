# -*- coding:utf-8 -*-

"""
    缓存模块

    为缓存操作提供辅助便捷方法。

    作者: Q.yuhen
    创建: 2011-08-17

    历史:
"""

from functools import partial

from redis import Redis
from redis.client import Pipeline

from utility import staticclass
from logic import get_context


# 缓存数据结构类型
STRING = "Strings"
HASH = "Hashes"
LIST = "Lists"
SET = "Sets"
SORTEDSET = "Sorted Sets"


@staticclass
class RedisCache(object):

    @staticmethod
    def set(key, value, expire = None, new = False, mode = STRING):
        """
            设置缓存

            参数:
                key
                value
                expire      过期时间(秒)
                new         是否删除已有的同名 KV
                mode        数据类型

            示例:
                set("a", range(10), mode = SET)
                set("b", zip(range(10), [float(x) / 10 for x in range(10)]), mode = SORTEDSET)
                set("c", dict(a = 1, b = 2), expire = 60, mode = HASH)
        """
        cache = get_context().get_cache(key)
        pipe = cache.pipeline() if new or (expire is not None) or (mode in (LIST, SET, SORTEDSET)) else cache

        method = { 
            STRING: pipe.set, 
            HASH: pipe.hmset, 
            LIST: pipe.rpush, 
            SET: pipe.sadd, 
            SORTEDSET: pipe.zadd 
        }.get(mode)

        if new: pipe.delete(key)

        if mode in (LIST, SET, SORTEDSET):
            for v in value: # 2.2 不支持 multi...
                method(key, *v) if isinstance(v, (tuple, list)) else method(key, v)
        else:
            method(key, value)

        if expire is not None: pipe.expire(key, expire)
        if isinstance(pipe, Pipeline): pipe.execute()


    @staticmethod
    def delete(*keys):
        """
            删除缓存
        """
        context = get_context()

        for k in keys:
            context.get_cache(k).delete(k)


    @staticmethod
    def op(key, method, *args, **kwargs):
        """
            缓存操作

            参数:
                expire_seconds  设置过期秒数，0 表示移除过期设置。
        """
        expire_seconds = kwargs.get("expire_seconds")
        cache = get_context().get_cache(key)

        if expire_seconds is not None:
            kwargs.pop("expire_seconds")

            pipe = cache.pipeline()
            method(pipe, key, *args, **kwargs)
            expire_seconds > 0 and pipe.expire(key, expire_seconds) or pipe.persist(key)

            return pipe.execute()[0]
        else:
            return method(cache, key, *args, **kwargs)


    @classmethod
    def get(cls, key, method = Redis.get, *args, **kwargs):
        """
            获取缓存值

            参数:
                expire_seconds  设置过期秒数，0 表示移除过期设置。

            示例:
                get("a", Redis.lrange, 0, -1)
                get("b", Redis.smembers)
                get("c", Redis.zrangebyscore, 0, 1, withscores = True)
                get("d", Redis.hgetall)
                get("d", Redis.hget, "name")
                get("e", Redis.get, expire_secnds = 10)
        """
        return cls.op(key, method, *args, **kwargs)



set_cache = RedisCache.set
del_cache = RedisCache.delete
get_cache = RedisCache.get
op_cache = RedisCache.op
set_hash_cache = partial(set_cache, mode = HASH)
set_list_cache = partial(set_cache, mode = LIST)
set_set_cache = partial(set_cache, mode = SET)
set_sorted_set_cache = partial(set_cache, mode = SORTEDSET)



__all__ = ["set_cache", "del_cache", "get_cache", "op_cache",
        "set_hash_cache", "set_list_cache", "set_set_cache", "set_sorted_set_cache"]
