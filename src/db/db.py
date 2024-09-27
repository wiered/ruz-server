import psycopg2

class DB:
    def __init__(self, dbname, user, host, password):
        self.dbname = dbname
        self.user = user
        self.host = host
        self.password = password

    def connect(self):
        return psycopg2.connect(dbname=self.dbname, user=self.user, host=self.host, password=self.password)
