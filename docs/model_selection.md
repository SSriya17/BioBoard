# Chosen Machine Learning Models for Features

### Nutritional Targets
**Goal:** Provide daily calorie and macronutrient recommendations for the user’s personalized plan.  
**Chosen Model:** Linear Regression  
**Reason for Selection:** Ideal for predicting continuous numeric outputs like calories and macronutrient needs from personal metrics.  
**How the Model is Trained:** The model learns relationships between user attributes (age, height, weight, activity level, etc.) and their corresponding daily calorie needs from the dataset.  

---

### Meal Recommendations
**Goal:** Suggest meal options that align with the user’s calorie goal and dietary preferences.  
**Chosen Model:** Content-Based Recommendation Model (using KNN or cosine similarity)  
**Reason for Selection:** Effective for comparing nutrient similarities and recommending meals that fit individual user preferences.  
**How the Model is Trained:** The model uses a dataset of meals and their nutritional details to calculate similarity scores between each meal and the user’s target nutrient profile.  

---

### Workout Plan
**Goal:** Generate personalized workout plans based on user goals and activity level.  
**Chosen Model:** Decision Tree Classifier  
**Reason for Selection:** Easy to interpret and well-suited for classifying users into workout types based on input features.  
**How the Model is Trained:** The model is trained using user data labeled with corresponding workout categories, learning the decision paths that best match input features like goal and activity level.  

---

### Progress Forecast
**Goal:** Predict user progress over time to track and visualize health improvements.  
**Chosen Model:** Linear Regression  
**Reason for Selection:** Works well for forecasting trends in continuous data like weight or calorie changes over time.  
**How the Model is Trained:** The model analyzes historical progress data (e.g., weight, calorie intake, workouts) to learn the rate and pattern of change, which it then uses to predict future values.  
