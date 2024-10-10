import psycopg2
import os
import logging
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
            logging.error(f"Error connecting to the database: {e}")
            raise

    def create_user(self, username, password_hash):
        """Creates a new user in the database."""
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
                    (username, password_hash)
                )
                self.conn.commit()
                user_id = cur.fetchone()[0]
                logging.info(f"User {username} created with ID {user_id}.")
                return user_id
        except psycopg2.Error as e:
            logging.error(f"Error creating user {username}: {e}")
            return None

    def get_user_by_username(self, username):
        """Fetches user details by username."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
                user = cur.fetchone()
                if user:
                    logging.info(f"User {username} found in the database.")
                    return {'id': user[0], 'username': user[1], 'password_hash': user[2]}
                else:
                    logging.info(f"User {username} not found.")
                    return None
        except psycopg2.Error as e:
            logging.error(f"Error retrieving user {username}: {e}")
            return None

    def get_user_by_id(self, user_id):
        """Fetches user details by user ID."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id, username, password_hash FROM users WHERE id = %s", (user_id,))
                user = cur.fetchone()
                if user:
                    logging.info(f"User with ID {user_id} found in the database.")
                    return {'id': user[0], 'username': user[1], 'password_hash': user[2]}
                else:
                    logging.info(f"User with ID {user_id} not found.")
                    return None
        except psycopg2.Error as e:
            logging.error(f"Error retrieving user by ID {user_id}: {e}")
            return None

    def __del__(self):
        """Closes the database connection when the Database object is destroyed."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            logging.info("Database connection closed.")
