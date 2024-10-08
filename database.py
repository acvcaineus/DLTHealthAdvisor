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
            st.write("Conexão com o banco de dados estabelecida com sucesso.")
            self.create_tables()  # Cria as tabelas necessárias caso ainda não existam
        except psycopg2.DatabaseError as e:
            st.error(f"Erro ao conectar ao banco de dados: {e}")
            logging.error(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def create_tables(self):
        """Cria as tabelas necessárias no banco de dados se ainda não existirem."""
        try:
            with self.conn.cursor() as cur:
                # Criação da tabela de usuários
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) NOT NULL UNIQUE,
                        password_hash VARCHAR(255) NOT NULL
                    );
                """)

                # Criação da tabela de perguntas do framework
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS perguntasframework (
                        id SERIAL PRIMARY KEY,
                        descricao TEXT NOT NULL,
                        camada_shermin TEXT,
                        caracteristica_algoritmo TEXT,
                        impacto TEXT,
                        ramificacao_sim INTEGER,
                        ramificacao_nao INTEGER
                    );
                """)

                # Criação da tabela de respostas dos usuários
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS respostasusuarios (
                        id SERIAL PRIMARY KEY,
                        id_pergunta INTEGER NOT NULL REFERENCES perguntasframework(id),
                        resposta VARCHAR(3) NOT NULL,  -- Sim ou Não
                        id_usuario INTEGER NOT NULL REFERENCES users(id)
                    );
                """)

                # Criação da tabela de frameworks de DLT
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS dlt_frameworks (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(50) NOT NULL UNIQUE,
                        security DOUBLE PRECISION,
                        scalability DOUBLE PRECISION,
                        energy_efficiency DOUBLE PRECISION,
                        governance DOUBLE PRECISION,
                        interoperability DOUBLE PRECISION,
                        operational_complexity DOUBLE PRECISION,
                        implementation_cost DOUBLE PRECISION,
                        latency DOUBLE PRECISION,
                        security_score NUMERIC,
                        scalability_score NUMERIC,
                        energy_efficiency_score NUMERIC,
                        governance_score NUMERIC,
                        interoperability_score NUMERIC,
                        operational_complexity_score NUMERIC,
                        implementation_cost_score NUMERIC,
                        latency_score NUMERIC,
                        example_algorithms VARCHAR(255)
                    );
                """)

                # Criação da tabela de algoritmos de consenso
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS dlt_consensus_algorithms (
                        id SERIAL PRIMARY KEY,
                        algorithm_name VARCHAR(50) NOT NULL UNIQUE,
                        consensus_group VARCHAR(100),
                        description TEXT,
                        caracteristica_prioritaria TEXT,
                        casos_de_uso TEXT[],
                        principais_caracteristicas TEXT
                    );
                """)

                # Criação da tabela para os casos de uso de frameworks
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS dlt_framework_use_cases (
                        framework_id INTEGER REFERENCES dlt_frameworks(id),
                        use_case_id INTEGER REFERENCES dlt_use_cases(id),
                        relevant_criteria TEXT
                    );
                """)

                # Criação da tabela de pontuação dos frameworks
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS pontuacaoframeworks (
                        id SERIAL PRIMARY KEY,
                        id_framework INTEGER REFERENCES dlt_frameworks(id),
                        id_usuario INTEGER REFERENCES users(id),
                        pontuacao NUMERIC,
                        framework_score NUMERIC
                    );
                """)

                # Criação da tabela de comparações de frameworks
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS comparacaoframeworks (
                        id SERIAL PRIMARY KEY,
                        id_framework_1 INTEGER REFERENCES dlt_frameworks(id),
                        id_framework_2 INTEGER REFERENCES dlt_frameworks(id),
                        metrica1 TEXT,
                        metrica2 TEXT,
                        descricao_comparacao TEXT
                    );
                """)

                # Criação da tabela de métricas de árvore de decisão
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS metricasdecisiontree (
                        id SERIAL PRIMARY KEY,
                        id_framework INTEGER REFERENCES dlt_frameworks(id),
                        id_algoritmo INTEGER REFERENCES dlt_consensus_algorithms(id),
                        valor_metrica NUMERIC,
                        metrica TEXT
                    );
                """)

                # Criação da tabela para dados de treinamento
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS dlt_training_data (
                        id SERIAL PRIMARY KEY,
                        framework VARCHAR(50),
                        Security DOUBLE PRECISION,
                        Scalability DOUBLE PRECISION,
                        Energy_efficiency BOOLEAN,
                        Governance DOUBLE PRECISION,
                        Operational_Complexity DOUBLE PRECISION,
                        Latency DOUBLE PRECISION,
                        Integration BOOLEAN,
                        Interoperability DOUBLE PRECISION,
                        Implementation_Cost DOUBLE PRECISION,
                        Privacy BOOLEAN,
                        Data_Volume BOOLEAN
                    );
                """)

                self.conn.commit()
                st.write("Tabelas criadas com sucesso.")
        except psycopg2.Error as e:
            st.error(f"Erro ao criar tabelas: {e}")
            logging.error(f"Erro ao criar tabelas: {e}")
            self.conn.rollback()

    def create_user(self, username, password_hash):
        """Insere um novo usuário no banco de dados."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cur.fetchone():
                    st.warning(f"O usuário {username} já existe.")
                    return None

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

    def __del__(self):
        """Fecha a conexão com o banco de dados quando o objeto Database for destruído."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
