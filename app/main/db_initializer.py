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

    def init_outbox(self):
        with self.get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS outbox (
                    id BIGSERIAL PRIMARY KEY,
                    job_id UUID NOT NULL,
                    event_type VARCHAR(50) NOT NULL,
                    payload JSONB NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP NULL
                )
                """
            )