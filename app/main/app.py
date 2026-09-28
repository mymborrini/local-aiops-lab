from fastapi import FastAPI, HTTPException
from shared.models import JobStatus, JobResponse, JobRequest
from uuid import uuid4
from shared.redis import RedisJobRepository
from shared.postgres import PsqlJobRepository
from contextlib import asynccontextmanager
from app.main.db_initializer import DBInitializer
import json


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("DB Initializing...", flush=True)
    db_initializer = DBInitializer()
    db_initializer.init_job()
    print("Job table initialized")
    db_initializer.init_outbox()
    print("Outbox table initialized")
    print("DB Initialized", flush=True)
    yield


app = FastAPI(title="AIOps Lab", lifespan=lifespan)


@app.get("/health")
def health_endpoint():
    return {"status": "UP"}


@app.post("/jobs", response_model=str)
def create_job_endpoint(request: JobRequest):
    job_id = str(uuid4())
    psql_job_repo = PsqlJobRepository()
    redis_job_repo = RedisJobRepository()

    print(f"Process JOB ID: {job_id}")

    print("Save in PSQL DB")
    psql_job_repo.create_job(job_id, json.dumps(request.numbers), JobStatus.PENDING.value)

    print("Save value in Redis Queue")
    # redis_job_repo.push_job(job_id=job_id)

    return job_id


@app.get("/jobs", response_model=list[JobResponse])
def get_jobs_endpoint():

    psql_job_repo = PsqlJobRepository()
    return psql_job_repo.get_all_jobs()

    


@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job_endpoint(job_id: str):

    psql_job_repo = PsqlJobRepository()
    job_response = psql_job_repo.get_job(job_id=job_id)
    if job_response is None:
        raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found",
            )
    return job_response