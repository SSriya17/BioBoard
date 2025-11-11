import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error
from datetime import datetime, timedelta
import joblib
import os

class ProgressForecastModel:
    def __init__(self):
        self.model = None
        self.results = {}
        
    def train(self, progress_df):
        """Train time-series model on progress data"""
        if progress_df is None or len(progress_df) == 0:
            print("⚠ No progress data available for training")
            return False
        
        df = progress_df.copy()
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(['participant_id', 'date'])
        
        df['days'] = df.groupby('participant_id')['date'].transform(
            lambda x: (x - x.min()).dt.days
        )
        
        X = df[['days', 'weight_kg', 'calories_burned', 'daily_steps']].fillna(0).values
        y = df.groupby('participant_id')['weight_kg'].shift(-1).values
        
        mask = ~np.isnan(y)
        X = X[mask]
        y = y[mask]
        
        if len(X) == 0:
            print("⚠ No valid training data after preprocessing")
            return False
        
        self.model = LinearRegression()
        self.model.fit(X, y)
        
        y_pred = self.model.predict(X)
        r2 = r2_score(y, y_pred)
        mae = mean_absolute_error(y, y_pred)
        
        self.results = {
            'r2_score': r2,
            'mae': mae,
            'training_samples': len(X),
            'coefficients': self.model.coef_.tolist()
        }
        
        print(f"✓ Progress Forecast Model Trained:")
        print(f"  - R² Score: {r2:.4f}")
        print(f"  - MAE: {mae:.2f} kg")
        print(f"  - Training samples: {len(X)}")
        
        return True
        
    def forecast(self, historical_data, weeks=12):
        """Forecast progress for next N weeks"""
        if not historical_data or len(historical_data) == 0:
            return []
        
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        latest = df.iloc[-1]
        start_date = latest['date']
        start_weight = latest.get('weight_kg', 70)
        start_calories = latest.get('calories_burned', 200)
        start_steps = latest.get('daily_steps', 8000)
        
        forecast = []
        for week in range(1, weeks + 1):
            days = len(df) + (week * 7)
            
            if self.model:
                X = np.array([[days, start_weight, start_calories, start_steps]])
                predicted_weight = self.model.predict(X)[0]
            else:
                if len(df) > 1:
                    weight_change = (df.iloc[-1]['weight_kg'] - df.iloc[0]['weight_kg']) / len(df)
                    predicted_weight = start_weight + (weight_change * days)
                else:
                    predicted_weight = start_weight
            
            forecast.append({
                'date': (start_date + timedelta(weeks=week)).strftime('%Y-%m-%d'),
                'predicted_weight': round(predicted_weight, 1),
                'predicted_bmi': round(predicted_weight / ((latest.get('height_cm', 170) / 100) ** 2), 1)
            })
        
        return forecast
    
    def save(self, path='models/progress_forecast.joblib'):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'results': self.results
        }, path)
        print(f"✓ Model saved to {path}")
