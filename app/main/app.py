from fastapi import FastAPI, HTTPException
from shared.models import JobStatus, JobResponse, JobRequest
from uuid import uuid4
from shared.redis import RedisCLient
from shared.postgres import PsqlClient
from contextlib import asynccontextmanager
from app.main.db_initializer import DBInitializer
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("DB Initializing...", flush=True)
    DBInitializer().init_job()
    print("DB Initialized", flush=True)
    yield

app = FastAPI(title="AIOps Lab", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "UP"}


@app.post("/jobs", response_model=str)
def create_job(request: JobRequest):
    job_id = str(uuid4())

    print(f"Process JOB ID: {job_id}")


    print("Save in PSQL DB")
    with PsqlClient().get_connection() as conn:
        conn.execute(
            """
            INSERT INTO jobs (job_id, numbers, total, status)
            VALUES (%s, %s, %s, %s)
            """,
            (
                job_id,
                json.dumps(request.numbers),
                None,
                JobStatus.PENDING.value
            ),
        )

    print("Save value in Redis Queue")
    redis_client = RedisCLient()
    redis_client.instance.rpush(
        RedisCLient.JOBS_QUEUE_NAME,
        job_id
    )

    return job_id

@app.get("/jobs", response_model=list[JobResponse])
def get_jobs():
    with PsqlClient().get_connection() as conn:
        rows = conn.execute(
            """
            SELECT job_id, status, total
            FROM jobs
            """
        ).fetchall()

    return [JobResponse(
        job_id=str(row[0]),
        status=JobStatus(row[1]),
        total=row[2]
    ) for row in rows]

@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str):
    with PsqlClient().get_connection() as conn:
        row = conn.execute(
            """
            SELECT job_id, status, total
            FROM jobs
            WHERE job_id = %s
            """,
            (job_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found",
        )

    return JobResponse(
        job_id=str(row[0]),
        status=JobStatus(row[1]),
        total=row[2]
    )