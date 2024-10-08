import streamlit as st
import pandas as pd
import io

def get_user_responses():
    st.write("Please consider the following questions:")
    
    st.write("1. Is high security against attacks (including Byzantine attacks) crucial for your application?")
    st.write("2. Does your application need to support a large volume of transactions and participants?")
    st.write("3. Is energy efficiency a critical factor for your network?")
    st.write("4. Do you require flexible governance that can be centralized or decentralized?")
    st.write("5. Is easy integration with legacy systems (e.g., EHRs) and other health systems important?")
    st.write("6. Is low operational complexity for implementation and maintenance in the healthcare environment important?")
    st.write("7. Is low implementation cost a priority for your project?")
    st.write("8. Is low latency crucial for your application, especially for real-time health monitoring?")
    
    return {}

def calculate_metrics(recommender, user_responses):
    # Calculate Information Gain
    information_gain = recommender.decision_tree.tree_.compute_feature_importances(normalize=False).mean()
    
    # Get Tree Depth
    tree_depth = recommender.decision_tree.get_depth()
    
    # Calculate Accuracy (this is a placeholder, real accuracy would require a test set)
    accuracy = 0.85  # Placeholder value
    
    return {
        'information_gain': information_gain,
        'tree_depth': tree_depth,
        'accuracy': accuracy
    }

def generate_explanation(framework, comparison_data):
    framework_data = comparison_data[comparison_data['name'] == framework].iloc[0]
    
    explanation = f"{framework} is recommended based on the following characteristics:\n\n"
    
    criteria = ['Security', 'Scalability', 'Energy Efficiency', 'Governance', 'Interoperability', 'Operational Complexity', 'Implementation Cost', 'Latency']
    
    for criterion in criteria:
        score = framework_data[criterion]
        if score >= 8:
            explanation += f"- High {criterion.lower()} (Score: {score}/10)\n"
        elif score >= 6:
            explanation += f"- Moderate {criterion.lower()} (Score: {score}/10)\n"
        else:
            explanation += f"- Low {criterion.lower()} (Score: {score}/10)\n"
    
    return explanation

def export_to_csv(recommendations, comparison_data, metrics):
    output = io.StringIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    # Write recommendations
    pd.DataFrame({'Recommendations': recommendations}).to_excel(writer, sheet_name='Recommendations', index=False)

    # Write comparison data
    comparison_data.to_excel(writer, sheet_name='Comparison', index=False)

    # Write metrics
    pd.DataFrame([metrics]).to_excel(writer, sheet_name='Metrics', index=False)

    writer.save()
    return output.getvalue()
