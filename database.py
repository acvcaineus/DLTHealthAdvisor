import psycopg2
import pandas as pd
import os

class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname=os.environ['PGDATABASE'],
                user=os.environ['PGUSER'],
                password=os.environ['PGPASSWORD'],
                host=os.environ['PGHOST'],
                port=os.environ['PGPORT']
            )
            self.create_tables()
            self.populate_training_data()
            self.populate_framework_data()
        except psycopg2.DatabaseError as e:
            print(f"Error connecting to the database: {e}")
            raise

    def create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS dlt_training_data (
                    id SERIAL PRIMARY KEY,
                    security BOOLEAN,
                    scalability BOOLEAN,
                    energy_efficiency BOOLEAN,
                    governance BOOLEAN,
                    interoperability BOOLEAN,
                    operational_complexity BOOLEAN,
                    implementation_cost BOOLEAN,
                    latency BOOLEAN,
                    framework VARCHAR(50)
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS dlt_frameworks (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50),
                    Security FLOAT,
                    Scalability FLOAT,
                    Energy_Efficiency FLOAT,
                    Governance FLOAT,
                    Interoperability FLOAT,
                    Operational_Complexity FLOAT,
                    Implementation_Cost FLOAT,
                    Latency FLOAT
                )
            ''')
        self.conn.commit()

    def get_training_data(self):
        self.create_tables()  # Ensure table exists
        query = "SELECT * FROM dlt_training_data"
        try:
            return pd.read_sql_query(query, self.conn)
        except Exception as e:
            print(f"Error executing the query: {e}")
            raise

    def populate_training_data(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM dlt_training_data")
            if cur.fetchone()[0] == 0:
                df = pd.read_csv('data/dlt_frameworks.csv')
                for _, row in df.iterrows():
                    cur.execute('''
                        INSERT INTO dlt_training_data (security, scalability, energy_efficiency, governance, interoperability, operational_complexity, implementation_cost, latency, framework)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (True, True, True, True, True, True, True, True, row['name']))
                self.conn.commit()
        except Exception as e:
            print(f"Error populating training data: {e}")
            self.conn.rollback()

    def populate_framework_data(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM dlt_frameworks")
            if cur.fetchone()[0] == 0:
                df = pd.read_csv('data/dlt_frameworks.csv')
                for _, row in df.iterrows():
                    cur.execute('''
                        INSERT INTO dlt_frameworks (name, Security, Scalability, Energy_Efficiency, Governance, Interoperability, Operational_Complexity, Implementation_Cost, Latency)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (row['name'], row['Security'], row['Scalability'], row['Energy Efficiency'], row['Governance'], row['Interoperability'], row['Operational Complexity'], row['Implementation Cost'], row['Latency']))
                self.conn.commit()
        except Exception as e:
            print(f"Error populating framework data: {e}")
            self.conn.rollback()

    def get_framework_data(self, frameworks):
        placeholders = ', '.join(['%s'] * len(frameworks))
        query = f"""
        SELECT * FROM dlt_frameworks
        WHERE name IN ({placeholders})
        """
        try:
            return pd.read_sql_query(query, self.conn, params=frameworks)
        except Exception as e:
            print(f"Error executing the query: {e}")
            raise

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
