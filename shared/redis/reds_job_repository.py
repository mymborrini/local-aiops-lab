from shared.redis import RedisCLient
from shared.models import RedisMessage


class RedisJobRepository(RedisCLient):
    def __init__(self):
        super().__init__()

    def get_last_job(self, timeout: int = 25) -> RedisMessage:
        response = self.instance.blpop(RedisCLient.JOBS_QUEUE_NAME, timeout=timeout)
        if response is None:
            return None
        return RedisMessage.model_validate_json(response[1])

    def push_job(self, job_id: str, event_id: str, correlation_id: str, trace_context: object):

        message = RedisMessage(
            event_id=event_id, job_id=job_id, correlation_id=correlation_id, trace_context=trace_context
        )

        self.instance.rpush(RedisCLient.JOBS_QUEUE_NAME, message.model_dump_json())
