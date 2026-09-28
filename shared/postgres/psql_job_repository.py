from shared.postgres import PsqlClient
from shared.postgres import PsqlClient
from shared.models import JobResponse, JobStatus, Job
import json
import time


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

        return Job(
            job_id=str(row[0]),
            status=JobStatus(row[3]),
            total=row[2],
            numbers=row[1],
        )
