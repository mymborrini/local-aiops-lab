import psycopg

class PsqlClient():

    def __init__(self):
        self._db_name = "jobs"
        self._db_user = "jobs"
        self.__db_psw = "jobs"
        

    def get_connection(self):
        return psycopg.connect(
            host="postgres",
            port=5432,
            dbname=self._db_name,
            user=self._db_user,
            password=self.__db_psw,
        )