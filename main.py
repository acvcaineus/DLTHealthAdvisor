import streamlit as st
import psycopg2
import hashlib
from database import Database
from sklearn import tree
import numpy as np
import pandas as pd

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(db, username, password):
    hashed_password = hash_password(password)
    try:
        with db.conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s AND password_hash = %s", (username, hashed_password))
            user = cur.fetchone()
            return user is not None, user
    except psycopg2.Error as e:
        st.error(f"Erro ao verificar o login: {e}")
        return False, None

def register_user(db, username, password):
    hashed_password = hash_password(password)
    return db.create_user(username, hashed_password)

def login_page(db):
    st.title("Login")
    login_username = st.text_input("Nome de Usuário")
    login_password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        authenticated, user = authenticate_user(db, login_username, login_password)
        if authenticated:
            st.session_state['logged_in'] = True
            st.session_state['username'] = login_username
            st.session_state['user_id'] = user[0]
            st.experimental_set_query_params(logged_in="True")
            st.rerun()
        else:
            st.error("Nome de usuário ou senha incorretos.")

    st.write("---")
    st.write("Ou registre um novo usuário abaixo:")

    register_username = st.text_input("Novo Nome de Usuário")
    register_password = st.text_input("Nova Senha", type="password")
    if st.button("Registrar Novo Usuário"):
        if register_username and register_password:
            if register_user(db, register_username, register_password):
                st.success(f"Usuário {register_username} registrado com sucesso! Por favor, faça login.")
            else:
                st.error(f"Falha ao registrar o usuário {register_username}.")
        else:
            st.warning("Por favor, preencha todos os campos.")

def dlt_recomendation_rules(respostas_usuario):
    if not respostas_usuario:
        return None
    if len(respostas_usuario) < 4:
        return None
    if respostas_usuario[0] == 1 and respostas_usuario[1] == 1:
        return "Hyperledger"
    elif respostas_usuario[2] == 1 and respostas_usuario[3] == 1:
        return "IOTA"
    elif respostas_usuario[0] == 0 and respostas_usuario[3] == 1:
        return "Ethereum"
    else:
        return "Corda"

def treinar_modelo(db):
    X = np.array([[1, 1, 1, 0], [0, 1, 0, 1], [1, 0, 1, 1], [0, 0, 0, 0]])
    y = np.array(['Hyperledger', 'Ethereum', 'IOTA', 'Corda'])

    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(X, y)
    return clf

def dlt_hybrid_recommendation(db, respostas_usuario):
    dlt_inicial = dlt_recomendation_rules(respostas_usuario)
    clf = treinar_modelo(db)
    dlt_final = clf.predict([respostas_usuario])[0]
    return dlt_inicial, dlt_final

def calcular_metricas(db, framework, respostas_usuario):
    gini = 1 - sum((respostas_usuario.count(val) / len(respostas_usuario)) ** 2 for val in set(respostas_usuario))
    pontuacao = gini * len(respostas_usuario)

    with db.conn.cursor() as cur:
        cur.execute("INSERT INTO pontuacaoframeworks (id_framework, id_usuario, pontuacao) VALUES (%s, %s, %s)", 
                    (framework, st.session_state['user_id'], pontuacao))
        db.conn.commit()

def dlt_questionnaire_page(db):
    st.title("Recomendação de DLT para Saúde")

    with db.conn.cursor() as cur:
        cur.execute("SELECT id, descricao FROM perguntasframework")
        perguntas = cur.fetchall()

    respostas_usuario = []

    for pergunta in perguntas:
        id_pergunta, descricao = pergunta
        resposta = st.radio(descricao, ["Sim", "Não"], key=f"pergunta_{id_pergunta}")
        respostas_usuario.append(1 if resposta == "Sim" else 0)

    if st.button("Obter Recomendação"):
        if not respostas_usuario:
            st.error("Por favor, responda pelo menos uma pergunta antes de enviar.")
        else:
            st.write("Selecione a abordagem para gerar a recomendação:")
            abordagem = st.selectbox("Escolha a abordagem", ["Baseada em Regras", "Híbrida (Regras + Machine Learning)"])

            if abordagem == "Baseada em Regras":
                dlt_recomendada = dlt_recomendation_rules(respostas_usuario)
                if dlt_recomendada:
                    st.write(f"**DLT Recomendada (Regras):** {dlt_recomendada}")
                else:
                    st.error("Respostas insuficientes para gerar recomendação.")
            elif abordagem == "Híbrida (Regras + Machine Learning)":
                dlt_inicial, dlt_final = dlt_hybrid_recommendation(db, respostas_usuario)
                st.write(f"**DLT Inicial Recomendada (Regras):** {dlt_inicial}")
                st.write(f"**DLT Final Refinada (Machine Learning):** {dlt_final}")

            calcular_metricas(db, dlt_recomendada if abordagem == "Baseada em Regras" else dlt_final, respostas_usuario)

            with db.conn.cursor() as cur:
                for i, resposta in enumerate(respostas_usuario):
                    cur.execute("INSERT INTO respostasusuarios (id_pergunta, resposta, id_usuario) VALUES (%s, %s, %s)", 
                                (perguntas[i][0], resposta, st.session_state['user_id']))
                db.conn.commit()

