from shared.postgres import PsqlClient

class PsqlOutBoxRepository(PsqlClient):

    def __init__(self):
        super().__init__()


    def get_pending_outbox_events(self):
        with self.get_connection() as conn:
            return conn.execute(
                """
                SELECT id, job_id, event_type, payload
                FROM outbox
                WHERE processed_at IS NULL
                ORDER BY id
                """
            ).fetchall()

    def mark_outbox_event_processed(self, event_id: int):
        with self.get_connection() as conn:
            conn.execute(
                """
                UPDATE outbox
                SET processed_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (event_id,),
            )