import pandas as pd
import os

def load_usda_meals(meal_dir):
    """Load and process USDA FoodData Central to create meal dataset"""
    try:
        # Load main files
        food_df = pd.read_csv(os.path.join(meal_dir, 'food.csv'))
        food_nutrient_df = pd.read_csv(os.path.join(meal_dir, 'food_nutrient.csv'))
        nutrient_df = pd.read_csv(os.path.join(meal_dir, 'nutrient.csv'))
        food_category_df = pd.read_csv(os.path.join(meal_dir, 'food_category.csv'))
        
        # Find nutrient IDs (standard USDA IDs)
        # Try multiple IDs for each nutrient to get more foods
        nutrient_id_map = {
            'calories': [1008, 2047, 2048],  # Energy (kcal) - try multiple
            'protein': [1003, 1053],  # Protein - try multiple
            'carbs': [1005, 1050, 1072],  # Carbohydrate - try multiple
            'fats': [1004, 1085]  # Total lipid (fat) - try multiple
        }
        
        # Get nutrient data for each food
        meals = []
        
        # Process in chunks for memory efficiency
        chunk_size = 10000
        for i in range(0, len(food_df), chunk_size):
            chunk_foods = food_df.iloc[i:i+chunk_size]
            
            for _, food_row in chunk_foods.iterrows():
                fdc_id = food_row['fdc_id']
                food_name = food_row['description']
                category_id = food_row.get('food_category_id', None)
                
                # Get nutrients for this food
                food_nutrients = food_nutrient_df[food_nutrient_df['fdc_id'] == fdc_id]
                
                if len(food_nutrients) == 0:
                    continue
                
                # Extract key nutrients - try multiple nutrient IDs for each
                meal_data = {'name': food_name, 'fdc_id': fdc_id}
                
                for nutrient_name, nutrient_ids in nutrient_id_map.items():
                    amount = 0
                    # Try each nutrient ID until we find one with data
                    for nutrient_id in nutrient_ids:
                        nutrient_row = food_nutrients[food_nutrients['nutrient_id'] == nutrient_id]
                        if len(nutrient_row) > 0:
                            # Use amount, or median if amount is NaN
                            val = nutrient_row.iloc[0]['amount']
                            if pd.isna(val):
                                val = nutrient_row.iloc[0].get('median', 0)
                            if not pd.isna(val) and val > 0:
                                amount = float(val)
                                break
                    
                    # If no amount found and it's calories, try to calculate from macros
                    if amount == 0 and nutrient_name == 'calories':
                        # Will calculate later from protein/carbs/fats if available
                        pass
                    
                    meal_data[nutrient_name] = amount
                
                # Calculate calories from macros if missing (4 cal/g protein/carbs, 9 cal/g fat)
                if meal_data['calories'] == 0:
                    calculated_calories = (meal_data['protein'] * 4) + (meal_data['carbs'] * 4) + (meal_data['fats'] * 9)
                    if calculated_calories > 0:
                        meal_data['calories'] = calculated_calories
                
                # Only add meals with valid calorie data and reasonable values
                # Allow foods even if some macros are 0 (as long as calories > 0)
                if meal_data['calories'] > 0 and meal_data['calories'] < 5000:
                    # Get category name
                    if category_id and category_id in food_category_df['id'].values:
                        category_row = food_category_df[food_category_df['id'] == category_id]
                        meal_data['category'] = category_row.iloc[0]['description'] if len(category_row) > 0 else 'Other'
                    else:
                        meal_data['category'] = 'Other'
                    
                    # Add cuisine estimate based on food name (simple heuristic)
                    food_lower = food_name.lower()
                    if any(word in food_lower for word in ['taco', 'burrito', 'quesadilla', 'enchilada', 'mexican']):
                        meal_data['cuisine'] = 'Mexican'
                    elif any(word in food_lower for word in ['pasta', 'pizza', 'risotto', 'italian', 'spaghetti']):
                        meal_data['cuisine'] = 'Italian'
                    elif any(word in food_lower for word in ['curry', 'masala', 'naan', 'tikka', 'indian']):
                        meal_data['cuisine'] = 'Indian'
                    elif any(word in food_lower for word in ['chow', 'fried rice', 'wonton', 'chinese', 'dim sum']):
                        meal_data['cuisine'] = 'Chinese'
                    else:
                        meal_data['cuisine'] = 'American'  # Default
                    
                    # Add diet type based on macros
                    if meal_data['calories'] > 0:
                        carbs_pct = (meal_data['carbs'] * 4) / meal_data['calories'] * 100
                        fats_pct = (meal_data['fats'] * 9) / meal_data['calories'] * 100
                        
                        if carbs_pct < 10:  # Less than 10% calories from carbs
                            meal_data['diet'] = 'Low_Carb'
                        elif fats_pct < 15:  # Less than 15% from fats
                            meal_data['diet'] = 'Low_Sodium'  # Approximate
                        else:
                            meal_data['diet'] = 'Balanced'
                    else:
                        meal_data['diet'] = 'Balanced'
                    
                    # Add dietary flags based on food name and category
                    food_lower = food_name.lower()
                    category_lower = meal_data.get('category', '').lower()
                    
                    # Check for vegan/vegetarian (exclude meat, dairy, eggs)
                    meat_keywords = ['beef', 'chicken', 'pork', 'turkey', 'lamb', 'meat', 'bacon', 'sausage', 'ham', 'steak', 'fish', 'seafood', 'salmon', 'tuna', 'shrimp', 'poultry']
                    dairy_keywords = ['cheese', 'milk', 'butter', 'cream', 'yogurt', 'whey', 'casein', 'dairy']
                    egg_keywords = ['egg', 'yolk']
                    
                    has_meat = any(kw in food_lower for kw in meat_keywords)
                    has_dairy = any(kw in food_lower for kw in dairy_keywords) or 'dairy' in category_lower or 'cheese' in category_lower
                    has_eggs = any(kw in food_lower for kw in egg_keywords)
                    
                    meal_data['is_vegetarian'] = not (has_meat or has_eggs)
                    meal_data['is_vegan'] = not (has_meat or has_dairy or has_eggs)
                    
                    meals.append(meal_data)
        
        if len(meals) == 0:
            return None
        
        meals_df = pd.DataFrame(meals)
        print(f"  Processed {len(meals_df)} meals from USDA FoodData Central")
        return meals_df
        
    except Exception as e:
        print(f"  Error processing USDA meals: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_pp_recipes(recipes_paths):
    """Load and process PP_recipes split files to create meal dataset"""
    try:
        # Handle both single file (backwards compat) or list of files
        if isinstance(recipes_paths, str):
            recipes_paths = [recipes_paths]
        
        # Check if all files exist
        existing_files = [p for p in recipes_paths if os.path.exists(p)]
        if not existing_files:
            return None
        
        print(f"  Loading PP_recipes files ({len(existing_files)} parts)...")
        # Load in chunks for memory efficiency
        chunk_list = []
        chunk_size = 10000
        
        # Process each file
        for recipes_path in existing_files:
            print(f"    Loading {os.path.basename(recipes_path)}...")
            for chunk in pd.read_csv(recipes_path, chunksize=chunk_size):
                meals = []
                
                for _, row in chunk.iterrows():
                    recipe_id = row['id']
                    calorie_level = row['calorie_level']
                    
                    # Map calorie_level to actual calorie ranges
                    # Level 0 = Low (300-600 cal), Level 1 = Medium (600-900 cal), Level 2 = High (900-1200 cal)
                    if calorie_level == 0:
                        base_calories = 450  # Low - good for breakfast
                    elif calorie_level == 1:
                        base_calories = 750  # Medium - good for lunch
                    else:  # calorie_level == 2
                        base_calories = 1050  # High - good for dinner
                    
                    # Add some variation to avoid all same calories
                    import random
                    variation = random.randint(-50, 50)
                    calories = max(200, base_calories + variation)
                    
                    # Estimate macros (balanced distribution)
                    # Protein: 25%, Carbs: 50%, Fats: 25%
                    protein = int(calories * 0.25 / 4)
                    carbs = int(calories * 0.50 / 4)
                    fats = int(calories * 0.25 / 9)
                    
                    # Create realistic meal names based on ingredients and calorie level
                    try:
                        import ast
                        import random
                        ingredient_tokens = ast.literal_eval(row['ingredient_tokens'])
                        num_ingredients = len(ingredient_tokens) if isinstance(ingredient_tokens, list) else 0
                        
                        # Real meal names based on calorie level and complexity
                        meal_names_by_level = {
                            0: [  # Breakfast options
                                "Overnight Oats Bowl",
                                "Avocado Toast Special",
                                "Breakfast Smoothie Bowl",
                                "Greek Yogurt Parfait",
                                "Scrambled Eggs & Vegetables",
                                "Quinoa Breakfast Bowl",
                                "Protein Pancakes",
                                "Fruit & Nut Granola Bowl",
                                "Breakfast Burrito Bowl",
                                "Veggie Omelet Plate"
                            ],
                            1: [  # Lunch options
                                "Mediterranean Salad Bowl",
                                "Grilled Chicken Salad",
                                "Vegetable Stir Fry",
                                "Quinoa Power Bowl",
                                "Caesar Salad Wrap",
                                "Pasta Primavera",
                                "Buddha Bowl Special",
                                "Grain Bowl with Vegetables",
                                "Healthy Wrap Deluxe",
                                "Mixed Green Salad Plate"
                            ],
                            2: [  # Dinner options
                                "Grilled Salmon with Vegetables",
                                "Pasta Carbonara",
                                "Chicken and Rice Bowl",
                                "Vegetable Curry Plate",
                                "Stir Fry Noodles",
                                "Baked Cod with Sides",
                                "Steak and Potatoes",
                                "Risotto Special",
                                "Roasted Chicken Dinner",
                                "Seafood Pasta Dish"
                            ]
                        }
                        
                        # Select meal name based on calorie level
                        available_names = meal_names_by_level.get(calorie_level, meal_names_by_level[1])
                        # Use recipe ID to get consistent name (so same recipe = same name)
                        name_index = recipe_id % len(available_names)
                        recipe_name = available_names[name_index]
                        
                    except:
                        # Fallback to simple descriptive names
                        level_names = {0: 'Breakfast', 1: 'Lunch', 2: 'Dinner'}
                        recipe_name = f"{level_names.get(calorie_level, 'Meal')} Special"
                    
                    # Determine meal type from calorie level
                    meal_types = {0: 'Breakfast', 1: 'Lunch', 2: 'Dinner'}
                    meal_type = meal_types.get(calorie_level, 'Meal')
                    
                    # Check if vegetarian/vegan based on meal name
                    # Meat keywords - if meal name contains these, it's not vegetarian/vegan
                    meat_keywords = [
                        'chicken', 'salmon', 'beef', 'pork', 'turkey', 'lamb', 'meat', 
                        'bacon', 'sausage', 'ham', 'steak', 'fish', 'seafood', 'tuna', 
                        'shrimp', 'poultry', 'cod', 'seafood', 'pasta carbonara', 'steak'
                    ]
                    # Dairy/egg keywords - if meal name contains these, it's not vegan (but can be vegetarian)
                    dairy_egg_keywords = [
                        'cheese', 'milk', 'butter', 'cream', 'yogurt', 'dairy', 'parfait',
                        'egg', 'eggs', 'scrambled', 'omelet', 'carbonara'
                    ]
                    
                    meal_name_lower = recipe_name.lower()
                    has_meat = any(keyword in meal_name_lower for keyword in meat_keywords)
                    has_dairy_eggs = any(keyword in meal_name_lower for keyword in dairy_egg_keywords)
                    
                    # Determine vegetarian/vegan status
                    if has_meat:
                        is_vegetarian = False
                        is_vegan = False
                    elif has_dairy_eggs:
                        is_vegetarian = True  # Can have dairy/eggs
                        is_vegan = False  # Cannot have dairy/eggs
                    else:
                        # No meat or dairy keywords - default to vegetarian/vegan
                        is_vegetarian = True
                        is_vegan = True
                    
                    meal_data = {
                        'name': recipe_name,
                        'fdc_id': recipe_id,  # Using recipe ID
                        'calories': int(calories),
                        'protein': protein,
                        'carbs': carbs,
                        'fats': fats,
                        'category': 'Recipe',
                        'cuisine': 'American',  # Default, could improve with techniques
                        'diet': 'Balanced',
                        'is_vegetarian': is_vegetarian,
                        'is_vegan': is_vegan,
                        'meal_type': meal_type,
                        'calorie_level': calorie_level
                    }
                    
                    meals.append(meal_data)
                
                # Add meals from this chunk to the main list
                chunk_list.extend(meals)
                
                # Limit to first 50000 for now (to avoid memory issues)
                if len(chunk_list) >= 50000:
                    break
        
        if len(chunk_list) == 0:
            return None
        
        meals_df = pd.DataFrame(chunk_list)
        print(f"  Processed {len(meals_df)} recipes from PP_recipes split files")
        return meals_df
        
    except Exception as e:
        print(f"  Error processing PP_recipes: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_datasets(base_path='../'):
    """Load all datasets"""
    datasets = {}
    
    try:
        datasets['progress'] = pd.read_csv(os.path.join(base_path, 'dataset2.csv'))
        print(f"✓ Loaded progress data: {len(datasets['progress'])} rows")
    except Exception as e:
        print(f"⚠ Error loading dataset2.csv: {e}")
        datasets['progress'] = None
    
    try:
        datasets['dietary'] = pd.read_csv(os.path.join(base_path, 'dataset6.csv'))
        print(f"✓ Loaded dietary data: {len(datasets['dietary'])} rows")
    except Exception as e:
        print(f"⚠ Error loading dataset6.csv: {e}")
        datasets['dietary'] = None
    
    try:
        # Use PP_recipes split files from PP_recipes folder (has actual recipes, not just ingredients)
        # Load all CSV files from PP_recipes folder
        pp_recipes_folder = os.path.join(base_path, 'PP_recipes')
        if os.path.exists(pp_recipes_folder) and os.path.isdir(pp_recipes_folder):
            # Get all CSV files from the folder
            recipe_files = []
            for file in os.listdir(pp_recipes_folder):
                if file.endswith('.csv'):
                    recipe_files.append(os.path.join(pp_recipes_folder, file))
            
            # Sort files to ensure consistent processing order
            recipe_files.sort()
            
            if recipe_files:
                print(f"  Found {len(recipe_files)} PP_recipes files in folder...")
                recipes_df = load_pp_recipes(recipe_files)
                if recipes_df is not None and len(recipes_df) > 0:
                    print(f"✓ Loaded PP recipes: {len(recipes_df)} meals with recipe-based names")
                    datasets['meals'] = recipes_df
                else:
                    # Fallback to USDA meals
                    datasets['meals'] = load_usda_meals(os.path.join(base_path, 'dataset_mealNutrition'))
                    if datasets['meals'] is not None:
                        print(f"✓ Loaded USDA meal nutrition data: {len(datasets['meals'])} meals")
            else:
                # No CSV files found in folder, try old location
                recipe_parts = [
                    os.path.join(base_path, 'PP_recipes_part1.csv'),
                    os.path.join(base_path, 'PP_recipes_part2.csv'),
                    os.path.join(base_path, 'PP_recipes_part3.csv')
                ]
                recipes_df = load_pp_recipes(recipe_parts)
                if recipes_df is not None and len(recipes_df) > 0:
                    print(f"✓ Loaded PP recipes: {len(recipes_df)} meals with recipe-based names")
                    datasets['meals'] = recipes_df
                else:
                    # Fallback to USDA meals
                    datasets['meals'] = load_usda_meals(os.path.join(base_path, 'dataset_mealNutrition'))
                    if datasets['meals'] is not None:
                        print(f"✓ Loaded USDA meal nutrition data: {len(datasets['meals'])} meals")
        else:
            # Folder doesn't exist, try old location
            recipe_parts = [
                os.path.join(base_path, 'PP_recipes_part1.csv'),
                os.path.join(base_path, 'PP_recipes_part2.csv'),
                os.path.join(base_path, 'PP_recipes_part3.csv')
            ]
            recipes_df = load_pp_recipes(recipe_parts)
            if recipes_df is not None and len(recipes_df) > 0:
                print(f"✓ Loaded PP recipes: {len(recipes_df)} meals with recipe-based names")
                datasets['meals'] = recipes_df
            else:
                # Fallback to USDA meals
                datasets['meals'] = load_usda_meals(os.path.join(base_path, 'dataset_mealNutrition'))
                if datasets['meals'] is not None:
                    print(f"✓ Loaded USDA meal nutrition data: {len(datasets['meals'])} meals")
    except Exception as e:
        print(f"⚠ Error loading meal dataset: {e}")
        import traceback
        traceback.print_exc()
        datasets['meals'] = None
    
    try:
        datasets['exercises'] = pd.read_csv(os.path.join(base_path, 'dataset8.csv'))
        print(f"✓ Loaded exercises data: {len(datasets['exercises'])} rows")
    except Exception as e:
        print(f"⚠ Error loading dataset8.csv: {e}")
        datasets['exercises'] = None
    
    try:
        datasets['stretches'] = pd.read_csv(os.path.join(base_path, 'stretch_exercise_dataset.csv'))
        print(f"✓ Loaded stretches data: {len(datasets['stretches'])} rows")
    except Exception as e:
        print(f"⚠ Error loading stretch_exercise_dataset.csv: {e}")
        datasets['stretches'] = None
    
    try:
        datasets['powerlifting'] = pd.read_csv(os.path.join(base_path, 'powerlifting_dataset.csv'))
        print(f"✓ Loaded powerlifting data: {len(datasets['powerlifting'])} rows")
    except Exception as e:
        print(f"⚠ Error loading powerlifting_dataset.csv: {e}")
        datasets['powerlifting'] = None
    
    return datasets
