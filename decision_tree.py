import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder

class DecisionTreeRecommender:
    def __init__(self):
        self.decision_tree = DecisionTreeClassifier()
        self.label_encoder = LabelEncoder()
        self.features = ['security', 'scalability', 'energy_efficiency', 'governance', 'interoperability', 'operational_complexity', 'implementation_cost', 'latency']
        self.target = 'framework'
        self.train_model()

    def train_model(self):
        # Load training data from database
        from database import Database
        db = Database()
        training_data = db.get_training_data()

        X = training_data[self.features]
        y = self.label_encoder.fit_transform(training_data[self.target])

        self.decision_tree.fit(X, y)

    def get_recommendations(self, user_responses):
        user_input = np.array([user_responses[feature] for feature in self.features]).reshape(1, -1)
        prediction = self.decision_tree.predict(user_input)
        recommended_framework = self.label_encoder.inverse_transform(prediction)[0]
        
        # Get probabilities for all frameworks
        probabilities = self.decision_tree.predict_proba(user_input)[0]
        sorted_indices = np.argsort(probabilities)[::-1]
        
        # Return top 3 recommendations
        return [self.label_encoder.inverse_transform([idx])[0] for idx in sorted_indices[:3]]
