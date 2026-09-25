from shared.redis import RedisCLient
from shared.models import JobStatus
import time
from shared.repository import JobRepository


class ProcessJob():

    def __init__(self):
        print("Process Job Initializing...", flush=True)
        self.update_job = JobRepository()
        self.redis_client = RedisCLient().instance
        super().__init__()
        print("Process Job Initialization Complete", flush=True)

    def main(self):
        print(f"Start retrieving jobs from queue {RedisCLient.JOBS_QUEUE_NAME}", flush=True)
        while True:
            result = self.redis_client.blpop(
                RedisCLient.JOBS_QUEUE_NAME,
                timeout=25
            )

            if result is None:
                print("No jobs available, still listening...", flush=True)
                continue

            _, job_id = result

            print(f"Received job {job_id}", flush=True)

            self._process(job_id)


    def _process(self, job_id):
        print(f"Processing job {job_id} from {RedisCLient.JOBS_QUEUE_NAME}", flush=True)

        self.update_job.update_status(job_id=job_id, status=JobStatus.RUNNING.value)

        print(f"Job {job_id} is RUNNING", flush=True)

        # Simulate some operations
        time.sleep(5)

        self.update_job.update_status(job_id=job_id, status=JobStatus.COMPLETED.value)
        print(f"Job {job_id} is COMPLETED", flush=True)

        print(f"Job {job_id} is saved in Psql DB", flush=True)

   

        

if __name__ == '__main__':
    print("Worker Start", flush=True)
    ProcessJob().main()