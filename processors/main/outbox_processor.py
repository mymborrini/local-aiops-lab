from shared.postgres.psql_outbox_repository import PsqlOutBoxRepository
from shared.redis.reds_job_repository import RedisJobRepository
import time

class OutBoxProcessor:

    def __init__(self):
        self.psql_outbox_repo = PsqlOutBoxRepository()
        self.redis_job_repo = RedisJobRepository()

    def process_outbox(self):
        events = self.psql_outbox_repo.get_pending_outbox_events()

        for event_id, job_id, event_type, payload in events:
            print(f"Processing outbox event {event_id}", flush=True)

            try:
                self.redis_job_repo.push_job(job_id=str(job_id), event_id=str(event_id))

                self.psql_outbox_repo.mark_outbox_event_processed(event_id)

                print(f"Outbox event {event_id} processed", flush=True)

            except Exception as exc:
                print(f"Failed to process outbox event {event_id}: {exc}")

    def main(self):
        print("Outbox processor started", flush=True)

        while True:
            self.process_outbox()
            time.sleep(30)

if __name__ == '__main__':
    print("Out box Processor Start", flush=True)
    OutBoxProcessor().main()