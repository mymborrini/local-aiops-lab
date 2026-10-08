from shared.postgres import PsqlClient
from shared.postgres import PsqlClient
from shared.models import JobStatus, Job, JobResponse
import json
import time
from uuid import UUID

class PsqlJobRepository(PsqlClient):
    def __init__(self):
        super().__init__()


    def get_job(self, job_id: str) -> Job:
        with self.get_connection() as conn:
            row = conn.execute(
                """
                    SELECT job_id, numbers, total, status, attempts
                    FROM jobs
                    WHERE job_id = %s
                    """,
                (job_id,),
            ).fetchone()

        if row is None:
            return None
        

        return Job(
            job_id=str(row[0]),
            status=JobStatus(row[3]),
            total=row[2],
            numbers=json.loads(row[1]),
            attempts=row[4]
        )

    def get_all_jobs(self) -> list[JobResponse]:
        with self.get_connection() as conn:
                rows = conn.execute(
                    """
                    SELECT job_id, status, total
                    FROM jobs
                    """
                ).fetchall()

        return [
                JobResponse(job_id=str(row[0]), status=JobStatus(row[1]), total=row[2])
                for row in rows
            ]


    def create_job(
        self,
        job_id: UUID,
        numbers: list[float],
        status: str,
    ):

        # With get_connection + Exception -> Everything is rolled back
        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO jobs (job_id, numbers, status)
                VALUES (%s, %s, %s)
                """,
                (
                    job_id,
                    json.dumps(numbers),
                    status,
                ),
            )


            conn.execute(
                """
                INSERT INTO outbox (job_id, event_type, payload)
                VALUES (%s, %s, %s)
                """,
                (
                    job_id,
                    "JOB_CREATED",
                    json.dumps(
                        {
                            "job_id": str(job_id),
                        }
                    ),
                ),
            )
            

    def is_event_processed(self, event_id: int):
        with self.get_connection() as conn:
             row = conn.execute(
                """
                SELECT 1
                FROM processed_events
                WHERE event_id = %s
                """,
                (event_id,),
            ).fetchone()

        return row is not None


    def complete_job(self, job_id: str, event_id: int, total: int):
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE jobs
                SET status = %s,
                    total = %s
                WHERE job_id = %s
                """,
                ("COMPLETED", total, job_id),
            )

            conn.execute(
                """
                INSERT INTO processed_events (event_id)
                VALUES (%s)
                ON CONFLICT (event_id) DO NOTHING
                """,
                (event_id,),
            )

    def start_job(self, job_id: str):
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE jobs
                SET status = %s,
                    attempts = attempts + 1
                WHERE job_id = %s
                """,
                ("RUNNING", job_id),
            )

    def fail_job(self, job_id: str):
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE jobs
                SET status = %s
                WHERE job_id = %s
                """,
                ("FAILED", job_id),
            )