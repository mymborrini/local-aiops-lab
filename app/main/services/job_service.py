from shared.postgres import PsqlJobRepository
from uuid import uuid4
import json
from shared.config import AiOpsLog

from shared.models import JobRequest, JobResponse, JobStatus
from opentelemetry import propagate


class JobService:
    def __init__(self, psql_job_repo: PsqlJobRepository):
        self.psql_job_repo = psql_job_repo
        self.log = AiOpsLog(__name__)

    def create_job(self, request: JobRequest) -> str:
        job_id = str(uuid4())
        correlation_id = uuid4()
        trace_context = {}
        propagate.inject(trace_context)

        self.log.info(
            f"Process JOB ID: {job_id}",
            job_id=job_id,
            status=JobStatus.PENDING,
            correlation_id=correlation_id,
        )

        self.psql_job_repo.create_job(
            job_id,
            json.dumps(request.numbers),
            JobStatus.PENDING.value,
            correlation_id=correlation_id,
            trace_context=trace_context
        )

        self.log.info(
            f"JOB ID: {job_id} Save in PSQL DB",
            job_id=job_id,
            status=JobStatus.PENDING,
            correlation_id=correlation_id,
        )

        return job_id

    def get_all_jobs(self) -> list[JobResponse]:
        return self.psql_job_repo.get_all_jobs()

    def get_job(self, job_id: str) -> JobResponse | None:
        return self.psql_job_repo.get_job(job_id=job_id)
