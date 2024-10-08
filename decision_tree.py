import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler

class DecisionTreeRecommender:
    def __init__(self):
        self.decision_tree = DecisionTreeClassifier(random_state=42)
        self.label_encoder = LabelEncoder()
        self.features = ['security', 'scalability', 'energy_efficiency', 'governance', 'interoperability', 'operational_complexity', 'implementation_cost', 'latency']
        self.target = 'framework'
        self.train_model()

    def train_model(self):
        # Load training data from database
        from database import Database
        db = Database()
        training_data = db.get_training_data()

        # Normalize the features
        self.scaler = StandardScaler()
        X = self.scaler.fit_transform(training_data[self.features])
        y = self.label_encoder.fit_transform(training_data[self.target])

        self.decision_tree.fit(X, y)

    def get_recommendations(self, user_responses):
        user_input = np.array([user_responses[feature] for feature in self.features]).reshape(1, -1)
        scaled_input = self.scaler.transform(user_input)
        prediction = self.decision_tree.predict(scaled_input)
        recommended_framework = self.label_encoder.inverse_transform(prediction)[0]

        # Get probabilities for all frameworks
        probabilities = self.decision_tree.predict_proba(scaled_input)[0]
        sorted_indices = np.argsort(probabilities)[::-1]

        # Return top 3 recommendations
        return [self.label_encoder.inverse_transform([idx])[0] for idx in sorted_indices[:3]]

    def get_feature_importances(self):
        return dict(zip(self.features, self.decision_tree.feature_importances_))

    def sensitivity_analysis(self, user_responses, num_perturbations=10, perturbation_range=0.1):
        original_input = np.array([user_responses[feature] for feature in self.features]).reshape(1, -1)
        scaled_original_input = self.scaler.transform(original_input)
        original_prediction = self.decision_tree.predict(scaled_original_input)[0]
        
        sensitivity_results = {}
        
        for feature_idx, feature in enumerate(self.features):
            changes = 0
            for _ in range(num_perturbations):
                perturbed_input = original_input.copy()
                perturbation = np.random.uniform(-perturbation_range, perturbation_range)
                perturbed_input[0, feature_idx] += perturbation
                
                scaled_perturbed_input = self.scaler.transform(perturbed_input)
                perturbed_prediction = self.decision_tree.predict(scaled_perturbed_input)[0]
                
                if perturbed_prediction != original_prediction:
                    changes += 1
            
            sensitivity_results[feature] = changes / num_perturbations
        
        return sensitivity_results
