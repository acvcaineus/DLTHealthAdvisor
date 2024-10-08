import streamlit as st
import psycopg2
import hashlib
from database import Database
from utils import get_user_responses

# Função para hash de senhas
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Função para autenticar o usuário
def authenticate_user(db, username, password):
    hashed_password = hash_password(password)
    try:
        with db.conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s AND password_hash = %s", (username, hashed_password))
            return cur.fetchone() is not None  # Retorna True se encontrar o usuário
    except psycopg2.Error as e:
        st.error(f"Erro ao verificar o login: {e}")
        return False

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
        if authenticate_user(db, login_username, login_password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = login_username
            st.success("Login bem-sucedido!")
            st.experimental_rerun()  # This will reload the app and show the questionnaire page
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

# Função para a página inicial
def home_page():
    st.title("Home")
    st.write(f"Bem-vindo, {st.session_state['username']}!")

# Função para exibir e gerenciar os Algoritmos de Consenso
def consensus_algorithms_page(db):
    st.title("Algoritmos de Consenso")
    st.write("Aqui estão os algoritmos de consenso disponíveis.")
    try:
        cur = db.conn.cursor()
        cur.execute("SELECT * FROM dlt_consensus_algorithms")
        data = cur.fetchall()
        if data:
            for row in data:
                st.write(row)
        else:
            st.write("Nenhum algoritmo de consenso disponível.")
    except Exception as e:
        st.error(f"Erro ao carregar algoritmos de consenso: {e}")

# Função para exibir e gerenciar os Casos de Uso de Frameworks
def framework_use_cases_page(db):
    st.title("Casos de Uso de Frameworks")
    st.write("Aqui estão os casos de uso dos frameworks.")
    try:
        cur = db.conn.cursor()
        cur.execute("SELECT * FROM dlt_framework_use_cases")
        data = cur.fetchall()
        if data:
            for row in data:
                st.write(row)
        else:
            st.write("Nenhum caso de uso de frameworks disponível.")
    except Exception as e:
        st.error(f"Erro ao carregar casos de uso de frameworks: {e}")

# Função para exibir e gerenciar os Frameworks DLT
def frameworks_page(db):
    st.title("Frameworks DLT")
    st.write("Aqui estão os frameworks DLT disponíveis.")
    try:
        cur = db.conn.cursor()
        cur.execute("SELECT * FROM dlt_frameworks")
        data = cur.fetchall()
        if data:
            for row in data:
                st.write(row)
        else:
            st.write("Nenhum framework DLT disponível.")
    except Exception as e:
        st.error(f"Erro ao carregar frameworks DLT: {e}")

# Função para exibir e gerenciar os Dados de Treinamento
def training_data_page(db):
    st.title("Dados de Treinamento")
    st.write("Aqui estão os dados de treinamento disponíveis.")
    try:
        cur = db.conn.cursor()
        cur.execute("SELECT * FROM dlt_training_data")
        data = cur.fetchall()
        if data:
            for row in data:
                st.write(row)
        else:
            st.write("Nenhum dado de treinamento disponível.")
    except Exception as e:
        st.error(f"Erro ao carregar dados de treinamento: {e}")

# Função para exibir e gerenciar os Casos de Uso DLT
def use_cases_page(db):
    st.title("Casos de Uso DLT")
    st.write("Aqui estão os casos de uso das DLTs.")
    try:
        cur = db.conn.cursor()
        cur.execute("SELECT * FROM dlt_use_cases")
        data = cur.fetchall()
        if data:
            for row in data:
                st.write(row)
        else:
            st.write("Nenhum caso de uso disponível.")
    except Exception as e:
        st.error(f"Erro ao carregar casos de uso de DLTs: {e}")

# Função para exibir e gerenciar as Comparações de Usuários
def user_comparisons_page(db):
    st.title("Comparações de Usuários")
    st.write("Aqui estão as comparações feitas pelos usuários.")
    try:
        cur = db.conn.cursor()
        cur.execute("SELECT * FROM user_comparisons")
        data = cur.fetchall()
        if data:
            for row in data:
                st.write(row)
        else:
            st.write("Nenhuma comparação disponível.")
    except Exception as e:
        st.error(f"Erro ao carregar comparações de usuários: {e}")

# Função para a administração de usuários
def admin_users_page(db):
    st.title("Administração de Usuários")
    st.write("Aqui estão os usuários registrados.")
    try:
        cur = db.conn.cursor()
        cur.execute("SELECT id, username FROM users")
        data = cur.fetchall()
        if data:
            for row in data:
                st.write(row)
        else:
            st.write("Nenhum usuário registrado.")
    except Exception as e:
        st.error(f"Erro ao carregar usuários: {e}")

# New function for questionnaire page
def questionnaire_page():
    st.title('Questionário')
    user_responses = get_user_responses()
    
    if st.button("Salvar Respostas"):
        # Here you would typically save the responses to the database
        st.success("Respostas salvas com sucesso!")

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
            st.experimental_rerun()

        # Menu lateral
        menu = ["Questionário", "Home", "Algoritmos de Consenso", "Casos de Uso de Frameworks", 
                "Frameworks DLT", "Dados de Treinamento", "Casos de Uso DLT", 
                "Comparações de Usuários", "Administração de Usuários"]

        choice = st.sidebar.selectbox("Menu", menu)

        # Mapeia as escolhas do menu para as funções correspondentes
        if choice == "Questionário":
            questionnaire_page()
        elif choice == "Home":
            home_page()
        elif choice == "Algoritmos de Consenso":
            consensus_algorithms_page(db)
        elif choice == "Casos de Uso de Frameworks":
            framework_use_cases_page(db)
        elif choice == "Frameworks DLT":
            frameworks_page(db)
        elif choice == "Dados de Treinamento":
            training_data_page(db)
        elif choice == "Casos de Uso DLT":
            use_cases_page(db)
        elif choice == "Comparações de Usuários":
            user_comparisons_page(db)
        elif choice == "Administração de Usuários":
            admin_users_page(db)

    # Se o usuário não estiver logado, exibir a página de login
    else:
        login_page(db)

# Executa a função principal
if __name__ == '__main__':
    main()
