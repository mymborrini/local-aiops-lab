from shared.redis import RedisCLient


class RedisJobRepository(RedisCLient):
    def __init__(self):
        super().__init__()

    def get_last_job(self, timeout: int = 25):
        return self.instance.blpop(RedisCLient.JOBS_QUEUE_NAME, timeout=timeout)

    def push_job(self, job_id: str):
        self.instance.rpush(RedisCLient.JOBS_QUEUE_NAME, job_id)
        
