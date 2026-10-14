from shared.postgres.psql_outbox_repository import PsqlOutBoxRepository
from shared.redis.reds_job_repository import RedisJobRepository
import time
import processors.main.monitoring.outbox_metrics as OUTBOX_METRIC
from prometheus_client import start_http_server
from shared.config import AiOpsLog, configure_logging
from shared.models import JobStatus


class OutBoxProcessor:
    def __init__(self):
        self.psql_outbox_repo = PsqlOutBoxRepository()
        self.redis_job_repo = RedisJobRepository()
        self.log = AiOpsLog("processor.main.outbox_processor")

    def process_outbox(self):
        with OUTBOX_METRIC.OUTBOX_PROCESSING_DURATION.time():
            self._process_outbox()

    def _process_outbox(self):
        events = self.psql_outbox_repo.get_pending_outbox_events()

        OUTBOX_METRIC.OUTBOX_PENDING_EVENTS.set(len(events))

        for event_id, job_id, event_type, payload in events:
            correlation_id = payload["correlation_id"]
            self.log.info(
                f"Processing outbox event {event_id} job {job_id}",
                job_id=job_id,
                event_id=event_id,
                status=JobStatus.PENDING,
                correlation_id=correlation_id,
            )

            try:
                self.redis_job_repo.push_job(
                    job_id=str(job_id),
                    event_id=str(event_id),
                    correlation_id=correlation_id,
                )

                self.psql_outbox_repo.mark_outbox_event_processed(event_id)

                OUTBOX_METRIC.OUTBOX_EVENTS_PROCESSED.labels(result="success").inc()

                self.log.info(
                    f"Outbox event {event_id} job {job_id} processed",
                    job_id=job_id,
                    event_id=event_id,
                    status=JobStatus.PENDING,
                    correlation_id=correlation_id,
                )

            except Exception as exc:
                OUTBOX_METRIC.OUTBOX_EVENTS_PROCESSED.labels(result="failure").inc()

                self.log.info(
                    f"Failed to process outbox event {event_id}: {exc}",
                    job_id=job_id,
                    event_id=event_id,
                    status=JobStatus.PENDING,
                    correlation_id=correlation_id,
                )

    def main(self):
        self.log.info("Outbox processor started")

        start_http_server(8001)
        while True:
            self.process_outbox()
            time.sleep(30)


if __name__ == "__main__":
    configure_logging()
    OutBoxProcessor().main()
