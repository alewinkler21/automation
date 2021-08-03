import redis

from raspberry.settings import AUTOMATION

redis = redis.Redis(host=AUTOMATION["redis-host"], port=6379, db=0)
