import pandas as pd
import numpy as np

class MealRecommender:
    def __init__(self):
        self.meals_db = None
        self.results = {}
        
    def create_meal_database(self, dietary_df):
        """Create meal database from dietary patterns"""
        meals = []
        
        cuisines = ['Mexican', 'Chinese', 'Italian', 'Indian']
        diet_types = ['Balanced', 'Low_Carb', 'Low_Sodium']
        
        meal_templates = {
            'Mexican': {
                'Balanced': [
                    {'name': 'Grilled Chicken Tacos', 'calories': 450, 'protein': 35, 'carbs': 40, 'fats': 15, 'restrictions': 'None'},
                    {'name': 'Black Bean Burrito Bowl', 'calories': 520, 'protein': 20, 'carbs': 65, 'fats': 18, 'restrictions': 'None'},
                    {'name': 'Shrimp Fajitas', 'calories': 380, 'protein': 32, 'carbs': 35, 'fats': 12, 'restrictions': 'None'},
                ],
                'Low_Carb': [
                    {'name': 'Cauliflower Rice Fajitas', 'calories': 380, 'protein': 32, 'carbs': 15, 'fats': 22, 'restrictions': 'None'},
                    {'name': 'Grilled Steak with Vegetables', 'calories': 420, 'protein': 40, 'carbs': 12, 'fats': 20, 'restrictions': 'None'},
                ],
                'Low_Sodium': [
                    {'name': 'Fresh Salsa Chicken', 'calories': 400, 'protein': 38, 'carbs': 30, 'fats': 14, 'restrictions': 'Low_Sodium'},
                ]
            },
            'Chinese': {
                'Balanced': [
                    {'name': 'Steamed Chicken and Vegetables', 'calories': 420, 'protein': 38, 'carbs': 35, 'fats': 12, 'restrictions': 'Low_Sodium'},
                    {'name': 'Beef and Broccoli', 'calories': 480, 'protein': 40, 'carbs': 42, 'fats': 16, 'restrictions': 'None'},
                    {'name': 'Sweet and Sour Chicken', 'calories': 550, 'protein': 35, 'carbs': 60, 'fats': 18, 'restrictions': 'None'},
                ],
                'Low_Carb': [
                    {'name': 'Stir-Fried Vegetables with Tofu', 'calories': 350, 'protein': 25, 'carbs': 20, 'fats': 18, 'restrictions': 'None'},
                ],
                'Low_Sodium': [
                    {'name': 'Steamed Fish with Vegetables', 'calories': 380, 'protein': 42, 'carbs': 25, 'fats': 12, 'restrictions': 'Low_Sodium'},
                ]
            },
            'Italian': {
                'Balanced': [
                    {'name': 'Grilled Salmon with Pasta', 'calories': 550, 'protein': 42, 'carbs': 55, 'fats': 18, 'restrictions': 'None'},
                    {'name': 'Chicken Parmesan', 'calories': 620, 'protein': 48, 'carbs': 45, 'fats': 25, 'restrictions': 'None'},
                    {'name': 'Margherita Pizza Slice', 'calories': 280, 'protein': 12, 'carbs': 35, 'fats': 10, 'restrictions': 'None'},
                ],
                'Low_Carb': [
                    {'name': 'Zucchini Noodles with Meatballs', 'calories': 450, 'protein': 38, 'carbs': 18, 'fats': 22, 'restrictions': 'None'},
                ],
                'Low_Sodium': [
                    {'name': 'Herb-Crusted Chicken', 'calories': 420, 'protein': 40, 'carbs': 30, 'fats': 16, 'restrictions': 'Low_Sodium'},
                ]
            },
            'Indian': {
                'Balanced': [
                    {'name': 'Chicken Tikka Masala', 'calories': 580, 'protein': 45, 'carbs': 50, 'fats': 22, 'restrictions': 'None'},
                    {'name': 'Lentil Dal with Rice', 'calories': 450, 'protein': 18, 'carbs': 70, 'fats': 10, 'restrictions': 'None'},
                    {'name': 'Vegetable Curry', 'calories': 380, 'protein': 15, 'carbs': 55, 'fats': 12, 'restrictions': 'None'},
                ],
                'Low_Carb': [
                    {'name': 'Tandoori Chicken with Cauliflower', 'calories': 420, 'protein': 42, 'carbs': 15, 'fats': 20, 'restrictions': 'None'},
                ],
                'Low_Sodium': [
                    {'name': 'Grilled Fish Curry', 'calories': 400, 'protein': 38, 'carbs': 30, 'fats': 16, 'restrictions': 'Low_Sodium'},
                ]
            }
        }
        
        for cuisine in cuisines:
            for diet in diet_types:
                if cuisine in meal_templates and diet in meal_templates[cuisine]:
                    for meal in meal_templates[cuisine][diet]:
                        meal['cuisine'] = cuisine
                        meal['diet'] = diet
                        meals.append(meal)
        
        self.meals_db = pd.DataFrame(meals)
        
        self.results = {
            'total_meals': len(self.meals_db),
            'cuisines': self.meals_db['cuisine'].unique().tolist(),
            'diet_types': self.meals_db['diet'].unique().tolist()
        }
        
        print(f"✓ Meal Database Created: {len(self.meals_db)} meals")
        print(f"  - Cuisines: {self.results['cuisines']}")
        print(f"  - Diet Types: {self.results['diet_types']}")
        
        return self.meals_db
    
    def recommend_meals(self, calorie_goal, dietary_preferences, cuisine_preference=None, num_meals=3):
        """Recommend meals based on user preferences"""
        if self.meals_db is None or len(self.meals_db) == 0:
            return []
        
        filtered = self.meals_db.copy()
        
        if cuisine_preference:
            filtered = filtered[filtered['cuisine'] == cuisine_preference]
        
        if dietary_preferences:
            if 'Low_Sugar' in dietary_preferences or 'Low_Carb' in dietary_preferences:
                filtered = filtered[filtered['diet'].isin(['Low_Carb', 'Balanced'])]
            if 'Low_Sodium' in dietary_preferences:
                filtered = filtered[filtered['restrictions'] == 'Low_Sodium']
        
        if len(filtered) == 0:
            filtered = self.meals_db.copy()
        
        target_calories_per_meal = calorie_goal / num_meals
        filtered['calorie_diff'] = abs(filtered['calories'] - target_calories_per_meal)
        filtered = filtered.sort_values('calorie_diff')
        
        selected = filtered.head(num_meals).to_dict('records')
        
        return selected
