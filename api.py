from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from decision_tree import DecisionTreeRecommender
from database import Database
from auth import authenticate_user
import datetime

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Defina uma chave secreta segura
jwt = JWTManager(app)

recommender = DecisionTreeRecommender()
db = Database()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = authenticate_user(username, password)
    if user:
        access_token = create_access_token(identity=user['id'], expires_delta=datetime.timedelta(hours=1))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/recommend', methods=['POST'])
@jwt_required()
def recommend():
    data = request.json
    approach = data.get("approach", "rule-based")
    user_responses = data.get("user_responses")

    if not user_responses:
        return jsonify({"error": "No user responses provided"}), 400

    if approach == "rule-based":
        recommendation = rule_based_api(user_responses)
    elif approach == "hybrid":
        recommendation = recommender.get_recommendations(user_responses)
    else:
        return jsonify({"error": "Invalid approach provided"}), 400

    return jsonify({"recommendation": recommendation}), 200

def rule_based_api(user_responses):
    # Implementação simplificada de uma lógica de recomendação baseada em regras
    if user_responses.get('security', 0) > 8 and user_responses.get('scalability', 0) > 7:
        return ["Ancile"]
    elif user_responses.get('energy_efficiency', 0) > 7:
        return ["ChainSure"]
    else:
        return ["BlockHR"]

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
