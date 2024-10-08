import streamlit as st
import pandas as pd
from decision_tree import DecisionTreeRecommender
from database import Database
from visualization import visualize_decision_tree, visualize_comparison
from utils import get_user_responses, calculate_metrics, generate_explanation, export_to_csv

# Initialize database connection
db = Database()

# Initialize the decision tree recommender
recommender = DecisionTreeRecommender()

st.set_page_config(page_title="DLT Framework Recommender for Healthcare", layout="wide")

st.title("DLT Framework Recommender for Healthcare")

st.write("Welcome to the DLT Framework Recommender for Healthcare. This tool will help you choose the most suitable DLT framework based on your specific needs.")

# Get user responses
user_responses = get_user_responses()

# Get recommendations
recommendations = recommender.get_recommendations(user_responses)

# Calculate metrics
metrics = calculate_metrics(recommender, user_responses)

# Display recommendations and metrics
st.subheader("Recommended DLT Frameworks")
for framework in recommendations:
    st.write(f"- {framework}")

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

# Export results
if st.button("Download Results"):
    csv_data = export_to_csv(recommendations, comparison_data, metrics)
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="dlt_framework_recommendations.csv",
        mime="text/csv"
    )
