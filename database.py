import psycopg2
import os
import logging
import streamlit as st
import pandas as pd

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='app_errors.log')

class Database:
    def __init__(self):
        try:
            # Conectando ao banco de dados PostgreSQL
            self.conn = psycopg2.connect(
                dbname=os.getenv('PGDATABASE'),
                user=os.getenv('PGUSER'),
                password=os.getenv('PGPASSWORD'),
                host=os.getenv('PGHOST'),
                port=os.getenv('PGPORT')
            )
            logging.info("Successfully connected to the database.")
        except psycopg2.DatabaseError as e:
            st.error(f"Error connecting to the database: {e}")
            logging.error(f"Error connecting to the database: {e}")
            raise

    def get_training_data(self):
        """Retrieves training data from the database."""
        try:
            with self.conn.cursor() as cur:
                cur.execute('''
                    SELECT "Security", "Scalability", "Energy Efficiency", "Governance", "Interoperability", 
                           "Operational Complexity", "Implementation Cost", "Latency", name as framework 
                    FROM dlt_training_data
                ''')
                data = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                df = pd.DataFrame(data, columns=columns)
                if df.empty:
                    st.error("No training data found in the database.")
                    logging.error("No training data found in the database.")
                else:
                    st.success("Training data successfully loaded.")
                    logging.info(f"Training data loaded. Columns: {df.columns.tolist()}")
                    st.write("Available columns in training data:", df.columns.tolist())
                return df
        except psycopg2.Error as e:
            st.error(f"Error retrieving training data: {e}")
            logging.error(f"Error retrieving training data: {e}")
            return pd.DataFrame()

    def get_user_by_username(self, username):
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
                user = cur.fetchone()
                if user:
                    return {'id': user[0], 'username': user[1], 'password_hash': user[2]}
                return None
        except psycopg2.Error as e:
            st.error(f"Error retrieving user: {e}")
            logging.error(f"Error retrieving user {username}: {e}")
            return None

    def create_user(self, username, password_hash):
        try:
            with self.conn.cursor() as cur:
                cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id", (username, password_hash))
                user_id = cur.fetchone()[0]
                self.conn.commit()
                return user_id
        except psycopg2.Error as e:
            st.error(f"Error creating user: {e}")
            logging.error(f"Error creating user {username}: {e}")
            return None

    def __del__(self):
        """Closes the database connection when the Database object is destroyed."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            logging.info("Database connection closed.")
