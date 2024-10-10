import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_radar_chart(data):
    """Creates a radar chart for comparing DLT frameworks."""
    categories = data.columns[:-1]
    fig = go.Figure()

    for i in range(len(data)):
        fig.add_trace(go.Scatterpolar(
            r=data.iloc[i, :-1].values,
            theta=categories,
            fill='toself',
            name=data.iloc[i, -1]
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True
    )

    return fig

def create_parallel_coordinates(data):
    """Creates a parallel coordinates plot to visualize the comparison of frameworks."""
    fig = px.parallel_coordinates(data, color="Security",
                                  dimensions=['Security', 'Scalability', 'Energy Efficiency', 'Governance', 
                                              'Interoperability', 'Operational Complexity', 
                                              'Implementation Cost', 'Latency'],
                                  color_continuous_scale=px.colors.diverging.Tealrose,
                                  color_continuous_midpoint=5)
    return fig

def create_grouped_bar_chart(data):
    """Creates a grouped bar chart for comparing frameworks across different features."""
    fig = px.bar(data, x='framework', y=['Security', 'Scalability', 'Energy Efficiency', 'Governance',
                                         'Interoperability', 'Operational Complexity', 
                                         'Implementation Cost', 'Latency'],
                 barmode='group', title="Comparison of DLT Frameworks")
    return fig
