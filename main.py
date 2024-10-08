import streamlit as st
import pandas as pd
from decision_tree import DecisionTreeRecommender
from database import Database
from visualization import visualize_decision_tree, visualize_comparison
from utils import get_user_responses, calculate_metrics, generate_explanation, export_to_csv
from auth import create_user, authenticate_user, User
import json

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None

# Initialize database connection and test it
db = Database()
if not db.test_connection():
    st.error("Failed to connect to the database. Please check your database configuration.")
    st.stop()

# Initialize the decision tree recommender
recommender = DecisionTreeRecommender()

st.set_page_config(page_title="DLT Framework Recommender for Healthcare", layout="wide")

st.title("DLT Framework Recommender for Healthcare")

# User authentication
if st.session_state.user is None:
    st.subheader("Login")
    login_username = st.text_input("Username")
    login_password = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)
    if col1.button("Login"):
        user = authenticate_user(login_username, login_password)
        if user:
            st.session_state.user = user
            st.success(f"Welcome, {user.username}!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")
    if col2.button("Register"):
        if login_username and login_password:
            user_id = create_user(login_username, login_password)
            if user_id:
                st.success("User registered successfully. Please log in.")
            else:
                st.error("Failed to register user. Username may already exist.")
        else:
            st.warning("Please enter both username and password to register.")
else:
    st.write(f"Welcome, {st.session_state.user.username}!")
    if st.button("Logout"):
        st.session_state.user = None
        st.experimental_rerun()

    st.write("Welcome to the DLT Framework Recommender for Healthcare. This tool will help you choose the most suitable DLT framework based on your specific needs.")

    # Collect user responses
    user_responses = get_user_responses()

    # Generate recommendations
    recommendations = recommender.get_recommendations(user_responses)

    # Display recommendations
    st.subheader("Recommended DLT Frameworks")
    for i, framework in enumerate(recommendations, 1):
        st.write(f"{i}. {framework}")

    # Calculate and display metrics
    metrics = calculate_metrics(recommender, user_responses)
    st.subheader("Decision Tree Metrics")
    st.write(f"Information Gain: {metrics['information_gain']:.2f}")
    st.write(f"Tree Depth: {metrics['tree_depth']}")
    st.write(f"Accuracy: {metrics['accuracy']:.2f}")

    # Visualize decision tree
    st.subheader("Decision Tree Visualization")
    fig_tree = visualize_decision_tree(recommender.decision_tree)
    st.plotly_chart(fig_tree)

    # Compare recommended frameworks
    st.subheader("Framework Comparison")
    comparison_data = db.get_framework_data(recommendations)
    fig_comparison = visualize_comparison(comparison_data)
    st.plotly_chart(fig_comparison)

    # Generate and display explanations
    st.subheader("Recommendations Explained")
    for framework in recommendations:
        explanation = generate_explanation(framework, comparison_data)
        st.write(f"**{framework}**")
        st.write(explanation)

    # Save comparison
    if st.button("Save Comparison"):
        comparison_data_dict = comparison_data.to_dict()
        comparison_id = db.save_user_comparison(st.session_state.user.id, {
            "user_responses": user_responses,
            "recommendations": recommendations,
            "metrics": metrics,
            "comparison_data": comparison_data_dict
        })
        if comparison_id:
            st.success(f"Comparison saved successfully (ID: {comparison_id})")
        else:
            st.error("Failed to save comparison")

    # Load saved comparisons
    st.subheader("Saved Comparisons")
    saved_comparisons = db.get_user_comparisons(st.session_state.user.id)
    if saved_comparisons:
        selected_comparison = st.selectbox("Select a saved comparison", 
                                           options=[f"Comparison {c['id']} - {c['created_at']}" for c in saved_comparisons],
                                           format_func=lambda x: x.split(' - ')[1])
        if selected_comparison:
            comparison_id = int(selected_comparison.split(' ')[1])
            selected_data = next(c for c in saved_comparisons if c['id'] == comparison_id)
            st.json(selected_data['data'])
    else:
        st.write("No saved comparisons found.")

    # Export results
    if st.button("Download Results"):
        csv = export_to_csv(recommendations, comparison_data, metrics)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="dlt_framework_recommendation.csv",
            mime="text/csv"
        )
