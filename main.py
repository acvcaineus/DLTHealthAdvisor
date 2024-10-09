import streamlit as st
from database import Database
import hashlib

# Função para gerar o hash da senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Página de criação de usuário
def create_user_page(db):
    st.title("Registrar Usuário")

    new_username = st.text_input("Nome de Usuário")
    new_password = st.text_input("Senha", type="password")

    if st.button("Registrar"):
        if new_username and new_password:
            hashed_password = hash_password(new_password)  # Gera o hash da senha
            user_id = db.create_user(new_username, hashed_password)
            if user_id:
                st.success(f"Usuário '{new_username}' registrado com sucesso!")
            else:
                st.warning(f"O nome de usuário '{new_username}' já existe.")
        else:
            st.warning("Por favor, preencha todos os campos.")

# Página de login do usuário
def login_page(db):
    st.title("Login de Usuário")

    username = st.text_input("Nome de Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if username and password:
            hashed_password = hash_password(password)
            user_id = db.authenticate_user(username, hashed_password)
            if user_id:
                st.success(f"Login bem-sucedido! Bem-vindo, {username}.")
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['user_id'] = user_id
            else:
                st.error("Nome de usuário ou senha incorretos.")
        else:
            st.warning("Por favor, preencha todos os campos.")

# Função principal
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

        st.write("Você está logado!")
        # Aqui você pode adicionar mais funcionalidades para usuários logados

    else:
        menu = ["Login", "Registrar-se"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Login":
            login_page(db)
        elif choice == "Registrar-se":
            create_user_page(db)

if __name__ == '__main__':
    main()
