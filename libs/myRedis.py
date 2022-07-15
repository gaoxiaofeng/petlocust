import redis
from enum import Enum


# from conf.config import REDIS
#
# class MyRedis(object):
#     def __init__(self, host=REDIS.get('ip'), port=REDIS.get('port'), password=REDIS.get('password'),
#                  db=REDIS.get('db').get('smooth')):
#         pool = redis.ConnectionPool(host=host, port=port, password=password,
#                                     decode_responses=True, db=db)
#         self.r = redis.Redis(connection_pool=pool)
#
#     @property
#     def db(self):
#         return self.r
#
#     def rm_smooth(self, interactId):
#         self.r.delete(f'SMOOTH:LiveAnswerDetail_interactId:{interactId}')


class RedisDbIndexEnum(Enum):
    smooth = 35
    local = 15


_smooth_redis_connect_pool = redis.ConnectionPool(host='r-2zekb0d3dkty455vff.redis.rds.aliyuncs.com',
                                                  password='EemaeV2gQA',
                                                  port=6379,
                                                  db=RedisDbIndexEnum.smooth.value,
                                                  max_connections=5)

_local_redis_connect_pool = redis.ConnectionPool(host='10.120.0.14',
                                                 password='YoukaTest112',
                                                 port=6390,
                                                 db=RedisDbIndexEnum.local.value,
                                                 max_connections=10)

_smooth_redis = redis.Redis(connection_pool=_smooth_redis_connect_pool, decode_responses=True)
_local_redis = redis.Redis(connection_pool=_local_redis_connect_pool, decode_responses=True)


def getRedisSession(redisDbIndex: RedisDbIndexEnum = RedisDbIndexEnum.local):
    if redisDbIndex == RedisDbIndexEnum.smooth:
        return _smooth_redis
    elif redisDbIndex == RedisDbIndexEnum.local:
        return _local_redis
