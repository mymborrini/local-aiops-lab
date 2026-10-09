import psycopg
from shared.config.app_properties import *


class PsqlClient:
    def get_connection(self):
        return psycopg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )
