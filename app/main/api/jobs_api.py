from fastapi import APIRouter, Depends, HTTPException

from shared.models import JobRequest, JobResponse
from shared.postgres import PsqlJobRepository
from app.main.services import JobService

router = APIRouter(prefix="/jobs", tags=["Jobs"])


def get_job_service() -> JobService:
    return JobService(psql_job_repo=PsqlJobRepository())


@router.post("", response_model=str)
def create_job_endpoint(
    request: JobRequest,
    service: JobService = Depends(get_job_service),
):
    return service.create_job(request)


@router.get("", response_model=list[JobResponse])
def get_jobs_endpoint(
    service: JobService = Depends(get_job_service),
):
    return service.get_all_jobs()


@router.get("/{job_id}", response_model=JobResponse)
def get_job_endpoint(
    job_id: str,
    service: JobService = Depends(get_job_service),
):
    job = service.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found",
        )

    return job
