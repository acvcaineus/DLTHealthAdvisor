import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from database import Database

class DecisionTreeRecommender:
    def __init__(self):
        self.decision_tree = DecisionTreeClassifier(random_state=42)
        self.scaler = StandardScaler()
        self.features = ['privacy', 'integration', 'data_volume', 'energy_efficiency', 'Security', 'Scalability', 'Governance', 'Interoperability', 'Operational Complexity', 'Implementation Cost', 'Latency']
        self.target = 'framework'
        self.train_model()

    def train_model(self):
        db = Database()
        training_data = db.get_training_data()
        if training_data.empty:
            return
        X = training_data[self.features]
        y = training_data[self.target]
        X_scaled = self.scaler.fit_transform(X)
        self.decision_tree.fit(X_scaled, y)

    def get_recommendations(self, user_input):
        X_user = self.scaler.transform([user_input])
        return self.decision_tree.predict(X_user)

    def sensitivity_analysis(self, user_input):
        baseline_prediction = self.get_recommendations(user_input)
        sensitivity_report = {}

        for feature_idx, feature in enumerate(self.features):
            perturbed_input = user_input.copy()
            # Perturbar levemente o valor da feature, aumentando 10%
            perturbed_input[feature_idx] *= 1.1
            perturbed_prediction = self.get_recommendations(perturbed_input)

            # Verificar se a predição mudou
            sensitivity_report[feature] = {
                "baseline": baseline_prediction[0],
                "perturbed": perturbed_prediction[0],
                "changed": baseline_prediction[0] != perturbed_prediction[0]
            }

        return sensitivity_report
