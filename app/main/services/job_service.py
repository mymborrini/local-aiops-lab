from shared.postgres import PsqlJobRepository
from uuid import uuid4
import json

from shared.models import JobRequest, JobResponse, JobStatus


class JobService:
    def __init__(self, psql_job_repo: PsqlJobRepository):
        self.psql_job_repo = psql_job_repo

    def create_job(self, request: JobRequest) -> str:
        job_id = str(uuid4())

        print(f"Process JOB ID: {job_id}")

        self.psql_job_repo.create_job(
            job_id,
            json.dumps(request.numbers),
            JobStatus.PENDING.value,
        )

        print(f"JOB ID: {job_id} Save in PSQL DB")

        return job_id

    def get_all_jobs(self) -> list[JobResponse]:
        return self.psql_job_repo.get_all_jobs()

    def get_job(self, job_id: str) -> JobResponse | None:
        return self.psql_job_repo.get_job(job_id=job_id)
