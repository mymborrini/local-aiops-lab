import redis
from shared.config.app_properties import *


class RedisCLient:
    JOBS_QUEUE_NAME = "jobs"

    def __init__(self):
        self.instance = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_timeout=None
        )

    def redis_id(seld, job_id):
        return f"job:{job_id}"
