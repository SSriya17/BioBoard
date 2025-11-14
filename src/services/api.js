/**
 * API service for communicating with the backend
 */

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001/api';

/**
 * Get nutritional targets from backend
 */
export async function getNutritionalTargets(userData) {
  try {
    const response = await fetch(`${API_BASE_URL}/nutritional-targets`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        age: parseInt(userData.age),
        weight: parseFloat(userData.weight),
        heightFeet: parseInt(userData.heightFeet),
        heightInches: parseInt(userData.heightInches),
        activityLevel: userData.activityLevel,
        gender: 'Male' // Default, can be updated if you add gender field
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching nutritional targets:', error);
    // Calculate fallback values using standard formulas
    return calculateFallbackTargets(userData);
  }
}

/**
 * Calculate fallback nutritional targets using standard formulas
 */
function calculateFallbackTargets(userData) {
  const age = parseInt(userData.age) || 25;
  const weightPounds = parseFloat(userData.weight) || 165; // weight is in pounds
  const weightKg = weightPounds * 0.453592; // Convert pounds to kg
  const heightFeet = parseInt(userData.heightFeet) || 5;
  const heightInches = parseInt(userData.heightInches) || 10;
  const activityLevel = userData.activityLevel || 'Moderate';
  
  // Convert height to cm
  const heightCm = (heightFeet * 12 + heightInches) * 2.54;
  
  // BMR calculation using Mifflin-St Jeor Equation (assuming Male as default)
  // For males: BMR = 10 * weight(kg) + 6.25 * height(cm) - 5 * age + 5
  const bmr = 10 * weightKg + 6.25 * heightCm - 5 * age + 5;
  
  // Activity multipliers
  const activityMultipliers = {
    'Sedentary': 1.2,
    'Light': 1.375,
    'Moderate': 1.55,
    'Active': 1.725,
    'Very Active': 1.9
  };
  
  const multiplier = activityMultipliers[activityLevel] || 1.55;
  const calories = Math.max(1200, Math.round(bmr * multiplier));
  
  // Macronutrient distribution (typical balanced diet)
  // Protein: 15% of calories (4 cal/g)
  // Carbs: 50% of calories (4 cal/g)
  // Fats: 35% of calories (9 cal/g)
  const protein = Math.max(50, Math.round(calories * 0.15 / 4));
  const carbs = Math.max(100, Math.round(calories * 0.50 / 4));
  const fats = Math.max(30, Math.round(calories * 0.35 / 9));
  
  return {
    calories,
    protein,
    carbs,
    fats
  };
}

/**
 * Get meal recommendations from backend
 */
export async function getMealRecommendations(calorieGoal, dietaryPreferences, numMeals = 3) {
  try {
    const response = await fetch(`${API_BASE_URL}/meal-recommendations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        calorieGoal,
        dietaryPreferences,
        numMeals
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching meal recommendations:', error);
    // Return fallback meal recommendations
    return getFallbackMeals(calorieGoal, numMeals);
  }
}

/**
 * Generate fallback meal recommendations when API is unavailable
 */
function getFallbackMeals(calorieGoal, numMeals = 3) {
  const caloriesPerMeal = Math.round(calorieGoal / numMeals);
  
  const mealTypes = ['Breakfast', 'Lunch', 'Dinner', 'Snack'];
  const meals = [];
  
  // Sample fallback meals
  const fallbackMealDatabase = {
    'Breakfast': [
      { name: 'Oatmeal with Berries', calories: 350, protein: 12, carbs: 60, fats: 8 },
      { name: 'Greek Yogurt Parfait', calories: 300, protein: 20, carbs: 35, fats: 8 },
      { name: 'Whole Grain Toast with Avocado', calories: 320, protein: 10, carbs: 40, fats: 12 },
      { name: 'Scrambled Eggs with Vegetables', calories: 280, protein: 18, carbs: 8, fats: 18 }
    ],
    'Lunch': [
      { name: 'Grilled Chicken Salad', calories: 400, protein: 35, carbs: 20, fats: 18 },
      { name: 'Quinoa Bowl with Vegetables', calories: 380, protein: 15, carbs: 55, fats: 12 },
      { name: 'Turkey Wrap', calories: 350, protein: 25, carbs: 40, fats: 10 },
      { name: 'Salmon with Sweet Potato', calories: 450, protein: 30, carbs: 45, fats: 15 }
    ],
    'Dinner': [
      { name: 'Baked Chicken Breast with Rice', calories: 450, protein: 40, carbs: 50, fats: 10 },
      { name: 'Vegetable Stir Fry with Tofu', calories: 380, protein: 20, carbs: 50, fats: 12 },
      { name: 'Lean Beef with Roasted Vegetables', calories: 420, protein: 35, carbs: 30, fats: 18 },
      { name: 'Pasta with Marinara and Vegetables', calories: 400, protein: 15, carbs: 70, fats: 8 }
    ],
    'Snack': [
      { name: 'Apple with Almond Butter', calories: 200, protein: 6, carbs: 25, fats: 10 },
      { name: 'Protein Smoothie', calories: 250, protein: 20, carbs: 30, fats: 5 },
      { name: 'Mixed Nuts', calories: 180, protein: 6, carbs: 8, fats: 15 },
      { name: 'Greek Yogurt with Granola', calories: 220, protein: 15, carbs: 28, fats: 6 }
    ]
  };
  
  for (let i = 0; i < numMeals; i++) {
    const mealType = mealTypes[i] || mealTypes[i % mealTypes.length];
    const options = fallbackMealDatabase[mealType] || fallbackMealDatabase['Lunch'];
    // Pick a meal that's closest to the target calories per meal
    const meal = options.reduce((closest, current) => {
      return Math.abs(current.calories - caloriesPerMeal) < Math.abs(closest.calories - caloriesPerMeal)
        ? current : closest;
    });
    
    meals.push({
      type: mealType,
      name: meal.name,
      calories: meal.calories,
      protein: meal.protein,
      carbs: meal.carbs,
      fats: meal.fats
    });
  }
  
  return meals;
}

/**
 * Get workout plan from backend
 */
export async function getWorkoutPlan(fitnessGoal, activityLevel, experienceLevel = 'Moderate') {
  try {
    const response = await fetch(`${API_BASE_URL}/workout-plan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        fitnessGoal,
        activityLevel,
        experienceLevel
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching workout plan:', error);
    // Return null - frontend will use its own workout plan
    return null;
  }
}

/**
 * Get progress forecast from backend
 */
export async function getProgressForecast(weight, fitnessGoal, activityLevel, weeks = 12) {
  try {
    const response = await fetch(`${API_BASE_URL}/progress-forecast`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        weight: parseFloat(weight),
        fitnessGoal,
        activityLevel,
        weeks
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching progress forecast:', error);
    // Return null - frontend will use its own forecast
    return null;
  }
}

/**
 * Health check
 */
export async function checkApiHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      return false;
    }
    const data = await response.json();
    return data.status === 'ok';
  } catch (error) {
    return false;
  }
}

