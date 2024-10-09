import streamlit as st
import psycopg2
import logging
import plotly.graph_objects as go
import time
from database import Database
from auth import create_user, authenticate_user
from decision_tree import DecisionTreeRecommender
from utils import get_user_responses, calculate_metrics, generate_explanation, export_to_csv
from visualization import visualize_decision_tree, visualize_comparison, create_radar_chart, create_heatmap, create_parallel_coordinates, create_grouped_bar_chart
from api import app as api_app
import threading

# Configuração de logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s', filename='app_errors.log')

def run_api():
    api_app.run(host='0.0.0.0', port=5001)

def dlt_questionnaire_page(db, recommender):
    st.title("DLT Framework Recommender for Healthcare")
    
    training_data = db.get_training_data()
    if training_data.empty:
        st.error("No training data available. Please contact the administrator.")
        return

    user_responses = get_user_responses()
    
    if st.button("Get Recommendations"):
        recommendations = recommender.get_recommendations(user_responses)
        metrics = calculate_metrics(recommender, user_responses)
        
        st.subheader("Recommended DLT Frameworks")
        for i, framework in enumerate(recommendations, 1):
            st.write(f"{i}. {framework}")
            st.write(generate_explanation(framework, training_data))
        
        st.subheader("Model Metrics")
        st.write(f"Information Gain: {metrics['information_gain']:.2f}")
        st.write(f"Tree Depth: {metrics['tree_depth']}")
        st.write(f"Accuracy: {metrics['accuracy']:.2f}")
        
        st.subheader("Decision Tree Visualization")
        st.plotly_chart(visualize_decision_tree(recommender.decision_tree))
        
        st.subheader("Framework Comparison")
        st.plotly_chart(visualize_comparison(training_data))
        
        st.subheader("Multi-dimensional Comparison (Radar Chart)")
        st.plotly_chart(create_radar_chart(training_data))
        
        st.subheader("Framework Heatmap Comparison")
        st.plotly_chart(create_heatmap(training_data))
        
        st.subheader("Parallel Coordinates Comparison")
        st.plotly_chart(create_parallel_coordinates(training_data))
        
        st.subheader("Grouped Bar Chart Comparison")
        st.plotly_chart(create_grouped_bar_chart(training_data))
        
        sensitivity_results = recommender.sensitivity_analysis(user_responses)
        st.subheader("Sensitivity Analysis")
        for feature, sensitivity in sensitivity_results.items():
            st.write(f"{feature}: {sensitivity:.2f}")
        
        if st.button("Export Results"):
            csv = export_to_csv(recommendations, training_data, metrics)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="dlt_recommendations.csv",
                mime="text/csv"
            )

def main():
    st.set_page_config(page_title="DLT Framework Recommender", layout="wide")
    
    db = Database()
    recommender = DecisionTreeRecommender()

    # Start API server in a separate thread
    api_thread = threading.Thread(target=run_api)
    api_thread.start()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.title("Welcome to DLT Framework Recommender")
        st.write("Please login or register to continue.")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                user = authenticate_user(username, password)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = user.id
                    st.session_state['username'] = user.username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        with col2:
            st.subheader("Register")
            new_username = st.text_input("New Username", key="register_username")
            new_password = st.text_input("New Password", type="password", key="register_password")
            if st.button("Register"):
                user_id = create_user(new_username, new_password)
                if user_id:
                    st.session_state['logged_in'] = True
                    st.session_state['user_id'] = user_id
                    st.session_state['username'] = new_username
                    st.success("Registration successful! You are now logged in.")
                    st.rerun()
                else:
                    st.error("Registration failed")
    else:
        st.sidebar.success(f"Welcome, {st.session_state['username']}")
        if st.sidebar.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

        dlt_questionnaire_page(db, recommender)

if __name__ == '__main__':
    main()
