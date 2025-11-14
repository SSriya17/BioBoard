import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import random

class WorkoutGeneratorML:
    """ML-based workout generator using exercise dataset"""
    
    def __init__(self):
        self.exercises_df = None
        self.scaler = StandardScaler()
        self.muscle_groups = None
        self.results = {}
        
    def train(self, exercises_df):
        """Train workout generator on exercise dataset"""
        if exercises_df is None or len(exercises_df) == 0:
            print("⚠ No exercise data available for training")
            return False
        
        self.exercises_df = exercises_df.copy()
        
        # Clean and prepare exercise data
        self.exercises_df['Main_muscle'] = self.exercises_df['Main_muscle'].fillna('Unknown')
        self.exercises_df['Equipment'] = self.exercises_df['Equipment'].fillna('Bodyweight')
        self.exercises_df['Difficulty (1-5)'] = pd.to_numeric(self.exercises_df['Difficulty (1-5)'], errors='coerce').fillna(3)
        self.exercises_df['Utility'] = self.exercises_df['Utility'].fillna('Auxiliary')
        
        # Extract unique muscle groups
        self.muscle_groups = self.exercises_df['Main_muscle'].unique().tolist()
        
        # Categorize exercises by muscle group and utility
        self.exercises_by_muscle = {}
        for muscle in self.muscle_groups:
            self.exercises_by_muscle[muscle] = self.exercises_df[
                self.exercises_df['Main_muscle'] == muscle
            ].to_dict('records')
        
        self.results = {
            'total_exercises': len(self.exercises_df),
            'muscle_groups': len(self.muscle_groups),
            'muscle_group_list': self.muscle_groups[:10]  # Top 10
        }
        
        print(f"✓ ML Workout Generator Trained:")
        print(f"  - Exercises: {len(self.exercises_df)}")
        print(f"  - Muscle Groups: {len(self.muscle_groups)}")
        
        return True
    
    def generate_workout_plan(self, goal, activity_level, experience_level='Moderate', days_per_week=5):
        """Generate workout plan using ML-based exercise selection"""
        if self.exercises_df is None or len(self.exercises_df) == 0:
            return []
        
        # Map goal to muscle groups and workout structure
        goal_config = self._get_goal_config(goal)
        experience_config = self._get_experience_config(experience_level)
        
        workout_plan = []
        
        # Generate workout days based on goal
        if goal == 'Muscle Gain':
            # Push/Pull/Legs split
            split_days = [
                {'focus': 'Upper Push', 'muscles': ['Chest', 'Shoulders', 'Triceps'], 'exercises_per_muscle': 2},
                {'focus': 'Lower Strength', 'muscles': ['Quadriceps', 'Hamstrings', 'Glutes'], 'exercises_per_muscle': 2},
                {'focus': 'Upper Pull', 'muscles': ['Back', 'Biceps', 'Lats'], 'exercises_per_muscle': 2},
                {'focus': 'Lower Hypertrophy', 'muscles': ['Quadriceps', 'Hamstrings', 'Calves'], 'exercises_per_muscle': 2},
                {'focus': 'Arms/Delts', 'muscles': ['Biceps', 'Triceps', 'Shoulders'], 'exercises_per_muscle': 1}
            ]
        elif goal == 'Weight Loss':
            # Full body circuit
            split_days = [
                {'focus': 'Full Body Circuit', 'muscles': ['Chest', 'Back', 'Quadriceps', 'Core'], 'exercises_per_muscle': 1},
                {'focus': 'Cardio + Core', 'muscles': ['Core', 'Cardio'], 'exercises_per_muscle': 2},
                {'focus': 'Upper Body + Intervals', 'muscles': ['Chest', 'Back', 'Shoulders'], 'exercises_per_muscle': 1},
                {'focus': 'Lower Body + Steps', 'muscles': ['Quadriceps', 'Hamstrings', 'Glutes'], 'exercises_per_muscle': 1},
                {'focus': 'Active Recovery', 'muscles': ['Core', 'Full Body'], 'exercises_per_muscle': 1}
            ]
        elif goal == 'Endurance':
            # Cardio-focused
            split_days = [
                {'focus': 'Zone 2 Base', 'muscles': ['Cardio'], 'exercises_per_muscle': 1},
                {'focus': 'Strength Maintenance', 'muscles': ['Full Body'], 'exercises_per_muscle': 2},
                {'focus': 'Intervals', 'muscles': ['Cardio'], 'exercises_per_muscle': 1},
                {'focus': 'Long Session', 'muscles': ['Cardio'], 'exercises_per_muscle': 1},
                {'focus': 'Mobility + Easy', 'muscles': ['Core', 'Full Body'], 'exercises_per_muscle': 1}
            ]
        else:  # General Fitness
            split_days = [
                {'focus': 'Full Body A', 'muscles': ['Chest', 'Back', 'Quadriceps', 'Core'], 'exercises_per_muscle': 1},
                {'focus': 'Cardio 30-40', 'muscles': ['Cardio'], 'exercises_per_muscle': 1},
                {'focus': 'Full Body B', 'muscles': ['Back', 'Shoulders', 'Hamstrings', 'Core'], 'exercises_per_muscle': 1},
                {'focus': 'Intervals + Steps', 'muscles': ['Cardio', 'Core'], 'exercises_per_muscle': 1},
                {'focus': 'Mobility + Core', 'muscles': ['Core', 'Full Body'], 'exercises_per_muscle': 1}
            ]
        
        # Generate exercises for each day
        for day_idx, day_config in enumerate(split_days[:days_per_week]):
            exercises = []
            
            for muscle in day_config['muscles']:
                if muscle == 'Cardio':
                    # Add cardio exercise
                    exercises.append({
                        'name': 'Zone 2 Cardio',
                        'sets': '30-45 min',
                        'reps': 'Steady pace',
                        'rest': 'N/A'
                    })
                elif muscle == 'Core':
                    # Get core exercises
                    core_exercises = self._get_exercises_by_muscle(['Abdominals', 'Core', 'Obliques'], 
                                                                   day_config['exercises_per_muscle'])
                    exercises.extend(core_exercises)
                elif muscle == 'Full Body':
                    # Get full body exercises
                    full_body_exercises = self._get_exercises_by_muscle(['Full Body', 'Compound'], 
                                                                        day_config['exercises_per_muscle'])
                    exercises.extend(full_body_exercises)
                else:
                    # Get exercises for specific muscle group
                    muscle_exercises = self._get_exercises_by_muscle([muscle], 
                                                                     day_config['exercises_per_muscle'])
                    exercises.extend(muscle_exercises)
            
            # Format exercises
            exercise_details = []
            for ex in exercises[:8]:  # Limit to 8 exercises per day
                if isinstance(ex, dict):
                    if 'name' in ex:
                        # Already formatted exercise
                        exercise_details.append(f"{ex['name']} {ex.get('sets', '3x10')}")
                    elif 'Exercise Name' in ex:
                        # Exercise from dataset
                        ex_name = ex.get('Exercise Name', 'Exercise')
                        sets_reps = self._get_sets_reps(goal, experience_level, ex.get('Difficulty (1-5)', 3))
                        exercise_details.append(f"{ex_name} {sets_reps}")
                    else:
                        # Generic dict, try to get name
                        ex_name = ex.get('name', ex.get('exercise', 'Exercise'))
                        sets_reps = self._get_sets_reps(goal, experience_level, ex.get('difficulty', 3))
                        exercise_details.append(f"{ex_name} {sets_reps}")
                elif isinstance(ex, str):
                    exercise_details.append(ex)
                else:
                    # Fallback
                    exercise_details.append('Exercise')
            
            workout_plan.append({
                'day': f'Day {day_idx + 1}',
                'focus': day_config['focus'],
                'details': exercise_details if exercise_details else ['No exercises found']
            })
        
        return workout_plan
    
    def _get_exercises_by_muscle(self, muscle_groups, num_exercises):
        """Get exercises for specific muscle groups"""
        exercises = []
        
        for muscle in muscle_groups:
            # Find exercises that match muscle group (fuzzy match)
            matching_exercises = self.exercises_df[
                self.exercises_df['Main_muscle'].str.contains(muscle, case=False, na=False) |
                self.exercises_df['Target_Muscles'].str.contains(muscle, case=False, na=False)
            ]
            
            if len(matching_exercises) > 0:
                # Select random exercises
                selected = matching_exercises.sample(min(num_exercises, len(matching_exercises)))
                exercises.extend(selected.to_dict('records'))
        
        # If no matches, get any exercises
        if len(exercises) == 0:
            exercises = self.exercises_df.sample(min(num_exercises * len(muscle_groups), len(self.exercises_df))).to_dict('records')
        
        return exercises
    
    def _get_sets_reps(self, goal, experience_level, difficulty):
        """Get sets and reps based on goal and experience"""
        if goal == 'Muscle Gain':
            if experience_level == 'Beginner':
                return '3x8-10'
            elif experience_level == 'Advanced':
                return '4x6-8'
            else:
                return '3x10-12'
        elif goal == 'Weight Loss':
            return '3x12-15'
        else:  # General Fitness or Endurance
            return '3x10'
    
    def _get_goal_config(self, goal):
        """Get configuration for fitness goal"""
        configs = {
            'Muscle Gain': {'volume': 'high', 'intensity': 'high', 'rest': 'long'},
            'Weight Loss': {'volume': 'high', 'intensity': 'moderate', 'rest': 'short'},
            'Endurance': {'volume': 'moderate', 'intensity': 'moderate', 'rest': 'short'},
            'General Fitness': {'volume': 'moderate', 'intensity': 'moderate', 'rest': 'moderate'}
        }
        return configs.get(goal, configs['General Fitness'])
    
    def _get_experience_config(self, experience_level):
        """Get configuration for experience level"""
        configs = {
            'Beginner': {'difficulty': 1, 'complexity': 'low'},
            'Moderate': {'difficulty': 3, 'complexity': 'moderate'},
            'Advanced': {'difficulty': 5, 'complexity': 'high'}
        }
        return configs.get(experience_level, configs['Moderate'])
    
    def save(self, path='models/workout_generator_ml.joblib'):
        import joblib
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'exercises_df': self.exercises_df,
            'exercises_by_muscle': self.exercises_by_muscle,
            'muscle_groups': self.muscle_groups,
            'results': self.results
        }, path)
        print(f"✓ ML Workout Generator saved to {path}")
    
    def load(self, path='models/workout_generator_ml.joblib'):
        import joblib
        data = joblib.load(path)
        self.exercises_df = data['exercises_df']
        self.exercises_by_muscle = data['exercises_by_muscle']
        self.muscle_groups = data['muscle_groups']
        self.results = data['results']
        print(f"✓ ML Workout Generator loaded from {path}")

