from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.main.db_initializer import DBInitializer
from app.main.api import jobs_router, health_router, metrics_router
from app.main.monitoring.middleware import prometheus_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("DB Initializing...", flush=True)
    db_initializer = DBInitializer()
    db_initializer.init_job()
    print("Job table initialized")
    db_initializer.init_outbox()
    print("Outbox table initialized")
    db_initializer.processed_event()
    print("Processed event initialized")
    print("DB Initialized", flush=True)
    yield


app = FastAPI(title="AIOps Lab", lifespan=lifespan)

app.middleware("http")(prometheus_middleware)
app.include_router(health_router)
app.include_router(jobs_router)
app.include_router(metrics_router)
