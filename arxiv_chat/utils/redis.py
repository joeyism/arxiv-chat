from .constants import REDIS_HOST
import redis

client = redis.Redis(host=REDIS_HOST, port=6379)
