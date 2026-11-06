from shared.postgres.psql_outbox_repository import PsqlOutBoxRepository
from shared.redis.reds_job_repository import RedisJobRepository
import time
import processors.main.monitoring.outbox_metrics as OUTBOX_METRIC
from prometheus_client import start_http_server
from shared.config import AiOpsLog, configure_logging, configure_tracing
from shared.models import JobStatus
from opentelemetry import propagate, trace
from opentelemetry.trace import Status, StatusCode


class OutBoxProcessor:
    def __init__(self):
        self.psql_outbox_repo = PsqlOutBoxRepository()
        self.redis_job_repo = RedisJobRepository()
        self.log = AiOpsLog("processor.main.outbox_processor")
        self.tracer = trace.get_tracer(__name__)

    def process_outbox(self):
        with OUTBOX_METRIC.OUTBOX_PROCESSING_DURATION.time():
            self._process_outbox()

    def _process_outbox(self):
        events = self.psql_outbox_repo.get_pending_outbox_events()

        OUTBOX_METRIC.OUTBOX_PENDING_EVENTS.set(len(events))

        for event_id, job_id, event_type, payload in events:
            correlation_id = payload["correlation_id"]
            trace_context = payload.get("trace_context", {})

            self.log.info(
                f"Processing outbox event {event_id} job {job_id}",
                job_id=job_id,
                event_id=event_id,
                status=JobStatus.PENDING,
                correlation_id=correlation_id,
            )

            parent_context = propagate.extract(trace_context)

            with self.tracer.start_as_current_span(
                "outbox.publish", context=parent_context
            ) as span:
                span.set_attribute("job.id", str(job_id))
                span.set_attribute("outbox.event_id", str(event_id))
                span.set_attribute("messaging.destination.name", "jobs")

                try:
                    self._process_outbox_job(
                        job_id=job_id, event_id=event_id, correlation_id=correlation_id
                    )
                except Exception as exc:
                    span.record_exception(exc)
                    span.set_status(Status(StatusCode.ERROR, str(exc)))

                    OUTBOX_METRIC.OUTBOX_EVENTS_PROCESSED.labels(result="failure").inc()

                    self.log.info(
                        f"Failed to process outbox event {event_id}: {exc}",
                        job_id=job_id,
                        event_id=event_id,
                        status=JobStatus.PENDING,
                        correlation_id=correlation_id,
                    )

    def _process_outbox_job(self, job_id: str, event_id: str, correlation_id: str):

        next_trace_context = {}
        propagate.inject(next_trace_context)

        self.redis_job_repo.push_job(
            job_id=str(job_id),
            event_id=str(event_id),
            correlation_id=correlation_id,
            trace_context=next_trace_context,
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

    def main(self):
        self.log.info("Outbox processor started")

        start_http_server(8001)
        while True:
            self.process_outbox()
            time.sleep(30)


if __name__ == "__main__":
    configure_logging()
    configure_tracing()
    OutBoxProcessor().main()
