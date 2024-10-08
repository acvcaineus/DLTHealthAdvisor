import streamlit as st
import pandas as pd
from decision_tree import DecisionTreeRecommender
from database import Database
from visualization import visualize_decision_tree, visualize_comparison
from utils import get_user_responses, calculate_metrics, generate_explanation, export_to_csv

# Initialize database connection and test it
db = Database()
if not db.test_connection():
    st.error("Failed to connect to the database. Please check your database configuration.")
    st.stop()

# Initialize the decision tree recommender
recommender = DecisionTreeRecommender()

st.set_page_config(page_title="DLT Framework Recommender for Healthcare", layout="wide")

st.title("DLT Framework Recommender for Healthcare")

st.write("Welcome to the DLT Framework Recommender for Healthcare. This tool will help you choose the most suitable DLT framework based on your specific needs.")

# Display questions without collecting responses
get_user_responses()

# Placeholder for recommendations and metrics
st.subheader("Recommended DLT Frameworks")
st.write("Recommendations will be generated based on your responses in the future.")

st.subheader("Decision Tree Metrics")
st.write("Metrics will be calculated based on the decision tree model in the future.")

# Visualize decision tree
st.subheader("Decision Tree Visualization")
fig_tree = visualize_decision_tree(recommender.decision_tree)
st.plotly_chart(fig_tree)

# Compare recommended frameworks (using placeholder data)
st.subheader("Framework Comparison")
placeholder_frameworks = ['Ancile', 'BlockHR', 'RBEF']  # You can adjust these as needed
comparison_data = db.get_framework_data(placeholder_frameworks)
fig_comparison = visualize_comparison(comparison_data)
st.plotly_chart(fig_comparison)

# Generate and display explanations (using placeholder data)
st.subheader("Recommendations Explained")
for framework in placeholder_frameworks:
    explanation = generate_explanation(framework, comparison_data)
    st.write(f"**{framework}**")
    st.write(explanation)

# Export results button (disabled for now)
st.button("Download Results", disabled=True)
