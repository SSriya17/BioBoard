#!/usr/bin/env python3
"""
Train all ML models and generate verifiable results
"""

import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_loader import load_datasets
from models.nutritional_model import NutritionalTargetModel
from models.meal_recommender import MealRecommender
from models.workout_classifier import WorkoutClassifier
from models.progress_forecast import ProgressForecastModel

def main():
    print("=" * 60)
    print("BIOBOARD ML MODEL TRAINING")
    print("=" * 60)
    print()
    
    print("Step 1: Loading datasets...")
    print("-" * 60)
    datasets = load_datasets()
    print()
    
    all_results = {
        'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'models': {}
    }
    
    print("Step 2: Training Nutritional Targets Model...")
    print("-" * 60)
    nutritional_model = NutritionalTargetModel()
    if datasets['dietary'] is not None:
        success = nutritional_model.train(datasets['dietary'])
        if success:
            nutritional_model.save('models/nutritional_model.joblib')
            all_results['models']['nutritional_targets'] = nutritional_model.results
            
            test_pred = nutritional_model.predict(25, 'Male', 175, 75, 'Moderate')
            all_results['models']['nutritional_targets']['test_prediction'] = test_pred
            print(f"  Test Prediction (25yo Male, 175cm, 75kg, Moderate):")
            print(f"    Calories: {test_pred['calories']}, Protein: {test_pred['protein']}g, Carbs: {test_pred['carbs']}g, Fats: {test_pred['fats']}g")
    print()
    
    print("Step 3: Creating Meal Recommendation System...")
    print("-" * 60)
    meal_recommender = MealRecommender()
    if datasets['dietary'] is not None:
        meal_recommender.create_meal_database(datasets['dietary'])
        all_results['models']['meal_recommendations'] = meal_recommender.results
        
        test_meals = meal_recommender.recommend_meals(2000, ['None'], 'Mexican', 3)
        all_results['models']['meal_recommendations']['test_recommendation'] = test_meals
        print(f"  Test Recommendation (2000 cal, Mexican, 3 meals):")
        for i, meal in enumerate(test_meals, 1):
            print(f"    Meal {i}: {meal['name']} - {meal['calories']} cal")
    print()
    
    print("Step 4: Training Workout Plan Classifier...")
    print("-" * 60)
    workout_classifier = WorkoutClassifier()
    if datasets['progress'] is not None:
        success = workout_classifier.train(datasets['progress'], datasets['exercises'])
        if success:
            workout_classifier.save('models/workout_classifier.joblib')
            all_results['models']['workout_plan'] = workout_classifier.results
            
            test_workout = workout_classifier.generate_workout_plan('Weight Loss', 'Moderate', 'Moderate')
            all_results['models']['workout_plan']['test_workout'] = test_workout
            print(f"  Test Workout Plan (Weight Loss, Moderate):")
            print(f"    Generated {len(test_workout)} workout days")
    print()
    
    print("Step 5: Training Progress Forecast Model...")
    print("-" * 60)
    progress_model = ProgressForecastModel()
    if datasets['progress'] is not None:
        success = progress_model.train(datasets['progress'])
        if success:
            progress_model.save('models/progress_forecast.joblib')
            all_results['models']['progress_forecast'] = progress_model.results
            
            sample_data = datasets['progress'].head(10).to_dict('records')
            test_forecast = progress_model.forecast(sample_data, 4)
            all_results['models']['progress_forecast']['test_forecast'] = test_forecast
            print(f"  Test Forecast (4 weeks):")
            for week in test_forecast:
                print(f"    {week['date']}: Weight {week['predicted_weight']}kg, BMI {week['predicted_bmi']}")
    print()
    
    print("Step 6: Saving results...")
    print("-" * 60)
    results_file = 'model_results.json'
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"✓ Results saved to {results_file}")
    print()
    
    print("=" * 60)
    print("TRAINING COMPLETE - SUMMARY")
    print("=" * 60)
    print(f"Training Date: {all_results['training_date']}")
    print(f"Models Trained: {len(all_results['models'])}/4")
    print()
    print("Model Results:")
    for model_name, results in all_results['models'].items():
        print(f"  - {model_name}: ✓ Trained")
        if 'r2_score' in results:
            print(f"    R² Score: {results['r2_score']:.4f}")
        if 'accuracy' in results:
            print(f"    Accuracy: {results['accuracy']:.4f}")
        if 'calories_r2' in results:
            print(f"    Calories R²: {results['calories_r2']:.4f}")
    print()
    print("=" * 60)
    print("✓ All models trained successfully!")
    print("=" * 60)

if __name__ == '__main__':
    main()
