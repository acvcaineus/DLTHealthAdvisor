import streamlit as st
import pandas as pd
import io
import json

def get_user_responses():
    responses = {}
    
    responses['privacy'] = st.radio(
        "1. Is data privacy a critical concern for your application?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['integration'] = st.radio(
        "2. Do you need seamless integration with existing healthcare systems?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['data_volume'] = st.radio(
        "3. Do you expect to handle large volumes of data?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['energy_efficiency'] = st.radio(
        "4. Is energy efficiency a critical factor for your network?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['Security'] = st.radio(
        "5. Do you require high-level security measures?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['Scalability'] = st.radio(
        "6. Is scalability a key requirement for your application?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['Governance'] = st.radio(
        "7. Do you need flexible governance options?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['Interoperability'] = st.radio(
        "8. Is interoperability with other blockchain networks important?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['Operational Complexity'] = st.radio(
        "9. Can you handle high operational complexity?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['Implementation Cost'] = st.radio(
        "10. Is low implementation cost a priority?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['Latency'] = st.radio(
        "11. Do you require low latency for your applications?",
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

def export_saved_comparison(saved_comparison):
    output = io.StringIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    # Write user responses
    pd.DataFrame([saved_comparison['data']['user_responses']]).to_excel(writer, sheet_name='User Responses', index=False)

    # Write recommendations
    pd.DataFrame({'Recommendations': saved_comparison['data']['recommendations']}).to_excel(writer, sheet_name='Recommendations', index=False)

    # Write comparison data
    comparison_data = pd.DataFrame(saved_comparison['data']['comparison_data'])
    comparison_data.to_excel(writer, sheet_name='Comparison', index=False)

    # Write metrics
    pd.DataFrame([saved_comparison['data']['metrics']]).to_excel(writer, sheet_name='Metrics', index=False)

    writer.save()
    return output.getvalue()
