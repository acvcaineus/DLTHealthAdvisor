import psycopg2
import pandas as pd
import os

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.environ['PGDATABASE'],
            user=os.environ['PGUSER'],
            password=os.environ['PGPASSWORD'],
            host=os.environ['PGHOST'],
            port=os.environ['PGPORT']
        )

    def get_training_data(self):
        query = "SELECT * FROM dlt_training_data"
        return pd.read_sql_query(query, self.conn)

    def get_framework_data(self, frameworks):
        placeholders = ', '.join(['%s'] * len(frameworks))
        query = f"""
        SELECT * FROM dlt_frameworks
        WHERE name IN ({placeholders})
        """
        return pd.read_sql_query(query, self.conn, params=frameworks)

    def __del__(self):
        self.conn.close()
