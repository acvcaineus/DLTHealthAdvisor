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

# Configuração de logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', filename='app_errors.log')

def desenhar_pilha_shermin(camada_atual):
    camadas = ["Camada de Aplicação", "Camada de Consenso", "Camada de Infraestrutura", "Camada de Internet"]
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
    explicacoes = {
        "Camada de Aplicação": "A camada de aplicação trata das interações diretas com o usuário e a aplicação final. Aqui, privacidade e integração são prioridades.",
        "Camada de Consenso": "A camada de consenso lida com como as decisões são feitas na rede descentralizada. Algoritmos como PBFT ou RAFT são usados aqui.",
        "Camada de Infraestrutura": "A camada de infraestrutura é responsável por como os dados são armazenados e processados. Escalabilidade e eficiência energética são prioridades.",
        "Camada de Internet": "A camada de internet é responsável pela conectividade global da rede. Redes distribuídas de larga escala são o foco aqui."
    }
    return explicacoes.get(camada_atual, "Camada não reconhecida.")

def dlt_questionnaire_page(db, recommender):
    st.title("Recomendação de DLT para Saúde")

    user_responses = get_user_responses()

    if st.button("Enviar"):
        recommendations = recommender.get_recommendations(user_responses)
        metrics = calculate_metrics(recommender, user_responses)
        
        st.subheader("Recomendações de DLT")
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")
        
        st.subheader("Métricas da Árvore de Decisão")
        st.write(f"Information Gain: {metrics['information_gain']:.4f}")
        st.write(f"Profundidade da Árvore: {metrics['tree_depth']}")
        st.write(f"Acurácia: {metrics['accuracy']:.2f}")

        st.subheader("Explicação da Recomendação Principal")
        explanation = generate_explanation(recommendations[0], db.get_training_data())
        st.write(explanation)

        st.subheader("Análise de Sensibilidade")
        sensitivity_results = recommender.sensitivity_analysis(user_responses)
        st.write("Sensibilidade das características:")
        for feature, sensitivity in sensitivity_results.items():
            st.write(f"{feature}: {sensitivity:.4f}")

        # Visualização da árvore de decisão
        st.subheader("Visualização da Árvore de Decisão")
        tree_fig = visualize_decision_tree(recommender.decision_tree)
        st.plotly_chart(tree_fig)

        # Visualização da comparação entre frameworks
        st.subheader("Comparação entre Frameworks")
        comparison_data = db.get_training_data()
        comparison_fig = visualize_comparison(comparison_data)
        st.plotly_chart(comparison_fig)

        if st.button("Exportar Resultados"):
            csv = export_to_csv(recommendations, db.get_training_data(), metrics)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="dlt_recommendation_results.csv",
                mime="text/csv",
            )

def main():
    db = Database()
    recommender = DecisionTreeRecommender()

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
