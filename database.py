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
                    "Security" FLOAT,
                    "Scalability" FLOAT,
                    "Energy Efficiency" FLOAT,
                    "Governance" FLOAT,
                    "Interoperability" FLOAT,
                    "Operational Complexity" FLOAT,
                    "Implementation Cost" FLOAT,
                    "Latency" FLOAT,
                    name VARCHAR(50)
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS dlt_frameworks (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50),
                    "Security" FLOAT,
                    "Scalability" FLOAT,
                    "Energy Efficiency" FLOAT,
                    "Governance" FLOAT,
                    "Interoperability" FLOAT,
                    "Operational Complexity" FLOAT,
                    "Implementation Cost" FLOAT,
                    "Latency" FLOAT
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL
                )
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS user_comparisons (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    comparison_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        self.conn.commit()

    def get_training_data(self):
        query = '''
        SELECT "Security" as security, "Scalability" as scalability, "Energy Efficiency" as energy_efficiency,
               "Governance" as governance, "Interoperability" as interoperability,
               "Operational Complexity" as operational_complexity, "Implementation Cost" as implementation_cost,
               "Latency" as latency, name as framework
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
                        INSERT INTO dlt_training_data ("Security", "Scalability", "Energy Efficiency", "Governance", "Interoperability", "Operational Complexity", "Implementation Cost", "Latency", name)
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
                        INSERT INTO dlt_frameworks (name, "Security", "Scalability", "Energy Efficiency", "Governance", "Interoperability", "Operational Complexity", "Implementation Cost", "Latency")
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

    def create_user(self, username, password_hash):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
                    (username, password_hash)
                )
                user_id = cur.fetchone()[0]
                self.conn.commit()
                return user_id
        except Exception as e:
            st.error(f"Error creating user: {e}")
            logging.error(f"Error creating user: {e}")
            self.conn.rollback()
            return None

    def get_user(self, user_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id, username, password_hash FROM users WHERE id = %s", (user_id,))
                user = cur.fetchone()
                if user:
                    return {"id": user[0], "username": user[1], "password_hash": user[2]}
                return None
        except Exception as e:
            st.error(f"Error getting user: {e}")
            logging.error(f"Error getting user: {e}")
            return None

    def get_user_by_username(self, username):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
                user = cur.fetchone()
                if user:
                    return {"id": user[0], "username": user[1], "password_hash": user[2]}
                return None
        except Exception as e:
            st.error(f"Error getting user by username: {e}")
            logging.error(f"Error getting user by username: {e}")
            return None

    def save_user_comparison(self, user_id, comparison_data):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO user_comparisons (user_id, comparison_data) VALUES (%s, %s) RETURNING id",
                    (user_id, psycopg2.extras.Json(comparison_data))
                )
                comparison_id = cur.fetchone()[0]
                self.conn.commit()
                return comparison_id
        except Exception as e:
            st.error(f"Error saving user comparison: {e}")
            logging.error(f"Error saving user comparison: {e}")
            self.conn.rollback()
            return None

    def get_user_comparisons(self, user_id):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT id, comparison_data, created_at FROM user_comparisons WHERE user_id = %s ORDER BY created_at DESC",
                    (user_id,)
                )
                comparisons = cur.fetchall()
                return [{"id": c[0], "data": c[1], "created_at": c[2]} for c in comparisons]
        except Exception as e:
            st.error(f"Error getting user comparisons: {e}")
            logging.error(f"Error getting user comparisons: {e}")
            return []

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
