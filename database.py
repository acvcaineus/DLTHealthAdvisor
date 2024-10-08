import psycopg2
import pandas as pd
import os
import streamlit as st
import logging

# Configuração de logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', filename='app_errors.log')

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
            st.write(f"Database connection test result: {self.test_connection()}")
            self.create_tables()
            self.populate_training_data()
            self.populate_framework_data()
        except psycopg2.DatabaseError as e:
            st.error(f"Error connecting to the database: {e}")
            logging.error(f"Error connecting to the database: {e}")
            raise

    def test_connection(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                if result == (1,):
                    st.success("Database connection test successful")
                    return True
                else:
                    st.warning("Unexpected result from database connection test")
                    return False
        except Exception as e:
            st.error(f"Error testing database connection: {e}")
            logging.error(f"Error testing database connection: {e}")
            return False

    def create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS dlt_training_data (
                    id SERIAL PRIMARY KEY,
                    security FLOAT,
                    scalability FLOAT,
                    energy_efficiency FLOAT,
                    governance FLOAT,
                    interoperability FLOAT,
                    operational_complexity FLOAT,
                    implementation_cost FLOAT,
                    latency FLOAT,
                    name VARCHAR(50)
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS dlt_frameworks (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50),
                    security FLOAT,
                    scalability FLOAT,
                    energy_efficiency FLOAT,
                    governance FLOAT,
                    interoperability FLOAT,
                    operational_complexity FLOAT,
                    implementation_cost FLOAT,
                    latency FLOAT
                )
            ''')
        self.conn.commit()

    def get_training_data(self):
        query = '''
        SELECT security, scalability, energy_efficiency, 
               governance, interoperability, 
               operational_complexity, implementation_cost, 
               latency, name as framework 
        FROM dlt_training_data
        '''
        try:
            return pd.read_sql_query(query, self.conn)
        except Exception as e:
            st.error(f"Error executing the query: {e}")
            logging.error(f"Error executing the query: {e}")
            raise

    def populate_training_data(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM dlt_training_data")
            if cur.fetchone()[0] == 0:
                df = pd.read_csv('data/dlt_frameworks.csv')
                for _, row in df.iterrows():
                    cur.execute('''
                        INSERT INTO dlt_training_data (security, scalability, energy_efficiency, governance, interoperability, operational_complexity, implementation_cost, latency, name)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (row['Security'], row['Scalability'], row['Energy Efficiency'], row['Governance'], row['Interoperability'], row['Operational Complexity'], row['Implementation Cost'], row['Latency'], row['name']))
                self.conn.commit()
                st.success("Training data populated successfully")
            else:
                st.info("Training data already populated")
        except Exception as e:
            st.error(f"Error populating training data: {e}")
            logging.error(f"Error populating training data: {e}")
            self.conn.rollback()

    def populate_framework_data(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT COUNT(*) FROM dlt_frameworks")
            if cur.fetchone()[0] == 0:
                df = pd.read_csv('data/dlt_frameworks.csv')
                for _, row in df.iterrows():
                    cur.execute('''
                        INSERT INTO dlt_frameworks (name, security, scalability, energy_efficiency, governance, interoperability, operational_complexity, implementation_cost, latency)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (row['name'], row['Security'], row['Scalability'], row['Energy Efficiency'], row['Governance'], row['Interoperability'], row['Operational Complexity'], row['Implementation Cost'], row['Latency']))
                self.conn.commit()
                st.success("Framework data populated successfully")
            else:
                st.info("Framework data already populated")
        except Exception as e:
            st.error(f"Error populating framework data: {e}")
            logging.error(f"Error populating framework data: {e}")
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
            st.error(f"Error executing the query: {e}")
            logging.error(f"Error executing the query: {e}")
            raise

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
