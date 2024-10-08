import psycopg2
import pandas as pd
import os
import streamlit as st
import logging
import psycopg2.extras

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

    # ... [other methods remain unchanged] ...

    def create_user(self, username, password_hash):
        try:
            with self.conn.cursor() as cur:
                # Check if user already exists
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cur.fetchone():
                    st.warning(f"User {username} already exists")
                    logging.warning(f"Attempted to create existing user: {username}")
                    return None
                
                cur.execute(
                    "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
                    (username, password_hash)
                )
                user_id = cur.fetchone()[0]
                self.conn.commit()
                logging.info(f"User created successfully: {username}")
                return user_id
        except psycopg2.Error as e:
            st.error(f"Database error when creating user: {e}")
            logging.error(f"Database error when creating user {username}: {e}")
            self.conn.rollback()
            return None
        except Exception as e:
            st.error(f"Unexpected error when creating user: {e}")
            logging.error(f"Unexpected error when creating user {username}: {e}")
            self.conn.rollback()
            return None

    # ... [other methods remain unchanged] ...

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
