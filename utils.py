import streamlit as st
import pandas as pd
import io

def get_user_responses():
    responses = {}
    
    responses['security'] = st.radio(
        "Is high security against attacks (including Byzantine attacks) crucial for your application?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['scalability'] = st.radio(
        "Does your application need to support a large volume of transactions and participants?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['energy_efficiency'] = st.radio(
        "Is energy efficiency a critical factor for your network?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['governance'] = st.radio(
        "Do you require flexible governance that can be centralized or decentralized?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['interoperability'] = st.radio(
        "Is easy integration with legacy systems (e.g., EHRs) and other health systems important?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['operational_complexity'] = st.radio(
        "Is low operational complexity for implementation and maintenance in the healthcare environment important?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['implementation_cost'] = st.radio(
        "Is low implementation cost a priority for your project?",
        ('Yes', 'No')
    ) == 'Yes'
    
    responses['latency'] = st.radio(
        "Is low latency crucial for your application, especially for real-time health monitoring?",
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
    
    criteria = ['Security', 'Scalability', 'Energy_Efficiency', 'Governance', 'Interoperability', 'Operational_Complexity', 'Implementation_Cost', 'Latency']
    
    for criterion in criteria:
        score = framework_data[criterion]
        if score >= 8:
            explanation += f"- High {criterion.lower().replace('_', ' ')} (Score: {score}/10)\n"
        elif score >= 6:
            explanation += f"- Moderate {criterion.lower().replace('_', ' ')} (Score: {score}/10)\n"
        else:
            explanation += f"- Low {criterion.lower().replace('_', ' ')} (Score: {score}/10)\n"
    
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
