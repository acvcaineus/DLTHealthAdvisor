import streamlit as st
import psycopg2
import hashlib
import pandas as pd
import numpy as np
from sklearn import tree
from database import Database
from decision_tree import DecisionTreeRecommender
import logging
import os
import plotly.graph_objs as go

# Configure logging
log_file = 'app.log'
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file),
                        logging.StreamHandler()
                    ])

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
        logging.error(f"Error verifying login: {e}")
        st.error(f"Error verifying login: {e}")
        return False, None

def register_user(db, username, password):
    hashed_password = hash_password(password)
    return db.create_user(username, hashed_password)

def login_page(db):
    st.title("Login")
    login_username = st.text_input("Username")
    login_password = st.text_input("Password", type="password")

    if st.button("Login"):
        authenticated, user = authenticate_user(db, login_username, login_password)
        if authenticated:
            st.session_state['logged_in'] = True
            st.session_state['username'] = login_username
            st.session_state['user_id'] = user[0]
            st.experimental_set_query_params(logged_in="True")
            logging.info(f"User {login_username} logged in successfully")
            st.rerun()
        else:
            st.error("Incorrect username or password.")

    st.write("---")
    st.write("Or register a new user below:")

    register_username = st.text_input("New Username")
    register_password = st.text_input("New Password", type="password")
    if st.button("Register New User"):
        if register_username and register_password:
            if register_user(db, register_username, register_password):
                logging.info(f"User {register_username} registered successfully")
                st.success(f"User {register_username} registered successfully! Please login.")
            else:
                logging.error(f"Failed to register user {register_username}")
                st.error(f"Failed to register user {register_username}.")
        else:
            st.warning("Please fill in all fields.")

def plot_sensitivity_analysis(sensitivity_results):
    features = list(sensitivity_results.keys())
    sensitivities = list(sensitivity_results.values())
    
    fig = go.Figure(data=[go.Bar(x=features, y=sensitivities)])
    fig.update_layout(
        title="Sensitivity Analysis",
        xaxis_title="Features",
        yaxis_title="Sensitivity",
        yaxis_range=[0, 1]
    )
    return fig

def dlt_questionnaire_page(db):
    st.title("DLT Recommendation for Healthcare")

    logging.info("Fetching questions from the database")
    with db.conn.cursor() as cur:
        cur.execute("SELECT id, descricao FROM perguntasframework")
        perguntas = cur.fetchall()

    respostas_usuario = {}

    for pergunta in perguntas:
        id_pergunta, descricao = pergunta
        resposta = st.radio(descricao, ["Yes", "No"], key=f"pergunta_{id_pergunta}")
        respostas_usuario[id_pergunta] = 1 if resposta == "Yes" else 0

    if st.button("Get Recommendation"):
        if not respostas_usuario:
            st.error("Please answer at least one question before submitting.")
        else:
            logging.info("Generating DLT recommendation")
            st.write("Select the approach to generate the recommendation:")
            abordagem = st.selectbox("Choose the approach", ["Rule-based", "Hybrid (Rules + Machine Learning)"])

            if abordagem == "Rule-based":
                dlt_recomendada = dlt_recomendation_rules(list(respostas_usuario.values()))
                if dlt_recomendada:
                    st.write(f"**Recommended DLT (Rules):** {dlt_recomendada}")
                else:
                    st.error("Insufficient responses to generate recommendation.")
            elif abordagem == "Hybrid (Rules + Machine Learning)":
                recommender = DecisionTreeRecommender()
                dlt_recomendada = recommender.get_recommendations(respostas_usuario)[0]
                st.write(f"**Recommended DLT (Hybrid):** {dlt_recomendada}")

                st.subheader("Feature Importance")
                feature_importances = recommender.get_feature_importances()
                for feature, importance in feature_importances.items():
                    st.write(f"{feature}: {importance:.4f}")

                st.subheader("Sensitivity Analysis")
                sensitivity_results = recommender.sensitivity_analysis(respostas_usuario)
                st.plotly_chart(plot_sensitivity_analysis(sensitivity_results))
                st.write("The sensitivity analysis shows the probability of change in recommendation when varying each feature.")

            logging.info(f"Calculating metrics for recommended DLT: {dlt_recomendada}")
            calcular_metricas(db, dlt_recomendada, list(respostas_usuario.values()))

            logging.info("Saving user responses to the database")
            with db.conn.cursor() as cur:
                for id_pergunta, resposta in respostas_usuario.items():
                    cur.execute("INSERT INTO respostasusuarios (id_pergunta, resposta, id_usuario) VALUES (%s, %s, %s)", 
                                (id_pergunta, resposta, st.session_state['user_id']))
                db.conn.commit()

def add_dlt_frameworks_page(db):
    st.title("DLT Frameworks")
    logging.info("Fetching DLT frameworks from the database")
    with db.conn.cursor() as cur:
        cur.execute("""
            SELECT 
                name, tipo_dlt, grupo_algoritmo, algoritmo_consenso, principais_caracteristicas, 
                security, scalability, energy_efficiency, governance, latency 
            FROM dlt_frameworks
        """)
        frameworks = cur.fetchall()

    df = pd.DataFrame(frameworks, columns=[
        'Name', 'DLT Type', 'Algorithm Group', 'Consensus Algorithm', 'Main Characteristics',
        'Security', 'Scalability', 'Energy Efficiency', 'Governance', 'Latency'
    ])

    st.dataframe(df)

def main():
    logging.info("Starting the application")
    db = Database()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        st.sidebar.success(f"Welcome, {st.session_state['username']}")

        if st.sidebar.button("Logout"):
            logging.info(f"User {st.session_state['username']} logged out")
            st.session_state['logged_in'] = False
            st.experimental_set_query_params(logged_in="False")
            st.rerun()

        menu = ["DLT Recommendation", "DLT Frameworks"]

        choice = st.sidebar.selectbox("Menu", menu)

        if choice == "DLT Recommendation":
            dlt_questionnaire_page(db)
        elif choice == "DLT Frameworks":
            add_dlt_frameworks_page(db)
    else:
        login_page(db)

if __name__ == '__main__':
    main()
