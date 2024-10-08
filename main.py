import streamlit as st
from database import Database

# Funções para cada página
def home_page():
    st.title("Home")
    st.write("Bem-vindo ao Framework de Seleção de DLT")
    st.write("Aqui você pode obter recomendações de DLTs e comparar diferentes frameworks.")
    st.subheader("Objetivo do Framework")
    st.write("Explicação detalhada sobre o objetivo do framework, baseado na pilha de Shermin com quatro camadas.")
    st.subheader("Base Teórica")
    st.write("Aqui você pode inserir uma explicação sobre a pilha de Shermin e as camadas: aplicação, consenso, infraestrutura e internet.")

def admin_panel_page(db):
    st.title("Admin de Painel")
    st.write("Gerencie os dados das tabelas do banco de dados.")

    st.subheader("Gerenciamento de Algoritmos de Consenso")
    # Adicionar formulário para inclusão/alteração/exclusão de dados de algoritmos de consenso

    st.subheader("Gerenciamento de Frameworks")
    # Adicionar formulário para inclusão/alteração/exclusão de dados de frameworks

    st.subheader("Gerenciamento de Casos de Uso")
    # Adicionar formulário para inclusão/alteração/exclusão de casos de uso

def dlt_recommendation_page(db):
    st.title("Recomendação de DLT")
    st.write("Responda às perguntas abaixo para obter a recomendação de DLT.")

    st.subheader("Camada de Aplicação")
    # Perguntas da camada de aplicação

    st.subheader("Camada de Consenso")
    # Perguntas da camada de consenso

    st.subheader("Camada de Infraestrutura")
    # Perguntas da camada de infraestrutura

    st.subheader("Camada de Internet")
    # Perguntas da camada de internet

    # Exibir recomendação com base nas respostas
    if st.button("Obter Recomendação"):
        st.write("Apresentar a recomendação de DLT com base nas respostas.")

def decision_tree_metrics_page():
    st.title("Métricas da Decision Tree")
    st.write("Fórmulas e resultados da árvore de decisão.")

    st.subheader("Fórmulas Utilizadas")
    # Explicar fórmulas e cálculos

    st.subheader("Resultados Otimizados")
    # Mostrar os resultados da árvore de decisão com base nas respostas

def validation_page():
    st.title("Validação dos Resultados")
    st.write("Justificativas técnicas para as pontuações e ponderações.")

    st.subheader("Justificativas Técnicas")
    # Explicações detalhadas

    st.subheader("Comparação com outros Frameworks")
    # Mostrar a comparação de resultados com outros frameworks

def comparison_page():
    st.title("Comparação entre Frameworks")
    st.write("Compare o framework proposto com outros frameworks no banco de dados.")

    # Exibir comparação entre os frameworks
    st.subheader("Métricas de Comparação")
    # Mostrar métricas de comparação

# Função principal
def main():
    # Instanciar o banco de dados
    db = Database()

    # Menu lateral
    menu = ["Home", "Admin de Painel", "Recomendação de DLT", "Métricas da Decision Tree", "Validação dos Resultados", "Comparação entre Frameworks"]
    choice = st.sidebar.selectbox("Menu", menu)

    # Mapeia as escolhas do menu para as funções correspondentes
    if choice == "Home":
        home_page()
    elif choice == "Admin de Painel":
        admin_panel_page(db)
    elif choice == "Recomendação de DLT":
        dlt_recommendation_page(db)
    elif choice == "Métricas da Decision Tree":
        decision_tree_metrics_page()
    elif choice == "Validação dos Resultados":
        validation_page()
    elif choice == "Comparação entre Frameworks":
        comparison_page()

# Executa a função principal
if __name__ == '__main__':
    main()
