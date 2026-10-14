from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.main.db_initializer import DBInitializer
from app.main.api import jobs_router, health_router, metrics_router
from app.main.monitoring.middleware import prometheus_middleware
from shared.config import AiOpsLog, configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    log = AiOpsLog(__name__)
    log.info("DB Initializing...")
    db_initializer = DBInitializer()
    db_initializer.init_job()
    log.info("Job table initialized")
    db_initializer.init_outbox()
    log.info("Outbox table initialized")
    db_initializer.processed_event()
    log.info("Processed event initialized")
    log.info("DB Initialized")
    yield


configure_logging()
app = FastAPI(title="AIOps Lab", lifespan=lifespan)

app.middleware("http")(prometheus_middleware)
app.include_router(health_router)
app.include_router(jobs_router)
app.include_router(metrics_router)
