#!/usr/bin/env python3
"""
Flask API server for BioBoard
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import os
import sys
import numpy as np
import pandas as pd

# Add backend to path  
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.nutritional_model import NutritionalTargetModel
from models.meal_recommender import MealRecommender
from models.meal_recommender_ml import MealRecommenderML
from models.workout_classifier import WorkoutClassifier
from models.workout_generator_ml import WorkoutGeneratorML
from models.progress_forecast import ProgressForecastModel
from utils.data_loader import load_datasets

app = Flask(__name__)
CORS(app)

# Global model instances
nutritional_model = None
meal_recommender = None
meal_recommender_ml = None
workout_classifier = None
workout_generator_ml = None
progress_model = None

def load_models():
    """Load trained models"""
    global nutritional_model, meal_recommender, meal_recommender_ml, workout_classifier, workout_generator_ml, progress_model
    
    # Get the directory where this script is located
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(backend_dir, 'models')
    base_dir = os.path.dirname(backend_dir)  # Parent directory (BioBoard root)
    
    print("Loading models...")
    
    # Load nutritional model
    try:
        model_path = os.path.join(models_dir, 'nutritional_model.joblib')
        if os.path.exists(model_path):
            data = joblib.load(model_path)
            nutritional_model = NutritionalTargetModel()
            nutritional_model.model_calories = data['model_calories']
            nutritional_model.model_protein = data['model_protein']
            nutritional_model.model_carbs = data['model_carbs']
            nutritional_model.model_fats = data['model_fats']
            nutritional_model.scaler = data['scaler']
            nutritional_model.results = data.get('results', {})
            print("✓ Nutritional model loaded")
        else:
            print("⚠ Nutritional model not found, will use fallback")
    except Exception as e:
        print(f"⚠ Error loading nutritional model: {e}")
        import traceback
        traceback.print_exc()
    
    # Initialize ML meal recommender (preferred) and fallback meal recommender
    try:
        # Change to base directory for data loading
        original_dir = os.getcwd()
        os.chdir(base_dir)
        datasets = load_datasets(base_path='.')
        os.chdir(original_dir)
        
        # Try to load ML meal recommender first
        meal_ml_path = os.path.join(models_dir, 'meal_recommender_ml.joblib')
        meal_recommender_ml = MealRecommenderML()
        
        if os.path.exists(meal_ml_path):
            try:
                meal_recommender_ml.load(meal_ml_path)
                # Verify model is loaded correctly
                if meal_recommender_ml.meals_df is not None and len(meal_recommender_ml.meals_df) > 0:
                    print(f"✓ ML Meal recommender loaded from file ({len(meal_recommender_ml.meals_df)} meals)")
                else:
                    print("⚠ ML Meal recommender loaded but meals_df is empty, retraining...")
                    # PRIORITY: Use meals dataset if available
                    if datasets.get('meals') is not None and len(datasets['meals']) > 0:
                        if meal_recommender_ml.train(meals_df=datasets['meals']):
                            meal_recommender_ml.save(meal_ml_path)
                            print(f"✓ ML Meal recommender retrained with {len(datasets['meals'])} USDA meals and saved")
                        else:
                            print("⚠ ML Meal recommender retraining failed")
                            meal_recommender_ml = None
                    elif datasets.get('dietary') is not None:
                        if meal_recommender_ml.train(dietary_df=datasets['dietary']):
                            meal_recommender_ml.save(meal_ml_path)
                            print("✓ ML Meal recommender retrained and saved")
                        else:
                            print("⚠ ML Meal recommender retraining failed")
                            meal_recommender_ml = None
                    else:
                        meal_recommender_ml = None
            except Exception as e:
                print(f"⚠ Error loading ML meal recommender: {e}")
                import traceback
                traceback.print_exc()
                meal_recommender_ml = None
        # Train new model with meals dataset (PRIORITY) or dietary dataset (fallback)
        elif datasets.get('meals') is not None and len(datasets['meals']) > 0:
            if meal_recommender_ml.train(meals_df=datasets['meals']):
                meal_recommender_ml.save(meal_ml_path)
                print(f"✓ ML Meal recommender trained with {len(datasets['meals'])} USDA meals and saved")
            else:
                print("⚠ ML Meal recommender training failed")
                meal_recommender_ml = None
        elif datasets.get('dietary') is not None:
            if meal_recommender_ml.train(dietary_df=datasets['dietary']):
                meal_recommender_ml.save(meal_ml_path)
                print("✓ ML Meal recommender trained and saved")
            else:
                print("⚠ ML Meal recommender training failed")
                meal_recommender_ml = None
        else:
            print("⚠ No meal or dietary data for ML meal recommender")
            meal_recommender_ml = None
        
        # Fallback: Initialize traditional meal recommender
        meal_recommender = MealRecommender()
        if datasets['dietary'] is not None:
            meal_recommender.create_meal_database(datasets['dietary'])
            print("✓ Fallback meal recommender initialized")
        else:
            print("⚠ No dietary data, meal recommender will use fallback")
    except Exception as e:
        print(f"⚠ Error initializing meal recommender: {e}")
        import traceback
        traceback.print_exc()
        meal_recommender_ml = None
        meal_recommender = MealRecommender()  # Initialize empty
    
    # Load ML workout generator (preferred) and fallback workout classifier
    try:
        original_dir = os.getcwd()
        os.chdir(base_dir)
        datasets = load_datasets(base_path='.')
        os.chdir(original_dir)
        
        # Try to load ML workout generator first
        workout_ml_path = os.path.join(models_dir, 'workout_generator_ml.joblib')
        workout_generator_ml = WorkoutGeneratorML()
        
        if os.path.exists(workout_ml_path):
            workout_generator_ml.load(workout_ml_path)
            print("✓ ML Workout generator loaded from file")
        elif datasets['exercises'] is not None:
            if workout_generator_ml.train(datasets['exercises']):
                workout_generator_ml.save(workout_ml_path)
                print("✓ ML Workout generator trained and saved")
            else:
                print("⚠ ML Workout generator training failed")
                workout_generator_ml = None
        else:
            print("⚠ No exercise data for ML workout generator")
            workout_generator_ml = None
        
        # Fallback: Load workout classifier
        workout_classifier = WorkoutClassifier()
        classifier_path = os.path.join(models_dir, 'workout_classifier.joblib')
        if os.path.exists(classifier_path):
            data = joblib.load(classifier_path)
            workout_classifier.model = data.get('model')
            workout_classifier.results = data.get('results', {})
            if datasets['exercises'] is not None:
                workout_classifier.exercises_db = datasets['exercises']
            print("✓ Fallback workout classifier loaded from file")
        elif datasets['progress'] is not None and datasets['exercises'] is not None:
            workout_classifier.train(datasets['progress'], datasets['exercises'])
            print("✓ Fallback workout classifier trained")
        else:
            print("⚠ Workout classifier will use fallback")
    except Exception as e:
        print(f"⚠ Error loading workout generator: {e}")
        import traceback
        traceback.print_exc()
        workout_generator_ml = None
        workout_classifier = WorkoutClassifier()  # Initialize empty
    
    # Load progress forecast model
    try:
        original_dir = os.getcwd()
        os.chdir(base_dir)
        datasets = load_datasets(base_path='.')
        os.chdir(original_dir)
        
        progress_model = ProgressForecastModel()
        # Try to load pre-trained model first
        forecast_path = os.path.join(models_dir, 'progress_forecast.joblib')
        if os.path.exists(forecast_path):
            data = joblib.load(forecast_path)
            progress_model.model = data.get('model')
            progress_model.results = data.get('results', {})
            print("✓ Progress forecast model loaded from file")
        elif datasets['progress'] is not None:
            progress_model.train(datasets['progress'])
            print("✓ Progress forecast model trained")
        else:
            print("⚠ Progress forecast model will use fallback")
    except Exception as e:
        print(f"⚠ Error loading progress forecast model: {e}")
        import traceback
        traceback.print_exc()
        progress_model = ProgressForecastModel()  # Initialize empty

@app.route('/', methods=['GET'])
def home():
    """Home endpoint"""
    return "✅ Bioboard API is running!"

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'BioBoard API is running'})

@app.route('/api/nutritional-targets', methods=['POST'])
def get_nutritional_targets():
    """Get nutritional targets based on user data"""
    try:
        data = request.json
        age = int(data.get('age', 25))
        weight_kg = float(data.get('weight', 70))
        height_feet = int(data.get('heightFeet', 5))
        height_inches = int(data.get('heightInches', 10))
        activity_level = data.get('activityLevel', 'Moderate')
        gender = data.get('gender', 'Male')  # Default to Male if not provided
        
        # Convert height to cm
        height_cm = (height_feet * 12 + height_inches) * 2.54
        
        if nutritional_model and nutritional_model.model_calories:
            result = nutritional_model.predict(age, gender, height_cm, weight_kg, activity_level)
        else:
            # Fallback calculation
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + (5 if gender.lower() == 'male' else -161)
            activity_multipliers = {
                'Sedentary': 1.2,
                'Light': 1.375,
                'Moderate': 1.55,
                'Active': 1.725,
                'Very Active': 1.9
            }
            multiplier = activity_multipliers.get(activity_level, 1.55)
            calories = max(1200, int(bmr * multiplier))
            result = {
                'calories': calories,
                'protein': max(50, int(calories * 0.15 / 4)),
                'carbs': max(100, int(calories * 0.50 / 4)),
                'fats': max(30, int(calories * 0.35 / 9))
            }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/meal-recommendations', methods=['POST'])
def get_meal_recommendations():
    """Get meal recommendations based on dietary preferences using ML ONLY"""
    try:
        data = request.json
        calorie_goal = int(data.get('calorieGoal', 2000))
        dietary_preferences = data.get('dietaryPreferences', 'Omnivore')
        num_meals = int(data.get('numMeals', 3))
        
        # USE ML MEAL RECOMMENDER ONLY - NO FALLBACKS
        if not meal_recommender_ml or not hasattr(meal_recommender_ml, 'meals_df') or meal_recommender_ml.meals_df is None or len(meal_recommender_ml.meals_df) == 0:
            print("✗ ERROR: ML meal recommender not available!")
            return jsonify({'error': 'ML meal recommender not available. Please ensure model is trained and loaded.'}), 500
        
        try:
            meals = meal_recommender_ml.recommend_meals(
                calorie_goal,
                dietary_preferences,
                num_meals=num_meals
            )
            if meals and len(meals) > 0:
                print(f"✓ ML meal recommender returned {len(meals)} meals from dataset")
                return jsonify(meals)
            else:
                print(f"⚠ ML meal recommender returned empty list")
                return jsonify({'error': 'No meals found matching your dietary preferences.'}), 404
        except Exception as e:
            print(f"✗ ML meal recommender error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'ML model error: {str(e)}'}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

@app.route('/api/workout-plan', methods=['POST'])
def get_workout_plan():
    """Get workout plan based on fitness goal and activity level using ML"""
    try:
        data = request.json
        goal = data.get('fitnessGoal', 'General Fitness')
        activity_level = data.get('activityLevel', 'Moderate')
        experience_level = data.get('experienceLevel', 'Moderate')
        
        # Determine days per week based on activity level
        activity_to_days = {
            'Sedentary': 3,
            'Light': 4,
            'Moderate': 5,
            'Active': 5,
            'Very Active': 6
        }
        days_per_week = activity_to_days.get(activity_level, 5)
        
        # Try ML workout generator first (preferred)
        if workout_generator_ml and workout_generator_ml.exercises_df is not None:
            try:
                plan = workout_generator_ml.generate_workout_plan(
                    goal,
                    activity_level,
                    experience_level,
                    days_per_week
                )
                if plan and len(plan) > 0:
                    return jsonify(plan)
            except Exception as e:
                print(f"⚠ ML workout generator error: {e}")
                import traceback
                traceback.print_exc()
        
        # Fallback to workout classifier
        if workout_classifier:
            plan = workout_classifier.generate_workout_plan(goal, activity_level, experience_level)
            if plan and len(plan) > 0:
                return jsonify(plan)
        
        # Last resort: Fallback plan (same as frontend)
        plans = {
            'Weight Loss': [
                {'day': 'Day 1', 'focus': 'Full Body Circuit', 'details': ['Squat 3x12', 'Push-ups 3x12', 'Rows 3x12', 'Plank 3x45s', '20 min Zone 2 cardio']},
                {'day': 'Day 2', 'focus': 'Cardio + Core', 'details': ['30-40 min Zone 2 cardio', 'Hanging knee raises 3x12', 'Side plank 3x30s/side']},
                {'day': 'Day 3', 'focus': 'Upper Body + Intervals', 'details': ['Incline DB Press 4x10', 'Lat Pulldown 4x10', 'Shoulder Press 3x12', 'Bike: 8x30s hard / 90s easy']},
                {'day': 'Day 4', 'focus': 'Lower Body + Steps', 'details': ['Deadlift 4x6', 'Lunges 3x12/leg', 'Leg Curl 3x12', '8-10k steps']},
            ],
            'Muscle Gain': [
                {'day': 'Day 1', 'focus': 'Upper Push', 'details': ['Bench Press 5x5', 'Incline DB Press 4x8', 'Overhead Press 4x8', 'Lateral Raises 4x12', 'Triceps 3x12']},
                {'day': 'Day 2', 'focus': 'Lower Strength', 'details': ['Back Squat 5x5', 'RDL 4x8', 'Leg Press 4x10', 'Calf Raise 4x15']},
                {'day': 'Day 3', 'focus': 'Upper Pull', 'details': ['Pull-ups 5xAMRAP', 'Barbell Row 4x8', 'Face Pull 4x12', 'Biceps 3x12']},
                {'day': 'Day 4', 'focus': 'Lower Hypertrophy', 'details': ['Front Squat 4x8', 'Hip Thrust 4x10', 'Leg Curl 4x12', 'Walking Lunges 3x12/leg']},
            ],
            'Endurance': [
                {'day': 'Day 1', 'focus': 'Zone 2 Base', 'details': ['Run/Cycle/Row 45-60 min Zone 2']},
                {'day': 'Day 2', 'focus': 'Strength Maintenance', 'details': ['Full Body 3x10: Squat, Press, Row, Lunge, Core']},
                {'day': 'Day 3', 'focus': 'Intervals', 'details': ['10x2 min hard / 2 min easy']},
                {'day': 'Day 4', 'focus': 'Long Session', 'details': ['75-90 min Zone 2']},
            ],
            'General Fitness': [
                {'day': 'Day 1', 'focus': 'Full Body A', 'details': ['Goblet Squat 4x10', 'Push-ups 4xAMRAP', 'Rows 4x10', 'Plank 3x45s']},
                {'day': 'Day 2', 'focus': 'Cardio 30-40', 'details': ['Zone 2 steady 30-40 min']},
                {'day': 'Day 3', 'focus': 'Full Body B', 'details': ['Deadlift 4x6', 'Overhead Press 4x8', 'Lat Pulldown 4x10', 'Side Plank 3x30s/side']},
                {'day': 'Day 4', 'focus': 'Intervals + Steps', 'details': ['6x1 min hard / 2 min easy', '8-10k steps']},
            ]
        }
        plan = plans.get(goal, plans['General Fitness'])
        return jsonify(plan)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

@app.route('/api/progress-forecast', methods=['POST'])
def get_progress_forecast():
    """Get 12-week progress forecast"""
    try:
        data = request.json
        weight = float(data.get('weight', 70))
        goal = data.get('fitnessGoal', 'General Fitness')
        activity_level = data.get('activityLevel', 'Moderate')
        weeks = int(data.get('weeks', 12))
        
        # Try to use ML model if available
        if progress_model and progress_model.model is not None:
            # Create initial data point for prediction
            # The model expects: days, weight_kg, calories_burned, daily_steps
            activity_to_calories = {
                'Sedentary': 150,
                'Light': 200,
                'Moderate': 300,
                'Active': 400,
                'Very Active': 500
            }
            activity_to_steps = {
                'Sedentary': 3000,
                'Light': 5000,
                'Moderate': 8000,
                'Active': 10000,
                'Very Active': 12000
            }
            
            calories_burned = activity_to_calories.get(activity_level, 300)
            daily_steps = activity_to_steps.get(activity_level, 8000)
            
            points = []
            current_weight = weight
            
            for week in range(weeks + 1):
                days = week * 7
                
                # Use ML model to predict next weight
                X = np.array([[days, current_weight, calories_burned, daily_steps]])
                predicted_weight = progress_model.model.predict(X)[0]
                
                # Ensure reasonable bounds
                predicted_weight = max(weight * 0.7, min(weight * 1.3, predicted_weight))
                
                points.append({
                    'week': week,
                    'weight': round(predicted_weight, 1)
                })
                
                # Update current weight for next iteration
                current_weight = predicted_weight
            
            # Calculate weekly delta from first and last point
            weekly_delta = round((points[-1]['weight'] - points[0]['weight']) / weeks, 2)
            
            return jsonify({
                'weeklyDelta': weekly_delta,
                'points': points
            })
        else:
            # Fallback: Simple projection logic
            base_deltas = {
                'Weight Loss': -0.75,
                'Muscle Gain': 0.35,
                'Endurance': -0.25,
                'General Fitness': -0.10,
            }
            base = base_deltas.get(goal, -0.10)
            
            activity_adjustments = {
                'Sedentary': 0.8,
                'Light': 0.9,
                'Moderate': 1.0,
                'Active': 1.1,
                'Very Active': 1.2,
            }
            adjustment = activity_adjustments.get(activity_level, 1.0)
            weekly_delta = base * adjustment
            
            points = []
            for week in range(weeks + 1):
                points.append({
                    'week': week,
                    'weight': round(weight + (weekly_delta * week), 1)
                })
            
            return jsonify({
                'weeklyDelta': round(weekly_delta, 2),
                'points': points
            })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print("=" * 60)
    print("BIOBOARD API SERVER")
    print("=" * 60)
    print("")
    load_models()
    print("")
    print("=" * 60)
    print("Starting server on http://localhost:5001")
    print("API endpoints:")
    print("  GET  /api/health")
    print("  POST /api/nutritional-targets")
    print("  POST /api/meal-recommendations")
    print("  POST /api/workout-plan")
    print("  POST /api/progress-forecast")
    print("=" * 60)
    print("")
    try:
        app.run(debug=True, port=5001, host='0.0.0.0')
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\n\nError starting server: {e}")
        import traceback
        traceback.print_exc()

