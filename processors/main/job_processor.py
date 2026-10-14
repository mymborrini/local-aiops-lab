from shared.redis import RedisCLient
from shared.models import JobStatus, RedisMessage
import time
from shared.redis import RedisJobRepository
from shared.postgres import PsqlJobRepository
from shared.models import Job
from shared.config.app_properties import MAX_ATTEMPTS
import random
import processors.main.monitoring.job_metrics as JOB_METRIC
from prometheus_client import start_http_server
from shared.config import AiOpsLog, configure_logging


class JobProcessor:
    def __init__(self):
        super().__init__()
        self.log = AiOpsLog("processor.main.job_processor")
        self.log.info("Process Job Initializing...")
        self.redis_job_repo = RedisJobRepository()
        self.psql_job_repo = PsqlJobRepository()
        self.log.info("Process Job Initialization Complete")

    def main(self):
        start_http_server(8001)
        self.log.info(
            f"Start retrieving jobs from queue {RedisCLient.JOBS_QUEUE_NAME}"
        )
        while True:
            redisMessage: RedisMessage = self.redis_job_repo.get_last_job()

            if redisMessage is None:
                self.log.info("No jobs available, still listening...")
                continue

            self.log.info(f"Received message from reds: {redisMessage}")

            self.log.info(
                f"Received job {redisMessage.job_id} event {redisMessage.event_id}",
                job_id=redisMessage.job_id,event_id=redisMessage.event_id, status=JobStatus.PENDING
            )

            self._process(redisMessage.job_id, redisMessage.event_id)

    def _process(self, job_id, event_id):

        if self.psql_job_repo.is_event_processed(event_id=event_id):
            self.log.info(f"Event {event_id} already processed", job_id=job_id, event_id=event_id)
            return

        self.log.info(f"Processing job {job_id} from {RedisCLient.JOBS_QUEUE_NAME}", job_id=job_id, event_id=event_id, status=JobStatus.PENDING)
        job: Job = self.psql_job_repo.get_job(job_id=job_id)
        self.log.info(f"Retrieved Job [job_id = {job_id}] saved in db", job_id=job_id, event_id=event_id, status=job.status)

        if job.status == JobStatus.COMPLETED:
            self.log.info(f"Job {job_id} already completed", job_id=job_id, event_id=event_id, status=JobStatus.COMPLETED)
            return

        with JOB_METRIC.JOB_PROCESSING_DURATION.time():
            self.psql_job_repo.start_job(job_id=job_id)
            JOB_METRIC.JOBS_RUNNING.inc()

            self.log.info(f"Job {job_id} is RUNNING",job_id=job_id, event_id=event_id, status=JobStatus.RUNNING)

            # Simulate some operations

            try:
                total = sum(job.numbers)
                time.sleep(5)

                r: int = random.randint(1, 3)
                self.log.info(f"Job {job_id} lucky number is....{r}", job_id=job_id, event_id=event_id, status=JobStatus.RUNNING)
                if r == 2:
                    raise Exception("Something went wrong")

                self.psql_job_repo.complete_job(
                    job_id=job_id, total=total, event_id=event_id
                )

                JOB_METRIC.JOBS_PROCESSED.labels(result="success").inc()

                self.log.info(f"Job {job_id} is COMPLETED with total {total}", job_id=job_id,event_id=event_id,status=JobStatus.COMPLETED)
            except Exception as exc:
                JOB_METRIC.JOBS_PROCESSED.labels(result="failure").inc()
                self.log.error(f"Job {job_id} failed: {exc}", job_id=job_id, event_id=event_id, status=JobStatus.RUNNING)
                self.psql_job_repo.fail_job(job_id=job_id)

                if job.attempts < MAX_ATTEMPTS:
                    self.redis_job_repo.push_job(job_id=job_id, event_id=event_id)

                    JOB_METRIC.JOB_RETRIES.inc()

                    self.log.info(
                        f"Job {job_id} queued for retry "
                        f"({job.attempts + 1}/{MAX_ATTEMPTS})",
                        job_id=job_id, event_id=event_id, status=JobStatus.RUNNING
                    )
                else:
                    self.log.error(f"Job {job_id} reached maximum attempts", job_id=job_id, event_id=event_id, status=JobStatus.FAILED)
            finally:
                JOB_METRIC.JOBS_RUNNING.dec()


if __name__ == "__main__":
    configure_logging()
    JobProcessor().main()
