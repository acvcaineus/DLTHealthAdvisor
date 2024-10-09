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
            # Conectando ao banco de dados PostgreSQL com variáveis de ambiente
            self.conn = psycopg2.connect(
                dbname=os.getenv('PGDATABASE'),
                user=os.getenv('PGUSER'),
                password=os.getenv('PGPASSWORD'),
                host=os.getenv('PGHOST'),
                port=os.getenv('PGPORT')
            )
            self.create_tables()  # Cria as tabelas necessárias caso ainda não existam
            self.inserir_perguntas()  # Insere as perguntas no banco de dados caso não estejam inseridas
        except psycopg2.DatabaseError as e:
            st.error(f"Erro ao conectar ao banco de dados: {e}")
            logging.error(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def create_tables(self):
        """Cria as tabelas necessárias no banco de dados se ainda não existirem."""
        try:
            with self.conn.cursor() as cur:
                # Criação da tabela de usuários com índice único
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) NOT NULL UNIQUE,
                        password_hash VARCHAR(255) NOT NULL,
                        CONSTRAINT unique_username UNIQUE (username)
                    );
                """)
                # Índice para melhorar buscas por nome de usuário
                cur.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")

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

                # Criação da tabela de respostas dos usuários com índice
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS respostasusuarios (
                        id SERIAL PRIMARY KEY,
                        id_pergunta INTEGER NOT NULL REFERENCES perguntasframework(id),
                        resposta VARCHAR(3) NOT NULL,  -- Sim ou Não
                        id_usuario INTEGER NOT NULL REFERENCES users(id),
                        CONSTRAINT unique_resposta_pergunta UNIQUE (id_pergunta, id_usuario)
                    );
                """)
                # Índice para melhorar performance de buscas por usuário e pergunta
                cur.execute("CREATE INDEX IF NOT EXISTS idx_respostasusuarios_usuario ON respostasusuarios(id_usuario);")

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

                # Criação da tabela de pontuação dos frameworks com constraint de unicidade
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS pontuacaoframeworks (
                        id SERIAL PRIMARY KEY,
                        id_framework VARCHAR(50),
                        id_usuario INTEGER REFERENCES users(id),
                        pontuacao NUMERIC,
                        framework_score NUMERIC,
                        CONSTRAINT unique_pontuacao_usuario_framework UNIQUE (id_framework, id_usuario)
                    );
                """)
                # Índice para buscas rápidas por frameworks e usuários
                cur.execute("CREATE INDEX IF NOT EXISTS idx_pontuacaoframeworks_usuario ON pontuacaoframeworks(id_usuario);")

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

                # Adicionar índice para melhorar buscas por frameworks
                cur.execute("CREATE INDEX IF NOT EXISTS idx_dlt_training_data_framework ON dlt_training_data(framework);")

                self.conn.commit()  # Confirma as alterações
        except psycopg2.Error as e:
            st.error(f"Erro ao criar tabelas: {e}")
            logging.error(f"Erro ao criar tabelas: {e}")
            self.conn.rollback()

    def inserir_perguntas(self):
        """Insere as perguntas do framework na tabela 'perguntasframework'."""
        perguntas = [
            ('A aplicação exige alta privacidade e controle centralizado?', 'Camada de Aplicação', 'Alta Privacidade', 'Se Sim, direciona para DLTs permissionadas.', 2, 3),
            ('A rede precisa integrar-se a sistemas legados de saúde (ex: EHRs, bancos de dados hospitalares)?', 'Camada de Aplicação', 'Integração com Sistemas Legados', 'Se Sim, sugere DLTs com alto suporte à interoperabilidade.', 4, 5),
            ('A rede precisa garantir segurança de dados sensíveis (ex: prontuários eletrônicos de saúde - EHR)?', 'Camada de Consenso', 'Alta Segurança', 'Se Sim, o foco será em algoritmos de consenso com alta segurança, como PBFT.', 6, 7),
            ('A infraestrutura precisa lidar com grandes volumes de dados ou dispositivos IoT?', 'Camada de Infraestrutura', 'Escalabilidade Alta', 'Se Sim, prioriza DLTs com alto suporte à escalabilidade, como IOTA.', 8, 9),
            ('A eficiência energética é um fator crucial para a rede?', 'Camada de Infraestrutura', 'Eficiência Energética', 'Se Sim, sugere DLTs energeticamente eficientes, como IOTA ou PoS.', 10, 11),
            ('Alta escalabilidade é mais importante que alta segurança?', 'Camada de Consenso', 'Escalabilidade', 'Se Sim, recomenda DLTs com alta escalabilidade, como Polkadot ou DPoS.', 12, 13),
            ('A rede precisa de baixa latência para suportar monitoramento de saúde em tempo real?', 'Camada de Infraestrutura', 'Baixa Latência', 'Se Sim, sugere DLTs com baixa latência, como Hyperledger Fabric.', 14, 15),
            ('A camada de internet deve suportar redes distribuídas globalmente?', 'Camada de Internet', 'Conectividade Global', 'Se Sim, prioriza redes distribuídas de grande escala.', 16, 17),
        ]

        try:
            with self.conn.cursor() as cur:
                # Verifica se já existem perguntas no banco de dados
                cur.execute("SELECT COUNT(*) FROM perguntasframework")
                result = cur.fetchone()[0]

                if result == 0:
                    # Insere as perguntas apenas se não houver perguntas cadastradas
                    for pergunta in perguntas:
                        cur.execute("""
                            INSERT INTO perguntasframework (descricao, camada_shermin, caracteristica_algoritmo, impacto, ramificacao_sim, ramificacao_nao)
                            VALUES (%s, %s, %s, %s, %s, %s);
                        """, pergunta)
                    self.conn.commit()
        except psycopg2.Error as e:
            st.error(f"Erro ao inserir perguntas no banco de dados: {e}")
            logging.error(f"Erro ao inserir perguntas no banco de dados: {e}")
            self.conn.rollback()

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