def add_consensus_algorithms_page(db):
    st.title("Algoritmos de Consenso")
    with db.conn.cursor() as cur:
        cur.execute("SELECT * FROM dlt_consensus_algorithms")
        algorithms = cur.fetchall()
    
    for algo in algorithms:
        st.subheader(algo[1])
        st.write(f"Grupo de Consenso: {algo[2]}")
        st.write(f"Descrição: {algo[3]}")
        st.write(f"Característica Prioritária: {algo[4]}")
        st.write(f"Casos de Uso: {', '.join(algo[5])}")
        st.write(f"Principais Características: {algo[6]}")
        st.write("---")

def add_framework_use_cases_page(db):
    st.title("Casos de Uso de Frameworks")
    with db.conn.cursor() as cur:
        cur.execute("""
            SELECT f.name, u.use_case, fu.relevant_criteria 
            FROM dlt_framework_use_cases fu
            JOIN dlt_frameworks f ON fu.framework_id = f.id
            JOIN dlt_use_cases u ON fu.use_case_id = u.id
        """)
        use_cases = cur.fetchall()
    
    for case in use_cases:
        st.subheader(f"{case[0]} - {case[1]}")
        st.write(f"Critérios Relevantes: {case[2]}")
        st.write("---")

def add_dlt_frameworks_page(db):
    st.title("Frameworks DLT")
    with db.conn.cursor() as cur:
        cur.execute("SELECT * FROM dlt_frameworks")
        frameworks = cur.fetchall()
    
    for fw in frameworks:
        st.subheader(fw[1])
        st.write(f"Segurança: {fw[2]}")
        st.write(f"Escalabilidade: {fw[3]}")
        st.write(f"Eficiência Energética: {fw[4]}")
        st.write(f"Governança: {fw[5]}")
        st.write(f"Interoperabilidade: {fw[6]}")
        st.write(f"Complexidade Operacional: {fw[7]}")
        st.write(f"Custo de Implementação: {fw[8]}")
        st.write(f"Latência: {fw[9]}")
        st.write(f"Algoritmos de Exemplo: {fw[18]}")
        st.write("---")

def add_training_data_page(db):
    st.title("Dados de Treinamento")
    with db.conn.cursor() as cur:
        cur.execute("SELECT * FROM dlt_training_data")
        data = cur.fetchall()
    
    df = pd.DataFrame(data, columns=['id', 'framework', 'Security', 'Scalability', 'Energy_efficiency', 'Governance', 'Operational_Complexity', 'Latency', 'Integration', 'Interoperability', 'Implementation_Cost', 'Privacy', 'Data_Volume'])
    st.dataframe(df)

def add_dlt_use_cases_page(db):
    st.title("Casos de Uso DLT")
    with db.conn.cursor() as cur:
        cur.execute("SELECT * FROM dlt_use_cases")
        use_cases = cur.fetchall()
    
    for case in use_cases:
        st.subheader(case[1])
        st.write(f"Descrição: {case[2]}")
        st.write(f"Benefícios: {case[3]}")
        st.write(f"Desafios: {case[4]}")
        st.write("---")

def add_user_comparisons_page(db):
    st.title("Comparações de Usuários")
    with db.conn.cursor() as cur:
        cur.execute("""
            SELECT u.username, f1.name as framework1, f2.name as framework2, c.metrica1, c.metrica2, c.descricao_comparacao
            FROM comparacaoframeworks c
            JOIN users u ON c.id_usuario = u.id
            JOIN dlt_frameworks f1 ON c.id_framework_1 = f1.id
            JOIN dlt_frameworks f2 ON c.id_framework_2 = f2.id
        """)
        comparisons = cur.fetchall()
    
    for comp in comparisons:
        st.subheader(f"Comparação por {comp[0]}")
        st.write(f"Framework 1: {comp[1]}")
        st.write(f"Framework 2: {comp[2]}")
        st.write(f"Métrica 1: {comp[3]}")
        st.write(f"Métrica 2: {comp[4]}")
        st.write(f"Descrição da Comparação: {comp[5]}")
        st.write("---")

def add_user_admin_page(db):
    st.title("Administração de Usuários")
    if st.session_state.get('is_admin', False):
        with db.conn.cursor() as cur:
            cur.execute("SELECT id, username FROM users")
            users = cur.fetchall()
        
        for user in users:
            st.write(f"ID: {user[0]}, Username: {user[1]}")
            if st.button(f"Delete {user[1]}"):
                pass
    else:
        st.write("Você não tem permissão para acessar esta página.")

def main():
    db = Database()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        st.sidebar.success(f"Bem-vindo, {st.session_state['username']}")

        if st.sidebar.button("Sair"):
            st.session_state['logged_in'] = False
            st.experimental_set_query_params(logged_in="False")
            st.rerun()

        menu = ["Recomendação de DLT", "Algoritmos de Consenso", "Casos de Uso de Frameworks", 
                "Frameworks DLT", "Dados de Treinamento", "Casos de Uso DLT", 
                "Comparações de Usuários", "Administração de Usuários"]

        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Recomendação de DLT":
            dlt_questionnaire_page(db)
        elif choice == "Algoritmos de Consenso":
            add_consensus_algorithms_page(db)
        elif choice == "Casos de Uso de Frameworks":
            add_framework_use_cases_page(db)
        elif choice == "Frameworks DLT":
            add_dlt_frameworks_page(db)
        elif choice == "Dados de Treinamento":
            add_training_data_page(db)
        elif choice == "Casos de Uso DLT":
            add_dlt_use_cases_page(db)
        elif choice == "Comparações de Usuários":
            add_user_comparisons_page(db)
        elif choice == "Administração de Usuários":
            add_user_admin_page(db)

    else:
        login_page(db)

if __name__ == '__main__':
    main()