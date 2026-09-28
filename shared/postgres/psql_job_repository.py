from shared.postgres import PsqlClient
from shared.postgres import PsqlClient
from shared.models import JobStatus, Job, JobResponse
import json
import time
from uuid import UUID

class PsqlJobRepository(PsqlClient):
    def __init__(self):
        super().__init__()

    def update_status(self, job_id: str, status: str):
        time.sleep(3)
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE jobs
                SET status = %s
                WHERE job_id = %s
                """,
                (status, job_id),
            )

    def update_total(self, job_id: str, total: int):
        time.sleep(3)
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE jobs
                SET total = %s
                WHERE job_id = %s
                """,
                (total, job_id),
            )

    def get_job(self, job_id: str) -> Job:
        with self.get_connection() as conn:
            row = conn.execute(
                """
                    SELECT job_id, numbers, total, status
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
            
