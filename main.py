import streamlit as st
import psycopg2
import logging
import plotly.graph_objects as go
import time
from database import Database
from auth import create_user, authenticate_user
from decision_tree import DecisionTreeRecommender
from utils import get_user_responses, calculate_metrics, generate_explanation, export_to_csv
from visualization import visualize_decision_tree, visualize_comparison
from api import app as api_app
import threading

# Configuração de logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', filename='app_errors.log')

# ... [rest of the code remains unchanged] ...

def run_api():
    api_app.run(host='0.0.0.0', port=5001)

def main():
    db = Database()
    recommender = DecisionTreeRecommender()

    # Start API server in a separate thread
    api_thread = threading.Thread(target=run_api)
    api_thread.start()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.sidebar.title("Login / Registro")
        action = st.sidebar.radio("Escolha uma ação", ["Login", "Registro"])

        if action == "Login":
            username = st.sidebar.text_input("Nome de usuário")
            password = st.sidebar.text_input("Senha", type="password")
            if st.sidebar.button("Login"):
                user = authenticate_user(username, password)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = user.id
                    st.session_state['username'] = user.username
                    st.experimental_rerun()
                else:
                    st.sidebar.error("Credenciais inválidas")
        else:
            new_username = st.sidebar.text_input("Novo nome de usuário")
            new_password = st.sidebar.text_input("Nova senha", type="password")
            if st.sidebar.button("Registrar"):
                user_id = create_user(new_username, new_password)
                if user_id:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = user_id
                    st.session_state['username'] = new_username
                    st.experimental_rerun()
                else:
                    st.sidebar.error("Falha no registro")
    else:
        st.sidebar.success(f"Bem-vindo, {st.session_state['username']}")
        if st.sidebar.button("Sair"):
            st.session_state['logged_in'] = False
            st.experimental_rerun()

        dlt_questionnaire_page(db, recommender)

if __name__ == '__main__':
    main()
