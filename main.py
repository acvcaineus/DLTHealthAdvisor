import streamlit as st
import pandas as pd
from decision_tree import DecisionTreeRecommender
from database import Database
from visualization import visualize_decision_tree, visualize_comparison
from utils import get_user_responses, calculate_metrics, generate_explanation, export_to_csv
from auth import create_user, authenticate_user, User
import json
from werkzeug.security import generate_password_hash

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
            password_hash = generate_password_hash(login_password)
            user_id = create_user(login_username, password_hash)
            if user_id:
                st.success("User registered successfully. Please log in.")
            else:
                st.error("Failed to register user. Username may already exist.")
        else:
            st.warning("Please enter both username and password to register.")

    # Add new user 'suenia' with password '1234'
    if not db.get_user_by_username('suenia'):
        suenia_password_hash = generate_password_hash('1234')
        suenia_user_id = create_user('suenia', suenia_password_hash)
        if suenia_user_id:
            st.success("User 'suenia' added successfully.")
        else:
            st.error("Failed to add user 'suenia'.")

else:
    st.write(f"Welcome, {st.session_state.user.username}!")
    if st.button("Logout"):
        st.session_state.user = None
        st.experimental_rerun()

    # Rest of the code remains unchanged
    # ...

