from flask import Flask, request, jsonify
from decision_tree import DecisionTreeRecommender
from database import Database

app = Flask(__name__)
recommender = DecisionTreeRecommender()
db = Database()

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json
    if not data or not all(key in data for key in recommender.features):
        return jsonify({"error": "Invalid input. All features must be provided."}), 400

    recommendations = recommender.get_recommendations(data)
    metrics = {
        'information_gain': recommender.decision_tree.tree_.compute_feature_importances(normalize=False).mean(),
        'tree_depth': recommender.decision_tree.get_depth(),
        'accuracy': 0.85  # Placeholder value, replace with actual accuracy calculation
    }
    
    sensitivity_results = recommender.sensitivity_analysis(data)
    
    response = {
        "recommendations": recommendations,
        "metrics": metrics,
        "sensitivity_analysis": sensitivity_results
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
