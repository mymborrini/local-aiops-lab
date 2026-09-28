from shared.redis import RedisCLient
from shared.models import JobStatus, RedisMessage
import time
from shared.redis import RedisJobRepository
from shared.postgres import PsqlJobRepository
from shared.models import Job

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

            print(f"Received job {redisMessage.job_id} event {redisMessage.event_id}", flush=True)

            self._process(redisMessage.job_id)

    def _process(self, job_id):
        print(f"Processing job {job_id} from {RedisCLient.JOBS_QUEUE_NAME}", flush=True)

        self.psql_job_repo.update_status(job_id=job_id, status=JobStatus.RUNNING.value)

        print(f"Job {job_id} is RUNNING", flush=True)

        # Simulate some operations
        job: Job = self.psql_job_repo.get_job(job_id=job_id)
        print(f"Retrieved Job [job_id = {job_id}] saved in db: {job}")
        total = sum(job.numbers)
        time.sleep(5)
        self.psql_job_repo.update_total(job_id=job_id, total=total)

        self.psql_job_repo.update_status(job_id=job_id, status=JobStatus.COMPLETED.value)
        print(f"Job {job_id} is COMPLETED", flush=True)

        print(f"Job {job_id} is saved in Psql DB", flush=True)


if __name__ == "__main__":
    print("Job Processor Start", flush=True)
    JobProcessor().main()
