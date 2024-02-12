import redis
from typing import Optional


class Redis:
    connection: Optional[redis.Redis] = None


def get_redis_connection(host: str, port: int, db: int) -> redis.Redis:
    if Redis.connection is None:
        Redis.connection = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    return Redis.connection


def get_redis_instance_pool(host: str, port: int, db: int, password: Optional[str] = None) -> redis.Redis:
    redis_pool = redis.ConnectionPool(host=host, port=port, db=db, password=password)
    redis_instance = redis.StrictRedis(connection_pool=redis_pool)

    return redis_instance
