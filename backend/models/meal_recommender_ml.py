import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

class MealRecommenderML:
    """ML-based meal recommender using content-based filtering and dataset patterns"""
    
    def __init__(self):
        self.dietary_df = None
        self.scaler = StandardScaler()
        self.knn_model = None
        self.meal_features = None
        self.results = {}
        
    def train(self, dietary_df=None, meals_df=None):
        """Train meal recommender on meal dataset (preferred) or dietary patterns"""
        
        # PRIORITY: Use actual meal dataset if provided
        if meals_df is not None and len(meals_df) > 0:
            print("✓ Using USDA FoodData Central meal dataset")
            self.meals_df = meals_df.copy()
            
            # Ensure required columns exist
            required_cols = ['name', 'calories', 'protein', 'carbs', 'fats']
            if not all(col in self.meals_df.columns for col in required_cols):
                print("⚠ Meal dataset missing required columns, trying to infer...")
                return False
            
            # Ensure numeric columns are properly formatted
            for col in ['calories', 'protein', 'carbs', 'fats']:
                self.meals_df[col] = pd.to_numeric(self.meals_df[col], errors='coerce').fillna(0)
            
            # Filter out invalid meals
            self.meals_df = self.meals_df[
                (self.meals_df['calories'] > 0) & 
                (self.meals_df['calories'] < 5000) &
                (self.meals_df['protein'] >= 0) &
                (self.meals_df['carbs'] >= 0) &
                (self.meals_df['fats'] >= 0)
            ].copy()
            
            print(f"  Loaded {len(self.meals_df)} real meals from USDA dataset")
            
        # FALLBACK: Use dietary patterns to create synthetic meals
        elif dietary_df is not None and len(dietary_df) > 0:
            print("⚠ No meal dataset found, creating synthetic meals from dietary patterns")
            self.dietary_df = dietary_df.copy()
            meals = []
            
            # Group by cuisine and diet recommendation to create meal profiles
            for cuisine in self.dietary_df['Preferred_Cuisine'].dropna().unique():
                for diet in self.dietary_df['Diet_Recommendation'].dropna().unique():
                    subset = self.dietary_df[
                        (self.dietary_df['Preferred_Cuisine'] == cuisine) & 
                        (self.dietary_df['Diet_Recommendation'] == diet)
                    ]
                    
                    if len(subset) > 0:
                        avg_calories = subset['Daily_Caloric_Intake'].mean()
                        if diet == 'Low_Carb':
                            protein_ratio, carb_ratio, fat_ratio = 0.35, 0.20, 0.45
                        elif diet == 'Low_Sodium':
                            protein_ratio, carb_ratio, fat_ratio = 0.30, 0.50, 0.20
                        else:  # Balanced
                            protein_ratio, carb_ratio, fat_ratio = 0.25, 0.50, 0.25
                        
                        for i, (_, row) in enumerate(subset.head(3).iterrows()):
                            meal_calories = avg_calories / 3
                            meals.append({
                                'name': f"{cuisine} {diet} Meal {i+1}",
                                'cuisine': cuisine,
                                'diet': diet,
                                'calories': int(meal_calories),
                                'protein': int(meal_calories * protein_ratio / 4),
                                'carbs': int(meal_calories * carb_ratio / 4),
                                'fats': int(meal_calories * fat_ratio / 9),
                            })
            
            self.meals_df = pd.DataFrame(meals)
        
        else:
            print("⚠ No meal or dietary data available for training")
            return False
        
        if len(self.meals_df) == 0:
            print("⚠ No meals available after processing")
            return False
        
        # Create feature matrix for content-based filtering
        feature_cols = ['calories', 'protein', 'carbs', 'fats']
        self.meal_features = self.meals_df[feature_cols].values
        self.meal_features_scaled = self.scaler.fit_transform(self.meal_features)
        
        # Train KNN model for recommendations
        self.knn_model = NearestNeighbors(n_neighbors=min(10, len(self.meals_df)), metric='cosine')
        self.knn_model.fit(self.meal_features_scaled)
        
        # Get cuisines and diet types
        cuisines = self.meals_df['cuisine'].unique().tolist() if 'cuisine' in self.meals_df.columns else []
        diet_types = self.meals_df['diet'].unique().tolist() if 'diet' in self.meals_df.columns else []
        
        self.results = {
            'total_meals': len(self.meals_df),
            'cuisines': cuisines,
            'diet_types': diet_types,
            'training_samples': len(self.meals_df)
        }
        
        print(f"✓ ML Meal Recommender Trained:")
        print(f"  - Meals: {len(self.meals_df)}")
        print(f"  - Cuisines: {self.results['cuisines']}")
        print(f"  - Diet Types: {self.results['diet_types']}")
        
        return True
    
    def _get_bmi_range(self, bmi):
        """Categorize BMI into range"""
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 25:
            return 'Normal'
        elif bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'
    
    def recommend_meals(self, calorie_goal, dietary_preferences, num_meals=3):
        """Recommend meals using ML (content-based filtering + KNN)"""
        if self.meals_df is None or len(self.meals_df) == 0:
            return []
        
        # Filter by dietary preferences
        filtered = self.meals_df.copy()
        
        # Map frontend dietary preferences to backend format
        if dietary_preferences:
            # Handle string or list of preferences
            if isinstance(dietary_preferences, str):
                pref_list = [dietary_preferences]
            else:
                pref_list = dietary_preferences if isinstance(dietary_preferences, list) else [dietary_preferences]
            
            # Filter by dietary preferences
            diet_filters = []
            restriction_filters = []
            
            for pref in pref_list:
                if 'Vegan' in pref:
                    # Filter to ONLY vegan foods (no meat, dairy, eggs)
                    if 'is_vegan' in filtered.columns:
                        filtered = filtered[filtered['is_vegan'] == True]
                    # Also filter by name as backup
                    filtered = filtered[~filtered['name'].str.lower().str.contains('|'.join([
                        'cheese', 'milk', 'butter', 'cream', 'yogurt', 'dairy',
                        'beef', 'chicken', 'pork', 'turkey', 'lamb', 'meat', 'bacon', 'sausage', 'ham', 'steak',
                        'fish', 'seafood', 'salmon', 'tuna', 'shrimp', 'poultry', 'egg', 'yolk'
                    ]), case=False, na=False)]
                elif 'Vegetarian' in pref:
                    # Filter to vegetarian (no meat, but can have dairy/eggs)
                    if 'is_vegetarian' in filtered.columns:
                        filtered = filtered[filtered['is_vegetarian'] == True]
                    # Also filter by name as backup (only meat, not dairy)
                    filtered = filtered[~filtered['name'].str.lower().str.contains('|'.join([
                        'beef', 'chicken', 'pork', 'turkey', 'lamb', 'meat', 'bacon', 'sausage', 'ham', 'steak',
                        'fish', 'seafood', 'salmon', 'tuna', 'shrimp', 'poultry'
                    ]), case=False, na=False)]
                    diet_filters.append('Balanced')
                elif 'Keto' in pref or 'Low_Carb' in pref:
                    diet_filters.extend(['Low_Carb', 'Balanced'])
                elif 'Low_Sodium' in pref:
                    restriction_filters.append('Low_Sodium')
                elif 'Paleo' in pref:
                    diet_filters.append('Balanced')  # Approximate
                elif 'Mediterranean' in pref:
                    diet_filters.append('Balanced')  # Approximate
                elif 'Omnivore' in pref or pref == 'Omnivore':
                    # Omnivore can eat anything but PREFER meat options
                    # Don't filter out any meals, but we'll prioritize non-vegetarian meals later
                    # Keep all meals available for selection
                    pass  # Don't add any filters - use all meals
            
            # Apply filters only if we have filters to apply
            if diet_filters:
                filtered = filtered[filtered['diet'].isin(diet_filters)]
            if restriction_filters:
                filtered = filtered[filtered['restrictions'].isin(restriction_filters)]
        
        # If no meals match filters (or no filters applied), use all meals
        if len(filtered) == 0:
            filtered = self.meals_df.copy()
        
        # Create target nutritional profile
        target_calories_per_meal = calorie_goal / num_meals
        # Estimate target macros (balanced distribution)
        target_protein = int(target_calories_per_meal * 0.25 / 4)
        target_carbs = int(target_calories_per_meal * 0.50 / 4)
        target_fats = int(target_calories_per_meal * 0.25 / 9)
        
        target_features = np.array([[target_calories_per_meal, target_protein, target_carbs, target_fats]])
        
        # Ensure scaler is initialized and working
        feature_cols = ['calories', 'protein', 'carbs', 'fats']
        
        # Reinitialize scaler if needed (e.g., after loading from file)
        if self.scaler is None or not hasattr(self.scaler, 'mean_') or self.meal_features is None:
            # Reinitialize scaler
            self.meal_features = self.meals_df[feature_cols].values
            self.scaler = StandardScaler()
            self.meal_features_scaled = self.scaler.fit_transform(self.meal_features)
        
        try:
            target_features_scaled = self.scaler.transform(target_features)
        except (ValueError, AttributeError) as e:
            # If scaler transform fails, reinitialize
            self.meal_features = self.meals_df[feature_cols].values
            self.scaler = StandardScaler()
            self.scaler.fit(self.meal_features)
            self.meal_features_scaled = self.scaler.transform(self.meal_features)
            target_features_scaled = self.scaler.transform(target_features)
        
        # Get features for filtered meals
        filtered_features_raw = filtered[feature_cols].values
        filtered_features_scaled = self.scaler.transform(filtered_features_raw)
        
        # Find most similar meals using cosine similarity
        similarities = cosine_similarity(target_features_scaled, filtered_features_scaled)[0]
        
        # For Omnivore: Boost similarity scores for meat options (prioritize non-vegetarian meals)
        if dietary_preferences and ('Omnivore' in dietary_preferences or dietary_preferences == 'Omnivore'):
            # Boost similarity for non-vegetarian meals by 20%
            meat_boost = 1.2
            for idx in range(len(similarities)):
                if not filtered.iloc[idx].get('is_vegetarian', True):  # If not vegetarian (has meat)
                    similarities[idx] = min(1.0, similarities[idx] * meat_boost)  # Cap at 1.0
        
        # Get top N meals with diversity (ensure different meal types AND cuisines)
        # Sort by similarity but ensure we get diverse meals
        top_indices = []
        selected_cuisines = set()
        selected_meal_types = set()
        similarity_sorted_indices = np.argsort(similarities)[::-1]
        
        # If dataset has meal_type column (from PP_recipes), prioritize meal type diversity
        has_meal_type = 'meal_type' in filtered.columns
        
        # For Omnivore: Track meat vs non-meat selection to ensure more meat
        is_omnivore = dietary_preferences and ('Omnivore' in dietary_preferences or dietary_preferences == 'Omnivore')
        meat_selected = 0
        veg_selected = 0
        target_meat_ratio = 0.65  # Aim for 65% meat, 35% vegetarian/vegan for omnivore
        
        for idx in similarity_sorted_indices:
            if len(top_indices) >= num_meals:
                break
            meal_cuisine = filtered.iloc[idx]['cuisine']
            meal_name = filtered.iloc[idx]['name']
            meal_type = filtered.iloc[idx].get('meal_type', None) if has_meal_type else None
            is_meat = not filtered.iloc[idx].get('is_vegetarian', True)
            
            # For Omnivore: Prioritize meat if we don't have enough yet
            if is_omnivore and len(top_indices) > 0:
                target_meat_count = int(num_meals * target_meat_ratio)
                needs_more_meat = meat_selected < target_meat_count
                
                # If we need more meat and this is meat, prioritize it (unless already have this meal type)
                if needs_more_meat and is_meat:
                    # Check if we should prioritize by meal type diversity first
                    if has_meal_type and meal_type and meal_type not in selected_meal_types:
                        # Different meal type is good
                        top_indices.append(idx)
                        meat_selected += 1
                        selected_cuisines.add(meal_cuisine)
                        selected_meal_types.add(meal_type)
                        continue
                    elif meal_cuisine not in selected_cuisines or len(top_indices) < target_meat_count:
                        # Different cuisine or still need more meat
                        top_indices.append(idx)
                        meat_selected += 1
                        selected_cuisines.add(meal_cuisine)
                        if meal_type:
                            selected_meal_types.add(meal_type)
                        continue
                    elif meat_selected < target_meat_count - 1:
                        # If we still need more meat, prefer this even if meal type/cuisine is duplicate
                        top_indices.append(idx)
                        meat_selected += 1
                        if meal_type:
                            selected_meal_types.add(meal_type)
                        continue
                
                # If we have enough meat and this is veg, that's fine if diversity is good
                if not needs_more_meat and not is_meat:
                    # Check diversity first
                    if has_meal_type and meal_type and meal_type not in selected_meal_types:
                        top_indices.append(idx)
                        veg_selected += 1
                        selected_meal_types.add(meal_type)
                        selected_cuisines.add(meal_cuisine)
                        continue
                    elif meal_cuisine not in selected_cuisines:
                        top_indices.append(idx)
                        veg_selected += 1
                        selected_cuisines.add(meal_cuisine)
                        if meal_type:
                            selected_meal_types.add(meal_type)
                        continue
            
            # Prioritize diversity - prefer different meal types first, then different cuisines
            if len(top_indices) == 0:
                # Always take first (best match)
                top_indices.append(idx)
                selected_cuisines.add(meal_cuisine)
                if meal_type:
                    selected_meal_types.add(meal_type)
                if is_omnivore:
                    if is_meat:
                        meat_selected += 1
                    else:
                        veg_selected += 1
            elif has_meal_type and meal_type and meal_type not in selected_meal_types:
                # Prioritize different meal type (Breakfast, Lunch, Dinner)
                top_indices.append(idx)
                selected_meal_types.add(meal_type)
                selected_cuisines.add(meal_cuisine)
                if is_omnivore:
                    if is_meat:
                        meat_selected += 1
                    else:
                        veg_selected += 1
            elif meal_cuisine not in selected_cuisines:
                # Prefer different cuisine for diversity
                top_indices.append(idx)
                selected_cuisines.add(meal_cuisine)
                if meal_type:
                    selected_meal_types.add(meal_type)
                if is_omnivore:
                    if is_meat:
                        meat_selected += 1
                    else:
                        veg_selected += 1
            elif len(top_indices) < num_meals and similarities[idx] > 0.5:
                # If we need more meals and similarity is good, take it
                # For omnivore, prefer meat if we don't have enough
                if is_omnivore and meat_selected < target_meat_count and is_meat:
                    top_indices.append(idx)
                    meat_selected += 1
                    if meal_type:
                        selected_meal_types.add(meal_type)
                elif not is_omnivore or veg_selected < num_meals - target_meat_count or not is_meat:
                    top_indices.append(idx)
                    if meal_type:
                        selected_meal_types.add(meal_type)
                    if is_omnivore:
                        if is_meat:
                            meat_selected += 1
                        else:
                            veg_selected += 1
        
        # If we still don't have enough and have meal types, try to fill with different meal types
        if has_meal_type and len(top_indices) < num_meals:
            target_meal_types = ['Breakfast', 'Lunch', 'Dinner']
            for target_type in target_meal_types:
                if len(top_indices) >= num_meals:
                    break
                if target_type not in selected_meal_types:
                    # Find best meal of this type
                    for idx in similarity_sorted_indices:
                        if idx not in top_indices and filtered.iloc[idx].get('meal_type') == target_type:
                            top_indices.append(idx)
                            selected_meal_types.add(target_type)
                            break
        
        # If we still don't have enough, fill with remaining top similar meals
        while len(top_indices) < num_meals and len(top_indices) < len(similarity_sorted_indices):
            for idx in similarity_sorted_indices:
                if idx not in top_indices:
                    top_indices.append(idx)
                    break
        
        # FORCE meal type diversity if we have meal_type column and need 3 meals
        if has_meal_type and num_meals == 3 and len(top_indices) >= 3:
            # Check if we have all 3 meal types
            current_meal_types = set()
            for idx in top_indices[:3]:
                mt = filtered.iloc[idx].get('meal_type')
                if mt:
                    current_meal_types.add(mt)
            
            # If we don't have all 3 types, force it
            if len(current_meal_types) < 3:
                target_types = ['Breakfast', 'Lunch', 'Dinner']
                new_indices = []
                used_indices = set()
                
                # For each target type, find the best matching meal
                for target_type in target_types:
                    best_idx = None
                    best_sim = -1
                    
                    # Find best match for this meal type
                    for idx in similarity_sorted_indices:
                        if idx in used_indices:
                            continue
                        mt = filtered.iloc[idx].get('meal_type')
                        if mt == target_type:
                            if similarities[idx] > best_sim:
                                best_sim = similarities[idx]
                                best_idx = idx
                    
                    if best_idx is not None:
                        new_indices.append(best_idx)
                        used_indices.add(best_idx)
                    else:
                        # Fallback to any available
                        for idx in similarity_sorted_indices:
                            if idx not in used_indices:
                                new_indices.append(idx)
                                used_indices.add(idx)
                                break
                
                if len(new_indices) == 3:
                    top_indices = new_indices
        
        selected_meals = filtered.iloc[top_indices[:num_meals]].copy().reset_index(drop=True)
        
        # Scale meals to match calorie goal - distribute across meals properly
        # For 3 meals: Breakfast 25%, Lunch 40%, Dinner 35%
        # For 4 meals: Breakfast 20%, Mid-morning 20%, Lunch 35%, Dinner 25%
        # For 5 meals: Breakfast 20%, Mid-morning 15%, Lunch 30%, Afternoon 15%, Dinner 20%
        # For 6 meals: Breakfast 18%, Mid-morning 15%, Lunch 25%, Afternoon 12%, Dinner 20%, Evening 10%
        # For other numbers: distribute evenly
        num_selected = len(selected_meals)
        if num_selected == 3:
            meal_distribution = [0.25, 0.40, 0.35]
        elif num_selected == 4:
            meal_distribution = [0.20, 0.20, 0.35, 0.25]
        elif num_selected == 5:
            meal_distribution = [0.20, 0.15, 0.30, 0.15, 0.20]
        elif num_selected == 6:
            meal_distribution = [0.18, 0.15, 0.25, 0.12, 0.20, 0.10]
        else:
            meal_distribution = [1.0/num_selected] * num_selected
        
        for idx in range(len(selected_meals)):
            # Scale each meal to its target distribution
            target_calories = int(calorie_goal * meal_distribution[idx] if idx < len(meal_distribution) else calorie_goal / len(selected_meals))
            original_calories = selected_meals.iloc[idx]['calories']
            if original_calories > 0:
                scale_factor = target_calories / original_calories
                selected_meals.iloc[idx, selected_meals.columns.get_loc('calories')] = int(target_calories)
                selected_meals.iloc[idx, selected_meals.columns.get_loc('protein')] = int(selected_meals.iloc[idx]['protein'] * scale_factor)
                selected_meals.iloc[idx, selected_meals.columns.get_loc('carbs')] = int(selected_meals.iloc[idx]['carbs'] * scale_factor)
                selected_meals.iloc[idx, selected_meals.columns.get_loc('fats')] = int(selected_meals.iloc[idx]['fats'] * scale_factor)
        
        # Format for frontend - assign meal types based on number of meals
        # Standard meal types for different numbers
        meal_types_map = {
            3: ['Breakfast', 'Lunch', 'Dinner'],
            4: ['Breakfast', 'Mid-morning Snack', 'Lunch', 'Dinner'],
            5: ['Breakfast', 'Mid-morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner'],
            6: ['Breakfast', 'Mid-morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner', 'Evening Snack']
        }
        
        # Default meal types order
        meal_types_order = meal_types_map.get(num_selected, ['Breakfast', 'Lunch', 'Dinner', 'Snack', 'Meal'])
        
        formatted_meals = []
        for i, (_, meal) in enumerate(selected_meals.iterrows()):
            # Use predefined meal types if available, otherwise use meal_type from data or default
            if i < len(meal_types_order):
                meal_type = meal_types_order[i]
            elif 'meal_type' in meal and pd.notna(meal['meal_type']):
                meal_type = meal['meal_type']
            else:
                # Generate default type based on position
                if num_selected <= 6 and i < len(meal_types_order):
                    meal_type = meal_types_order[i]
                else:
                    meal_type = f'Meal {i+1}'
            
            formatted_meals.append({
                'name': meal['name'],
                'type': meal_type,
                'protein': int(meal['protein']),
                'carbs': int(meal['carbs']),
                'fats': int(meal['fats']),
                'calories': int(meal['calories'])
            })
        
        return formatted_meals
    
    def save(self, path='models/meal_recommender_ml.joblib'):
        import joblib
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'meals_df': self.meals_df,
            'scaler': self.scaler,
            'meal_features': self.meal_features,
            'meal_features_scaled': self.meal_features_scaled,
            'knn_model': self.knn_model,
            'results': self.results
        }, path)
        print(f"✓ ML Meal Recommender saved to {path}")
    
    def load(self, path='models/meal_recommender_ml.joblib'):
        import joblib
        data = joblib.load(path)
        self.meals_df = data['meals_df']
        self.scaler = data['scaler']
        self.meal_features = data['meal_features']
        self.meal_features_scaled = data['meal_features_scaled']
        self.knn_model = data['knn_model']
        self.results = data['results']
        print(f"✓ ML Meal Recommender loaded from {path}")

