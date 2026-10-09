from shared.redis import RedisCLient
from shared.models import JobStatus, RedisMessage
import time
from shared.redis import RedisJobRepository
from shared.postgres import PsqlJobRepository
from shared.models import Job
from shared.config.app_properties import MAX_ATTEMPTS
import random


class JobProcessor:
    def __init__(self):
        super().__init__()
        print("Process Job Initializing...", flush=True)
        self.redis_job_repo = RedisJobRepository()
        self.psql_job_repo = PsqlJobRepository()
        print("Process Job Initialization Complete", flush=True)

    def main(self):
        print(
            f"Start retrieving jobs from queue {RedisCLient.JOBS_QUEUE_NAME}",
            flush=True,
        )
        while True:
            redisMessage: RedisMessage = self.redis_job_repo.get_last_job()

            if redisMessage is None:
                print("No jobs available, still listening...", flush=True)
                continue

            print(f"Received message from reds: {redisMessage}")

            print(
                f"Received job {redisMessage.job_id} event {redisMessage.event_id}",
                flush=True,
            )

            self._process(redisMessage.job_id, redisMessage.event_id)

    def _process(self, job_id, event_id):

        if self.psql_job_repo.is_event_processed(event_id=event_id):
            print(f"Event {event_id} already processed")
            return

        print(f"Processing job {job_id} from {RedisCLient.JOBS_QUEUE_NAME}", flush=True)
        job: Job = self.psql_job_repo.get_job(job_id=job_id)
        print(f"Retrieved Job [job_id = {job_id}] saved in db", flush=True)

        if job.status == JobStatus.COMPLETED:
            print(f"Job {job_id} already completed")
            return

        self.psql_job_repo.start_job(job_id=job_id)

        print(f"Job {job_id} is RUNNING", flush=True)

        # Simulate some operations

        total = sum(job.numbers)

        try:
            time.sleep(5)

            if random.randint(1, 6) == 6:
                raise Exception("Something went wrong")

            self.psql_job_repo.complete_job(
                job_id=job_id, total=total, event_id=event_id
            )

            print(f"Job {job_id} is COMPLETED with total {total}", flush=True)
        except Exception as exc:
            print(f"Job {job_id} failed: {exc}")
            self.psql_job_repo.fail_job(job_id=job_id)

            if job.attempts < MAX_ATTEMPTS:
                self.redis_job_repo.push_job(job_id=job_id, event_id=event_id)

                print(
                    f"Job {job_id} queued for retry "
                    f"({job.attempts + 1}/{MAX_ATTEMPTS})",
                    flush=True,
                )
            else:
                print(f"Job {job_id} reached maximum attempts", flush=True)


if __name__ == "__main__":
    print("Job Processor Start", flush=True)
    JobProcessor().main()
