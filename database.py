import psycopg2
import os
import logging
import streamlit as st
import pandas as pd

# Configuração de logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', filename='app_errors.log')

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
        except psycopg2.DatabaseError as e:
            st.error(f"Erro ao conectar ao banco de dados: {e}")
            logging.error(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def get_training_data(self):
        """Recupera os dados de treinamento do banco de dados."""
        try:
            with self.conn.cursor() as cur:
                cur.execute('''
                    SELECT *
                    FROM dlt_training_data
                ''')
                data = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                df = pd.DataFrame(data, columns=columns)
                if df.empty:
                    st.error("No training data found in the database.")
                    logging.error("No training data found in the database.")
                else:
                    st.write("Available columns in training data:", df.columns.tolist())
                    logging.info(f"Available columns in training data: {df.columns.tolist()}")
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

    def __del__(self):
        """Fecha a conexão com o banco de dados quando o objeto Database for destruído."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
