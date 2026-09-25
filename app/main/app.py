from fastapi import FastAPI, HTTPException
from shared.models import JobStatus, JobResponse, JobRequest
from uuid import uuid4
from shared.redis import RedisCLient

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
    print(f"Process JOB ID: {job_id}")
    print("Creating Redis Client")
    redis_client = RedisCLient()


    print("Save value in Redis DB")
    redis_client.instance.set(
        redis_client.redis_id(job_id=job_id),
        job.model_dump_json()
    )

    print("Save value in Redis Queue")
    redis_client.instance.rpush(
        redis_client.JOBS_QUEUE_NAME,
        job_id
    )

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