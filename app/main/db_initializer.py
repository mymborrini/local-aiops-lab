from shared.postgres import PsqlClient


class DBInitializer(PsqlClient):
    def __init__(self):
        super().__init__()

    def init_job(self):
        with self.get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id UUID PRIMARY KEY,
                    numbers JSONB NOT NULL,
                    total BIGINT,
                    status VARCHAR(20) NOT NULL
                )
                """
            )
