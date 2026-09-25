from pydantic import BaseModel
from shared.models.job_status import JobStatus

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus