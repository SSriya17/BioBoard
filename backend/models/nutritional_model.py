import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import os

class NutritionalTargetModel:
    def __init__(self):
        self.model_calories = None
        self.model_protein = None
        self.model_carbs = None
        self.model_fats = None
        self.scaler = StandardScaler()
        self.results = {}
        
    def train(self, dietary_df):
        """Train models on dietary data"""
        if dietary_df is None or len(dietary_df) == 0:
            print("⚠ No dietary data available for training")
            return False
        
        df = dietary_df.copy()
        
        # Feature engineering
        df['gender_encoded'] = df['Gender'].map({'Male': 1, 'Female': 0})
        df['activity_encoded'] = df['Physical_Activity_Level'].map({
            'Sedentary': 1.2, 'Moderate': 1.55, 'Active': 1.725
        }).fillna(1.55)
        
        # Features for training
        X = df[['Age', 'Weight_kg', 'Height_cm', 'BMI', 'gender_encoded', 'activity_encoded']].values
        X = self.scaler.fit_transform(X)
        
        # Targets
        y_calories = df['Daily_Caloric_Intake'].values
        y_protein = y_calories * 0.15 / 4  # 15% protein
        y_carbs = y_calories * 0.50 / 4    # 50% carbs
        y_fats = y_calories * 0.35 / 9     # 35% fats
        
        # Train models
        self.model_calories = LinearRegression().fit(X, y_calories)
        self.model_protein = LinearRegression().fit(X, y_protein)
        self.model_carbs = LinearRegression().fit(X, y_carbs)
        self.model_fats = LinearRegression().fit(X, y_fats)
        
        # Calculate metrics
        y_pred_cal = self.model_calories.predict(X)
        y_pred_prot = self.model_protein.predict(X)
        y_pred_carbs = self.model_carbs.predict(X)
        y_pred_fats = self.model_fats.predict(X)
        
        self.results = {
            'calories_r2': r2_score(y_calories, y_pred_cal),
            'calories_mae': mean_absolute_error(y_calories, y_pred_cal),
            'protein_r2': r2_score(y_protein, y_pred_prot),
            'protein_mae': mean_absolute_error(y_protein, y_pred_prot),
            'carbs_r2': r2_score(y_carbs, y_pred_carbs),
            'carbs_mae': mean_absolute_error(y_carbs, y_pred_carbs),
            'fats_r2': r2_score(y_fats, y_pred_fats),
            'fats_mae': mean_absolute_error(y_fats, y_pred_fats),
            'training_samples': len(df)
        }
        
        print(f"✓ Nutritional Model Trained:")
        print(f"  - Calories R²: {self.results['calories_r2']:.4f}, MAE: {self.results['calories_mae']:.2f}")
        print(f"  - Protein R²: {self.results['protein_r2']:.4f}, MAE: {self.results['protein_mae']:.2f}")
        print(f"  - Carbs R²: {self.results['carbs_r2']:.4f}, MAE: {self.results['carbs_mae']:.2f}")
        print(f"  - Fats R²: {self.results['fats_r2']:.4f}, MAE: {self.results['fats_mae']:.2f}")
        
        return True
        
    def predict(self, age, gender, height_cm, weight_kg, activity_level):
        """Predict nutritional targets"""
        bmi = weight_kg / ((height_cm / 100) ** 2)
        gender_encoded = 1 if gender.lower() == 'male' else 0
        
        activity_map = {
            'Sedentary': 1.2,
            'Light': 1.375,
            'Moderate': 1.55,
            'Active': 1.725,
            'Very Active': 1.9
        }
        activity_encoded = activity_map.get(activity_level, 1.55)
        
        X = np.array([[age, weight_kg, height_cm, bmi, gender_encoded, activity_encoded]])
        X = self.scaler.transform(X)
        
        calories = max(1200, int(self.model_calories.predict(X)[0]))
        protein = max(50, int(self.model_protein.predict(X)[0]))
        carbs = max(100, int(self.model_carbs.predict(X)[0]))
        fats = max(30, int(self.model_fats.predict(X)[0]))
        
        return {
            'calories': calories,
            'protein': protein,
            'carbs': carbs,
            'fats': fats
        }
    
    def save(self, path='models/nutritional_model.joblib'):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model_calories': self.model_calories,
            'model_protein': self.model_protein,
            'model_carbs': self.model_carbs,
            'model_fats': self.model_fats,
            'scaler': self.scaler,
            'results': self.results
        }, path)
        print(f"✓ Model saved to {path}")
