from pydantic import BaseModel


class RedisMessage(BaseModel):
    event_id: str
    job_id: str
    correlation_id: str
