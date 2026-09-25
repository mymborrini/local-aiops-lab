from shared.redis import RedisCLient
import json
from shared.models import JobStatus
import time
from redis import RedisError

class ProcessJob(RedisCLient):

    def __init__(self):
        print("Process Job Initializing...", flush=True)
        super().__init__()
        print("Process Job Initialization Complete", flush=True)

    def main(self):
        print(f"Start retrieving jobs from queue {self.JOBS_QUEUE_NAME}", flush=True)
        while True:
            result = self.instance.blpop(
                self.JOBS_QUEUE_NAME,
                timeout=25
            )

            if result is None:
                print("No jobs available, still listening...", flush=True)
                continue

            _, job_id = result

            print(f"Received job {job_id}", flush=True)

            self._process(job_id)


    def _process(self, job_id):
        print(f"Processing job {job_id} from {self.JOBS_QUEUE_NAME}", flush=True)
        redis_id =  self.redis_id(job_id=job_id)

        job_data = self.instance.get(redis_id)

        if job_data is None:
            print(f"Job {job_id} not found", flush=True)
            return

        job = json.loads(job_data)
        job["status"] = JobStatus.RUNNING

        print(f"Job {job_id} is RUNNING", flush=True)

        # Simulate some operations
        time.sleep(5)

        job["status"] = JobStatus.COMPLETED
        print(f"Job {job_id} is COMPLETED", flush=True)

        self.instance.set(
            redis_id,
            json.dumps(job)
        )

        print(f"Job {job_id} is saved in Redis DB", flush=True)

   

        

if __name__ == '__main__':
    print("Worker Start", flush=True)
    ProcessJob().main()