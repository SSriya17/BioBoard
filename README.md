# BioBoard
Health Fitness Web App

A personalized health analytics web application that generates custom health plans including nutritional targets, meal suggestions, workout regimens, and progress forecasts using machine learning models.

🌐 **Live Website:** [https://bio-board-seven.vercel.app/](https://bio-board-seven.vercel.app/)

## Features

- **Multi-Step User Input Form**: Collects user metrics (age, weight, height, activity level, fitness goals, dietary preferences)
- **Personalized Dashboard**: Displays user profile and three main sections (Nutrition, Workout Regimen, Progress Forecast)
- **Nutritional Targets**: Shows daily calorie and macronutrient recommendations
- **Meal Recommendations**: Suggests personalized meal plans based on dietary preferences
- **Workout Plans**: Custom workout regimens based on fitness goals
- **Progress Forecasting**: 12-week progress projections

## Tech Stack

### Frontend
- **React.js** with Vite
- **React Router** for navigation
- Modern CSS with dark theme design

### Backend (To be implemented)
- **Python** with Flask/FastAPI
- **Machine Learning Models**:
  - Linear Regression (Nutritional Targets & Progress Forecast)
  - Content-Based Recommendation (Meal Recommendations)
  - Decision Tree Classifier (Workout Plans)

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

## Project Structure

```
BioBoard/
├── src/
│   ├── components/
│   │   ├── LandingPage.jsx      # Multi-step form (Steps 1-3)
│   │   ├── Dashboard.jsx        # Main dashboard with profile and sections
│   │   └── NutritionDetail.jsx  # Nutrition targets and meal plan
│   ├── App.jsx                  # Main app with routing
│   ├── App.css                  # Component styles
│   ├── index.css                # Global styles
│   └── main.jsx                 # Entry point
├── dataset1.csv                 # Health/fitness datasets
├── dataset2.csv
├── dataset3.csv
├── dataset4.csv
└── package.json
```

## Model Selection

### Nutritional Targets
**Goal:** Provide daily calorie and macronutrient recommendations for the user's personalized plan.  
**Chosen Model:** Linear Regression  
**Reason for Selection:** Ideal for predicting continuous numeric outputs like calories and macronutrient needs from personal metrics.  
**How the Model is Trained:** The model learns relationships between user attributes (age, height, weight, activity level, etc.) and their corresponding daily calorie needs from the dataset.  

### Meal Recommendations
**Goal:** Suggest meal options that align with the user's calorie goal and dietary preferences.  
**Chosen Model:** Content-Based Recommendation Model (using KNN or cosine similarity)  
**Reason for Selection:** Effective for comparing nutrient similarities and recommending meals that fit individual user preferences.  
**How the Model is Trained:** The model uses a dataset of meals and their nutritional details to calculate similarity scores between each meal and the user's target nutrient profile.  

### Workout Plan
**Goal:** Generate personalized workout plans based on user goals and activity level.  
**Chosen Model:** Decision Tree Classifier  
**Reason for Selection:** Easy to interpret and well-suited for classifying users into workout types based on input features.  
**How the Model is Trained:** The model is trained using user data labeled with corresponding workout categories, learning the decision paths that best match input features like goal and activity level.  

### Progress Forecast
**Goal:** Predict user progress over time to track and visualize health improvements.  
**Chosen Model:** Linear Regression  
**Reason for Selection:** Works well for forecasting trends in continuous data like weight or calorie changes over time.  
**How the Model is Trained:** The model analyzes historical progress data (e.g., weight, calorie intake, workouts) to learn the rate and pattern of change, which it then uses to predict future values.

## Next Steps

1. Implement Python backend with Flask/FastAPI
2. Train machine learning models using the provided datasets
3. Connect frontend to backend API endpoints
4. Deploy application (Heroku/Netlify)  
