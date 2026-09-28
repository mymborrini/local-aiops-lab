from pydantic import BaseModel
from shared.models.job_status import JobStatus


class Job(BaseModel):
    job_id: str
    status: JobStatus
    total: int | None = None
    numbers: list[float]