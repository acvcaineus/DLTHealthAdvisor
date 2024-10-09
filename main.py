import streamlit as st
import psycopg2
import logging
import plotly.graph_objects as go
import time
import os
from database import Database
from decision_tree import DecisionTreeRecommender
from auth import create_user, authenticate_user

# Configuração de logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', filename='app_errors.log')

def desenhar_pilha_shermin(camada_atual):
    camadas = ["Camada de Aplicação", "Camada de Consenso", "Camada de Infraestrutura", "Camada de Internet"]

    # Definir cores para destacar a camada atual
    cores = ['#D3D3D3' if camada != camada_atual else '#FFA500' for camada in camadas]

    fig = go.Figure(go.Bar(
        x=[1] * len(camadas),
        y=camadas,
        orientation='h',
        marker=dict(color=cores)
    ))

    fig.update_layout(
        title="Pilha Shermin - Camada Atual",
        xaxis_title="",
        yaxis_title="",
        showlegend=False,
        xaxis=dict(showticklabels=False),
        yaxis=dict(tickfont=dict(size=14))
    )

    return fig

def explicar_camada(camada_atual):
    explicacao = {
        "Camada de Aplicação": "A Camada de Aplicação está relacionada com a interface direta com o usuário final e como o sistema interage com outras aplicações. Aqui, priorizamos questões como privacidade e integração com sistemas legados.",
        "Camada de Consenso": "A Camada de Consenso lida com o processo de alcançar um acordo distribuído em redes descentralizadas. Algoritmos como PBFT e RAFT são priorizados nesta camada para garantir a segurança e escalabilidade.",
        "Camada de Infraestrutura": "A Camada de Infraestrutura trata dos aspectos de escalabilidade, eficiência energética e latência da rede. Nesta camada, priorizamos redes como IOTA e Hyperledger Fabric para lidar com grandes volumes de dados e alta demanda de eficiência.",
        "Camada de Internet": "A Camada de Internet lida com a conectividade global e como as redes distribuídas interagem através da Internet. A conectividade global e a distribuição de redes são fatores críticos aqui."
    }
    return explicacao.get(camada_atual, "Sem explicação disponível.")

def dlt_questionnaire_page(db):
    st.title("Recomendação de DLT para Saúde")

    with db.conn.cursor() as cur:
        # Recupera a primeira pergunta
        cur.execute("SELECT id, descricao, camada_shermin, caracteristica_algoritmo, ramificacao_sim, ramificacao_nao FROM perguntasframework WHERE id = 1")
        pergunta = cur.fetchone()

    respostas_usuario = {}
    proxima_pergunta_id = pergunta[0]

    while proxima_pergunta_id:
        with db.conn.cursor() as cur:
            cur.execute("SELECT id, descricao, camada_shermin, caracteristica_algoritmo, ramificacao_sim, ramificacao_nao FROM perguntasframework WHERE id = %s", (proxima_pergunta_id,))
            pergunta_atual = cur.fetchone()

        camada_atual = pergunta_atual[2]
        caracteristica_atual = pergunta_atual[3]

        # Desenhar a pilha Shermin com a camada atual destacada
        st.plotly_chart(desenhar_pilha_shermin(camada_atual))

        st.subheader(f"Camada Atual: {camada_atual}")
        st.write(f"**Característica Priorizada**: {caracteristica_atual}")
        st.write(f"**Explicação da Camada**: {explicar_camada(camada_atual)}")

        resposta = st.radio(pergunta_atual[1], ["Sim", "Não"], key=f"pergunta_{pergunta_atual[0]}")
        respostas_usuario[pergunta_atual[0]] = 1 if resposta == "Sim" else 0

        # Animação suave antes de pular para a próxima camada
        time.sleep(0.5)

        if resposta == "Sim":
            proxima_pergunta_id = pergunta_atual[4]  # Ramificação SIM
        else:
            proxima_pergunta_id = pergunta_atual[5]  # Ramificação NÃO

        if not proxima_pergunta_id:
            break

    if st.button("Enviar"):
        st.write("Respostas:", respostas_usuario)
        calcular_metricas(db, respostas_usuario)
    
    # Perform sensitivity analysis
    perform_sensitivity_analysis(respostas_usuario)

def calcular_metricas(db, respostas_usuario):
    pontuacao_total = sum(respostas_usuario.values())
    st.write(f"Pontuação calculada: {pontuacao_total}")

    with db.conn.cursor() as cur:
        cur.execute("INSERT INTO pontuacaoframeworks (id_usuario, pontuacao) VALUES (%s, %s)", 
                    (st.session_state['user_id'], pontuacao_total))
        db.conn.commit()

def perform_sensitivity_analysis(user_responses):
    st.subheader("Análise de Sensibilidade")
    recommender = DecisionTreeRecommender()
    sensitivity_results = recommender.sensitivity_analysis(user_responses)
    
    st.write("A análise de sensibilidade mostra como pequenas mudanças nas respostas podem afetar a recomendação final:")
    
    for feature, sensitivity in sensitivity_results.items():
        st.write(f"{feature}: {sensitivity:.2f}")
    
    st.write("Valores mais altos indicam que a característica tem um impacto maior na recomendação final.")

def main():
    db = Database()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("Login / Register")
        
        login_tab, register_tab = st.tabs(["Login", "Register"])
        
        with login_tab:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                user = authenticate_user(username, password)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = user.id
                    st.session_state['username'] = user.username
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password")
        
        with register_tab:
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            if st.button("Register"):
                user_id = create_user(new_username, new_password)
                if user_id:
                    st.success("Registration successful. Please log in.")
                else:
                    st.error("Registration failed. Username may already exist.")
    
    if st.session_state['logged_in']:
        st.sidebar.success(f"Welcome, {st.session_state['username']}")
        if st.sidebar.button("Logout"):
            st.session_state['logged_in'] = False
            st.experimental_rerun()
        
        dlt_questionnaire_page(db)

if __name__ == '__main__':
    main()
