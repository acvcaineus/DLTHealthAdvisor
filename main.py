import streamlit as st
from database import Database
import hashlib
from auth import authenticate_user
from decision_tree import DecisionTreeRecommender
from visualization import create_radar_chart, create_heatmap, create_parallel_coordinates, create_grouped_bar_chart
import pandas as pd

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
            user = authenticate_user(username, password)
            if user:
                st.success(f"Login bem-sucedido! Bem-vindo, {user.username}.")
                st.session_state['logged_in'] = True
                st.session_state['username'] = user.username
                st.session_state['user_id'] = user.id
            else:
                st.error("Nome de usuário ou senha incorretos.")
        else:
            st.warning("Por favor, preencha todos os campos.")

# Função para exibir as visualizações
def display_visualizations(comparison_data):
    st.subheader("Visualizações Avançadas")
    
    # Radar Chart
    st.plotly_chart(create_radar_chart(comparison_data))
    
    # Heatmap
    st.plotly_chart(create_heatmap(comparison_data))
    
    # Parallel Coordinates
    st.plotly_chart(create_parallel_coordinates(comparison_data))
    
    # Grouped Bar Chart
    st.plotly_chart(create_grouped_bar_chart(comparison_data))

# Função principal
def main():
    db = Database()
    recommender = DecisionTreeRecommender()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        st.sidebar.success(f"Bem-vindo, {st.session_state['username']}")

        if st.sidebar.button("Sair"):
            st.session_state['logged_in'] = False
            st.experimental_set_query_params(logged_in="False")
            st.rerun()

        st.title("DLT Framework Recommender")

        # Aqui você pode adicionar a lógica para coletar as respostas do usuário
        # e gerar recomendações usando o DecisionTreeRecommender

        # Para fins de demonstração, vamos criar alguns dados de comparação fictícios
        comparison_data = pd.DataFrame({
            'name': ['Ancile', 'BlockHR', 'RBEF', 'ChainSure', 'PCH'],
            'Security': [9.5, 8.0, 7.5, 8.5, 7.5],
            'Scalability': [7.0, 6.5, 8.5, 9.0, 7.5],
            'Energy_Efficiency': [6.5, 7.5, 8.5, 8.5, 6.0],
            'Governance': [9.0, 7.0, 7.5, 8.5, 7.0],
            'Interoperability': [8.5, 7.5, 8.0, 7.5, 6.5],
            'Operational_Complexity': [7.0, 6.5, 7.0, 7.5, 6.0],
            'Implementation_Cost': [7.5, 6.5, 7.5, 7.0, 6.0],
            'Latency': [6.5, 7.0, 7.5, 8.0, 5.5]
        })

        display_visualizations(comparison_data)

    else:
        menu = ["Login", "Registrar-se"]
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "Login":
            login_page(db)
        elif choice == "Registrar-se":
            create_user_page(db)

if __name__ == '__main__':
    main()
