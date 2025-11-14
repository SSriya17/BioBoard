/**
 * API service for communicating with the backend
 */

const API_BASE_URL = 'http://localhost:5001/api';

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
    // Return fallback values
    return null;
  }
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
    // Return empty array - frontend will use its own meal database
    return [];
  }
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

