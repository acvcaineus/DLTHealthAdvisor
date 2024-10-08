import plotly.graph_objects as go
import plotly.express as px
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
import io

def visualize_decision_tree(decision_tree):
    # Create a BytesIO object to store the image
    buf = io.BytesIO()
    
    # Plot the decision tree
    plt.figure(figsize=(20,10))
    plot_tree(decision_tree, filled=True, feature_names=['privacy', 'integration', 'data_volume', 'energy_efficiency'])
    plt.savefig(buf, format='png')
    plt.close()
    
    # Create a Plotly figure from the image
    buf.seek(0)
    img = plt.imread(buf)
    fig = px.imshow(img)
    fig.update_layout(title_text="Decision Tree Visualization")
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    
    return fig

def visualize_comparison(comparison_data):
    criteria = ['Security', 'Scalability', 'Energy Efficiency', 'Governance', 'Interoperability', 'Operational Complexity', 'Implementation Cost', 'Latency']
    
    fig = go.Figure()
    
    for framework in comparison_data['name']:
        fig.add_trace(go.Scatterpolar(
            r=comparison_data.loc[comparison_data['name'] == framework, criteria].values.flatten().tolist(),
            theta=criteria,
            fill='toself',
            name=framework
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True,
        title="DLT Framework Comparison"
    )
    
    return fig
