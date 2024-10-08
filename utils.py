import streamlit as st
import pandas as pd
import io

def get_user_responses():
    responses = {}
    
    responses['privacy'] = st.radio(
        "Does the application require high privacy and centralized control?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['integration'] = st.radio(
        "Does the network need to integrate with legacy healthcare systems (e.g., EHRs, hospital databases)?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['data_volume'] = st.radio(
        "Does the infrastructure need to handle large volumes of data or IoT devices?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['energy_efficiency'] = st.radio(
        "Is energy efficiency a crucial factor for the network?",
        ('Yes', 'No')
    ) == 'Yes'
    
    return responses

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
