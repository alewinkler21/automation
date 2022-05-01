import redis

from raspberry.settings import AUTOMATION

redis_conn = redis.Redis(host=AUTOMATION["redis-host"], port=6379, db=0)
