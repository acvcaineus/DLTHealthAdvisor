import psycopg2
import os
import logging
import streamlit as st

# Configuração de logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', filename='app_errors.log')

class Database:
    def __init__(self):
        try:
            # Conectando ao banco de dados PostgreSQL
            self.conn = psycopg2.connect(
                dbname=os.environ['PGDATABASE'],
                user=os.environ['PGUSER'],
                password=os.environ['PGPASSWORD'],
                host=os.environ['PGHOST'],
                port=os.environ['PGPORT']
            )
        except psycopg2.DatabaseError as e:
            st.error(f"Error connecting to the database: {e}")
            logging.error(f"Error connecting to the database: {e}")
            raise

    def create_user(self, username, password_hash):
        """
        Insere um novo usuário na tabela 'users' no banco de dados.
        Retorna o id do usuário se for bem-sucedido, None se o usuário já existir.
        """
        try:
            with self.conn.cursor() as cur:
                # Verifica se o usuário já existe
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cur.fetchone():
                    st.warning(f"O usuário {username} já existe.")
                    return None

                # Insere o novo usuário
                cur.execute(
                    "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
                    (username, password_hash)
                )
                user_id = cur.fetchone()[0]
                self.conn.commit()
                logging.info(f"Usuário criado com sucesso: {username}")
                return user_id
        except psycopg2.Error as e:
            st.error(f"Erro ao criar usuário no banco de dados: {e}")
            logging.error(f"Erro ao criar usuário {username}: {e}")
            self.conn.rollback()
            return None
        except Exception as e:
            st.error(f"Erro inesperado ao criar usuário: {e}")
            logging.error(f"Erro inesperado ao criar usuário {username}: {e}")
            self.conn.rollback()
            return None

    def __del__(self):
        """
        Fecha a conexão com o banco de dados quando o objeto Database for destruído.
        """
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
