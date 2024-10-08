import streamlit as st
import psycopg2
import hashlib
from database import Database
from sklearn import tree
import numpy as np

# Função para hash de senhas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Função para autenticar o usuário
def authenticate_user(db, username, password):
    hashed_password = hash_password(password)
    try:
        with db.conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s AND password_hash = %s", (username, hashed_password))
            user = cur.fetchone()
            return user is not None, user  # Retorna True se encontrar o usuário e o próprio usuário
    except psycopg2.Error as e:
        st.error(f"Erro ao verificar o login: {e}")
        return False, None

# Função para registrar novo usuário
def register_user(db, username, password):
    hashed_password = hash_password(password)
    return db.create_user(username, hashed_password)

# Função para a tela de login
def login_page(db):
    st.title("Login")
    login_username = st.text_input("Nome de Usuário")
    login_password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        authenticated, user = authenticate_user(db, login_username, login_password)
        if authenticated:
            st.session_state['logged_in'] = True
            st.session_state['username'] = login_username
            st.session_state['user_id'] = user[0]  # Armazena o id do usuário
            st.experimental_set_query_params(logged_in="True")  # Define query param para recarregar a página
            st.rerun()  # This will reload the app and show the questionnaire page
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

# Função para exibir perguntas e recomendar DLT para saúde com base em regras
def dlt_recomendation_rules(respostas_usuario):
    if not respostas_usuario:
        return None
    # Exemplo de regras simples para recomendação de DLT
    if len(respostas_usuario) < 4:
        return None  # Retorna None se não houver respostas suficientes
    if respostas_usuario[0] == 1 and respostas_usuario[1] == 1:
        return "Hyperledger"
    elif respostas_usuario[2] == 1 and respostas_usuario[3] == 1:
        return "IOTA"
    elif respostas_usuario[0] == 0 and respostas_usuario[3] == 1:
        return "Ethereum"
    else:
        return "Corda"

# Função para treinar o modelo de árvore de decisão
def treinar_modelo(db):
    # Exemplo de treinamento simples com frameworks e perguntas
    X = np.array([[1, 1, 1, 0], [0, 1, 0, 1], [1, 0, 1, 1], [0, 0, 0, 0]])
    y = np.array(['Hyperledger', 'Ethereum', 'IOTA', 'Corda'])

    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(X, y)
    return clf

# Função híbrida que utiliza regras e Machine Learning
def dlt_hybrid_recommendation(db, respostas_usuario):
    # Fase 1: Aplicação de Regras
    dlt_inicial = dlt_recomendation_rules(respostas_usuario)

    # Fase 2: Refinar com Machine Learning
    clf = treinar_modelo(db)
    dlt_final = clf.predict([respostas_usuario])[0]

    return dlt_inicial, dlt_final

# Função para calcular as métricas de Decision Tree e gravar no banco
def calcular_metricas(db, framework, respostas_usuario):
    # Exemplo de métricas simples usando Gini
    gini = 1 - sum((respostas_usuario.count(val) / len(respostas_usuario)) ** 2 for val in set(respostas_usuario))
    pontuacao = gini * len(respostas_usuario)  # Pontuação ponderada baseada na métrica Gini

    # Gravar no banco de dados
    with db.conn.cursor() as cur:
        cur.execute("INSERT INTO pontuacaoframeworks (id_framework, id_usuario, pontuacao) VALUES (%s, %s, %s)", 
                    (framework, st.session_state['user_id'], pontuacao))
        db.conn.commit()

# Função para exibir o questionário de perguntas e recomendar DLT
def dlt_questionnaire_page(db):
    st.title("Recomendação de DLT para Saúde")

    # Carregar perguntas do banco de dados
    with db.conn.cursor() as cur:
        cur.execute("SELECT id, descricao FROM perguntasframework")
        perguntas = cur.fetchall()

    respostas_usuario = []

    for pergunta in perguntas:
        id_pergunta, descricao = pergunta
        resposta = st.radio(descricao, ["Sim", "Não"], key=f"pergunta_{id_pergunta}")
        respostas_usuario.append(1 if resposta == "Sim" else 0)

    # Moved outside the loop
    if st.button("Obter Recomendação"):
        if not respostas_usuario:
            st.error("Por favor, responda pelo menos uma pergunta antes de enviar.")
        else:
            # Seleção do tipo de abordagem
            st.write("Selecione a abordagem para gerar a recomendação:")
            abordagem = st.selectbox("Escolha a abordagem", ["Baseada em Regras", "Híbrida (Regras + Machine Learning)"])

            if abordagem == "Baseada em Regras":
                # Abordagem baseada em regras
                dlt_recomendada = dlt_recomendation_rules(respostas_usuario)
                if dlt_recomendada:
                    st.write(f"**DLT Recomendada (Regras):** {dlt_recomendada}")
                else:
                    st.error("Respostas insuficientes para gerar recomendação.")
            elif abordagem == "Híbrida (Regras + Machine Learning)":
                # Abordagem híbrida
                dlt_inicial, dlt_final = dlt_hybrid_recommendation(db, respostas_usuario)
                st.write(f"**DLT Inicial Recomendada (Regras):** {dlt_inicial}")
                st.write(f"**DLT Final Refinada (Machine Learning):** {dlt_final}")

            # Gravar as respostas no banco de dados e calcular métricas
            calcular_metricas(db, dlt_recomendada if abordagem == "Baseada em Regras" else dlt_final, respostas_usuario)

            # Gravar as respostas do usuário
            with db.conn.cursor() as cur:
                for i, resposta in enumerate(respostas_usuario):
                    cur.execute("INSERT INTO respostasusuarios (id_pergunta, resposta, id_usuario) VALUES (%s, %s, %s)", 
                                (perguntas[i][0], resposta, st.session_state['user_id']))
                db.conn.commit()

# Função principal para controle da aplicação
def main():
    # Instanciar a classe Database
    db = Database()

    # Controle de login usando session state
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Se o usuário estiver logado, exibir as páginas da aplicação
    if st.session_state['logged_in']:
        st.sidebar.success(f"Bem-vindo, {st.session_state['username']}")

        # Adicionar botão de logout
        if st.sidebar.button("Sair"):
            st.session_state['logged_in'] = False
            st.experimental_set_query_params(logged_in="False")  # Definir query param para forçar o recarregamento
            st.rerun()  # Use st.rerun() instead of st.experimental_rerun()

        # Menu lateral
        menu = ["Recomendação de DLT", "Algoritmos de Consenso", "Casos de Uso de Frameworks", 
                "Frameworks DLT", "Dados de Treinamento", "Casos de Uso DLT", 
                "Comparações de Usuários", "Administração de Usuários"]

        choice = st.sidebar.selectbox("Menu", menu)

        # Mapeia as escolhas do menu para as funções correspondentes
        if choice == "Recomendação de DLT":
            dlt_questionnaire_page(db)  # Função para exibir o questionário e recomendação
        # Outras páginas podem ser adicionadas conforme a necessidade

    # Se o usuário não estiver logado, exibir a página de login
    else:
        login_page(db)

# Executa a função principal
if __name__ == '__main__':
    main()
