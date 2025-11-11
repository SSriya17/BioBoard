import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

class WorkoutClassifier:
    def __init__(self):
        self.model = None
        self.exercises_db = None
        self.results = {}
        
    def train(self, progress_df, exercises_df):
        """Train decision tree on activity patterns"""
        if progress_df is None or len(progress_df) == 0:
            print("⚠ No progress data available for training")
            return False
        
        df = progress_df.copy()
        
        activity_goal_map = {
            'Weight Training': 'Muscle Gain',
            'HIIT': 'Weight Loss',
            'Running': 'Endurance',
            'Swimming': 'Endurance',
            'Cycling': 'Endurance',
            'Walking': 'General Fitness',
            'Yoga': 'General Fitness',
            'Dancing': 'General Fitness',
            'Tennis': 'General Fitness',
            'Basketball': 'General Fitness'
        }
        
        df['goal'] = df['activity_type'].map(activity_goal_map).fillna('General Fitness')
        
        df['intensity_encoded'] = df['intensity'].map({'Low': 1, 'Medium': 2, 'High': 3}).fillna(2)
        if 'fitness_level' in df.columns:
            df['fitness_level_normalized'] = df['fitness_level'] / df['fitness_level'].max()
        else:
            df['fitness_level_normalized'] = 0.5
        
        X = df[['intensity_encoded', 'fitness_level_normalized', 'duration_minutes']].values
        y = df['goal'].values
        
        self.model = DecisionTreeClassifier(max_depth=5, random_state=42)
        self.model.fit(X, y)
        
        y_pred = self.model.predict(X)
        accuracy = accuracy_score(y, y_pred)
        
        self.results = {
            'accuracy': accuracy,
            'training_samples': len(df),
            'classes': list(self.model.classes_),
            'classification_report': classification_report(y, y_pred, output_dict=True)
        }
        
        print(f"✓ Workout Classifier Trained:")
        print(f"  - Accuracy: {accuracy:.4f}")
        print(f"  - Classes: {self.results['classes']}")
        
        self.exercises_db = exercises_df
        return True
        
    def generate_workout_plan(self, goal, activity_level, experience_level='Moderate'):
        """Generate workout plan based on goal"""
        experience_map = {
            'Beginner': 0.2,
            'Moderate': 0.5,
            'Advanced': 0.8
        }
        fitness_level = experience_map.get(experience_level, 0.5)
        
        intensity_map = {
            'Sedentary': 1,
            'Light': 1,
            'Moderate': 2,
            'Active': 2,
            'Very Active': 3
        }
        intensity = intensity_map.get(activity_level, 2)
        
        if self.model:
            X = np.array([[intensity, fitness_level, 45]])
            predicted_goal = self.model.predict(X)[0]
        else:
            predicted_goal = goal
        
        plans = {
            'Weight Loss': [
                {'day': 'Day 1', 'focus': 'Full Body Circuit', 
                 'exercises': ['Squat 3x12', 'Push-ups 3x12', 'Rows 3x12', 'Plank 3x45s', '20 min Zone 2 cardio']},
                {'day': 'Day 2', 'focus': 'Cardio + Core',
                 'exercises': ['30-40 min Zone 2 cardio', 'Hanging knee raises 3x12', 'Side plank 3x30s/side']},
                {'day': 'Day 3', 'focus': 'Upper Body + Intervals',
                 'exercises': ['Incline DB Press 4x10', 'Lat Pulldown 4x10', 'Shoulder Press 3x12', 'Bike: 8x30s hard / 90s easy']},
                {'day': 'Day 4', 'focus': 'Lower Body + Steps',
                 'exercises': ['Deadlift 4x6', 'Lunges 3x12/leg', 'Leg Curl 3x12', '8-10k steps']},
            ],
            'Muscle Gain': [
                {'day': 'Day 1', 'focus': 'Upper Push',
                 'exercises': ['Bench Press 5x5', 'Incline DB Press 4x8', 'Overhead Press 4x8', 'Lateral Raises 4x12', 'Triceps 3x12']},
                {'day': 'Day 2', 'focus': 'Lower Strength',
                 'exercises': ['Back Squat 5x5', 'RDL 4x8', 'Leg Press 4x10', 'Calf Raise 4x15']},
                {'day': 'Day 3', 'focus': 'Upper Pull',
                 'exercises': ['Pull-ups 5xAMRAP', 'Barbell Row 4x8', 'Face Pull 4x12', 'Biceps 3x12']},
                {'day': 'Day 4', 'focus': 'Lower Hypertrophy',
                 'exercises': ['Front Squat 4x8', 'Hip Thrust 4x10', 'Leg Curl 4x12', 'Walking Lunges 3x12/leg']},
            ],
            'Endurance': [
                {'day': 'Day 1', 'focus': 'Zone 2 Base',
                 'exercises': ['Run/Cycle/Row 45-60 min Zone 2']},
                {'day': 'Day 2', 'focus': 'Strength Maintenance',
                 'exercises': ['Full Body 3x10: Squat, Press, Row, Lunge, Core']},
                {'day': 'Day 3', 'focus': 'Intervals',
                 'exercises': ['10x2 min hard / 2 min easy']},
                {'day': 'Day 4', 'focus': 'Long Session',
                 'exercises': ['75-90 min Zone 2']},
            ],
            'General Fitness': [
                {'day': 'Day 1', 'focus': 'Full Body A',
                 'exercises': ['Goblet Squat 4x10', 'Push-ups 4xAMRAP', 'Rows 4x10', 'Plank 3x45s']},
                {'day': 'Day 2', 'focus': 'Cardio 30-40',
                 'exercises': ['Zone 2 steady 30-40 min']},
                {'day': 'Day 3', 'focus': 'Full Body B',
                 'exercises': ['Deadlift 4x6', 'Overhead Press 4x8', 'Lat Pulldown 4x10', 'Side Plank 3x30s/side']},
                {'day': 'Day 4', 'focus': 'Intervals + Steps',
                 'exercises': ['6x1 min hard / 2 min easy', '8-10k steps']},
            ]
        }
        
        return plans.get(predicted_goal, plans['General Fitness'])
    
    def save(self, path='models/workout_classifier.joblib'):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'results': self.results
        }, path)
        print(f"✓ Model saved to {path}")
