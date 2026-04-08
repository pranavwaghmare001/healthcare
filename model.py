import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Health advice and severity mappings
DISEASE_INFO = {
    "Common Cold": {"severity": "Low", "advice": "Rest, stay hydrated, and take over-the-counter cold medications."},
    "Influenza (Flu)": {"severity": "Medium", "advice": "Get plenty of rest, drink fluids, and consider antiviral drugs if prescribed by a doctor."},
    "COVID-19": {"severity": "High", "advice": "Isolate yourself, monitor oxygen levels, and consult a healthcare provider immediately."},
    "Allergies": {"severity": "Low", "advice": "Avoid allergens and take antihistamines."},
    "Food Poisoning": {"severity": "Medium", "advice": "Stay hydrated with electrolytes, eat bland foods. Seek medical help if severe."},
    "Migraine": {"severity": "Medium", "advice": "Rest in a quiet, dark room. Take prescribed migraine medication."},
    "Gastroenteritis": {"severity": "Medium", "advice": "Drink plenty of fluids. Seek medical care if unable to keep liquids down."},
    "Asthma": {"severity": "High", "advice": "Use your rescue inhaler. If breathing does not improve, seek emergency medical care."},
    "Bronchitis": {"severity": "Medium", "advice": "Rest, drink fluids, use a humidifier, and avoid lung irritants."},
    "Pneumonia": {"severity": "High", "advice": "Seek immediate medical attention for antibiotics and respiratory therapy."},
    "Malaria": {"severity": "High", "advice": "Requires immediate medical diagnosis and prescription antimalarial medication."},
    "Dengue Fever": {"severity": "High", "advice": "Seek medical attention immediately. Manage symptoms with pain relievers but avoid ibuprofen/aspirin."},
    "Typhoid": {"severity": "Medium", "advice": "Requires medical diagnosis and a course of antibiotics."},
    "Anemia": {"severity": "Medium", "advice": "Eat iron-rich foods, and consult a doctor for a blood test and supplements."},
    "Diabetes": {"severity": "High", "advice": "Requires medical diagnosis, lifestyle changes, and potentially insulin/medications."},
    "Hypertension": {"severity": "High", "advice": "Requires medical supervision, lifestyle modifications, and blood pressure medications."},
    "Chickenpox": {"severity": "Low", "advice": "Rest, use calamine lotion for itching, and avoid scratching."},
}

class DiseaseModel:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.symptoms_list = []
        self.is_trained = False

    def load_and_train(self, data_path="dataset.csv"):
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Dataset not found at {data_path}. Please run data_generator.py first.")
            
        df = pd.read_csv(data_path)
        
        # Features and target
        X = df.drop("Disease", axis=1)
        y = df["Disease"]
        
        self.symptoms_list = list(X.columns)
        
        # Train-test split for evaluation
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Training
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Validation
        preds = self.model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        return acc

    def predict(self, user_symptoms):
        """
        Given a list of symptoms, predict diseases.
        Returns: Top 3 diseases with probabilities and feature contribution.
        """
        if not self.is_trained:
            raise ValueError("Model is not trained yet.")

        # Create input array
        input_vector = np.zeros(len(self.symptoms_list))
        
        matched_symptoms = []
        for symptom in user_symptoms:
            if symptom in self.symptoms_list:
                idx = self.symptoms_list.index(symptom)
                input_vector[idx] = 1
                matched_symptoms.append(symptom)
                
        # Reshape to 2D array for sklearn
        input_vector = input_vector.reshape(1, -1)
        
        # Get probabilities
        probabilities = self.model.predict_proba(input_vector)[0]
        
        # Get Top 3
        top_indices = np.argsort(probabilities)[::-1][:3]
        classes = self.model.classes_
        
        results = []
        for idx in top_indices:
            disease = classes[idx]
            prob = probabilities[idx]
            if prob > 0:
                info = DISEASE_INFO.get(disease, {"severity": "Unknown", "advice": "Consult a doctor."})
                results.append({
                    "disease": disease,
                    "probability": round(prob * 100, 2),
                    "severity": info["severity"],
                    "advice": info["advice"]
                })
                
        # Feature importance for explainability
        # We find which provided symptoms are most important globally for the model
        global_importances = self.model.feature_importances_
        feature_contributions = []
        for sym in matched_symptoms:
            sym_idx = self.symptoms_list.index(sym)
            feature_contributions.append({
                "symptom": sym,
                "importance": global_importances[sym_idx]
            })
            
        feature_contributions.sort(key=lambda x: x["importance"], reverse=True)
            
        return results, feature_contributions

    def get_all_symptoms(self):
        return self.symptoms_list
