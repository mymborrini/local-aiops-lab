import redis


class RedisCLient():

    JOBS_QUEUE_NAME = "jobs"
    
    def __init__(self):
        self.instance = redis.Redis(
            host="redis",
            port=6379,
            decode_responses=True,
            socket_timeout=None
        )
        

    def redis_id(seld, job_id):
        return f"job:{job_id}"

    




