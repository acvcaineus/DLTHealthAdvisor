from visualization import create_radar_chart, create_parallel_coordinates, create_grouped_bar_chart

def hybrid_recommendation(recommender):
    # Recomendação com Árvore de Decisão (Machine Learning)
    st.subheader("Hybrid Recommendation (Machine Learning)")
    user_responses = {
        'security': st.slider("Security", 1, 10, 5),
        'scalability': st.slider("Scalability", 1, 10, 5),
        'energy_efficiency': st.slider("Energy Efficiency", 1, 10, 5),
        'governance': st.slider("Governance", 1, 10, 5),
        'interoperability': st.slider("Interoperability", 1, 10, 5),
        'operational_complexity': st.slider("Operational Complexity", 1, 10, 5),
        'implementation_cost': st.slider("Implementation Cost", 1, 10, 5),
        'latency': st.slider("Latency", 1, 10, 5),
    }

    if st.button("Get Hybrid Recommendations"):
        recommendations = recommender.get_recommendations(user_responses)
        st.subheader("Recommended DLT Framework")
        for framework in recommendations:
            st.write(framework)

        # Carregar dados para visualização
        db = Database()
        training_data = db.get_training_data()

        # Visualização da Comparação dos Frameworks
        st.subheader("Multi-dimensional Comparison (Radar Chart)")
        st.plotly_chart(create_radar_chart(training_data))

        st.subheader("Parallel Coordinates Comparison")
        st.plotly_chart(create_parallel_coordinates(training_data))

        st.subheader("Grouped Bar Chart Comparison")
        st.plotly_chart(create_grouped_bar_chart(training_data))

    if st.button("Perform Sensitivity Analysis"):
        sensitivity_results = recommender.sensitivity_analysis(user_responses)
        st.subheader("Sensitivity Analysis Results")
        for feature, sensitive in sensitivity_results.items():
            st.write(f"{feature}: {'Sensitive' if sensitive else 'Not Sensitive'}")
