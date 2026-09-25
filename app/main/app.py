from fastapi import FastAPI, HTTPException
from shared.models import JobStatus, JobResponse, JobRequest
from uuid import uuid4

app = FastAPI(title="AIOps Lab")


jobs: dict[str,JobResponse] = {}

@app.get("/health")
def health():
    return {"status": "UP"}


@app.post("/jobs", response_model=JobResponse)
def create_job(request: JobRequest):
    job_id = str(uuid4())

    job =  JobResponse(
        job_id=job_id,
        status=JobStatus.PENDING
    )

    jobs[job_id] = job

    return job

@app.get("/jobs", response_model=dict[str,JobResponse])
def get_jobs():
    return jobs

@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str):
    job = jobs.get(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )
    return job