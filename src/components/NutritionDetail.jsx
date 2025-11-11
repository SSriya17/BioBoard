import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from './Header'
import '../App.css'

function NutritionDetail() {
  const [userData, setUserData] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    const data = localStorage.getItem('userData')
    if (data) {
      setUserData(JSON.parse(data))
    } else {
      navigate('/')
    }
  }, [navigate])

  if (!userData) {
    return <div>Loading...</div>
  }

  // Calculate nutritional targets (placeholder calculations - will be replaced with ML model predictions)
  const calculateTargets = () => {
    const age = parseInt(userData.age) || 25
    const weight = parseFloat(userData.weight) || 150
    const heightInches = (parseInt(userData.heightFeet) || 5) * 12 + (parseInt(userData.heightInches) || 10)
    
    // Simple BMR calculation (Mifflin-St Jeor Equation)
    const bmr = 10 * weight + 6.25 * heightInches - 5 * age + 5
    
    // Activity multiplier
    const activityMultipliers = {
      'Sedentary': 1.2,
      'Light': 1.375,
      'Moderate': 1.55,
      'Active': 1.725,
      'Very Active': 1.9
    }
    const multiplier = activityMultipliers[userData.activityLevel] || 1.55
    const calories = Math.round(bmr * multiplier)
    
    // Macronutrient distribution (placeholder - will use ML model)
    const protein = Math.round(calories * 0.15 / 4) // 15% of calories from protein
    const carbs = Math.round(calories * 0.50 / 4) // 50% of calories from carbs
    const fats = Math.round(calories * 0.35 / 9) // 35% of calories from fats
    
    return { calories, protein, carbs, fats }
  }

  const targets = calculateTargets()

  // Meal suggestions (placeholder - will use ML recommendation model)
  const meals = [
    {
      name: 'Bacon & Eggs with Avocado',
      type: 'Breakfast',
      protein: Math.round(targets.protein / 3),
      carbs: Math.round(targets.carbs / 3),
      fats: Math.round(targets.fats / 3),
      calories: Math.round(targets.calories / 3)
    },
    {
      name: 'Cauliflower Rice Chicken Bowl',
      type: 'Lunch',
      protein: Math.round(targets.protein / 3),
      carbs: Math.round(targets.carbs / 3),
      fats: Math.round(targets.fats / 3),
      calories: Math.round(targets.calories / 3)
    },
    {
      name: 'Ribeye Steak',
      type: 'Dinner',
      protein: Math.round(targets.protein / 3),
      carbs: Math.round(targets.carbs / 3),
      fats: Math.round(targets.fats / 3),
      calories: Math.round(targets.calories / 3)
    }
  ]

  return (
    <div style={{ minHeight: '100vh', padding: '40px 20px 100px 20px', maxWidth: '1000px', margin: '0 auto' }}>
      {/* Header */}
      <div className="page-header">
        <Header variant="light" />
        <h1>PERSONALIZED HEALTH</h1>
      </div>

      {/* Back Button */}
      <button
        className="btn-primary"
        onClick={() => navigate('/dashboard')}
        style={{ marginBottom: '32px' }}
      >
        ← Back to Dashboard
      </button>

      {/* Nutritional Targets Section */}
      <div className="form-container" style={{ marginBottom: '32px' }}>
        <h2 style={{ marginBottom: '24px', fontSize: '24px', fontWeight: '600' }}>Nutritional Targets</h2>
        
        <div style={{ marginBottom: '32px' }}>
          <div style={{ fontSize: '48px', fontWeight: '700', marginBottom: '8px' }}>{targets.calories}</div>
          <div style={{ fontSize: '18px', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '16px' }}>Calories</div>
          <div style={{ width: '100%', height: '8px', backgroundColor: 'rgba(255, 255, 255, 0.2)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: '60%', height: '100%', backgroundColor: '#4A90E2', borderRadius: '4px' }}></div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
          <div>
            <div style={{ fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>{targets.protein}g</div>
            <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.7)' }}>PROTEIN</div>
            <div style={{ width: '100%', height: '2px', backgroundColor: '#ffffff', marginTop: '12px' }}></div>
          </div>
          <div>
            <div style={{ fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>{targets.carbs}g</div>
            <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.7)' }}>CARBS</div>
            <div style={{ width: '100%', height: '2px', backgroundColor: '#ffffff', marginTop: '12px' }}></div>
          </div>
          <div>
            <div style={{ fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>{targets.fats}g</div>
            <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.7)' }}>Fats</div>
            <div style={{ width: '100%', height: '2px', backgroundColor: '#ffffff', marginTop: '12px' }}></div>
          </div>
        </div>
      </div>

      {/* Suggested Meal Plan Section */}
      <div className="form-container">
        <h2 style={{ marginBottom: '24px', fontSize: '24px', fontWeight: '600' }}>Suggested Meal Plan</h2>
        
        {meals.map((meal, index) => (
          <div key={index} style={{ marginBottom: index < meals.length - 1 ? '32px' : '0' }}>
            <div style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px' }}>{meal.type}</div>
            <div style={{ fontSize: '18px', marginBottom: '16px' }}>{meal.name}</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '8px' }}>
              <div>
                <div style={{ fontSize: '16px', fontWeight: '600' }}>Protein {meal.protein}g</div>
              </div>
              <div>
                <div style={{ fontSize: '16px', fontWeight: '600' }}>Carbs {meal.carbs}g</div>
              </div>
              <div>
                <div style={{ fontSize: '16px', fontWeight: '600' }}>Fat {meal.fats}g</div>
              </div>
            </div>
            <div style={{ fontSize: '18px', fontWeight: '600', color: 'rgba(255, 255, 255, 0.8)' }}>
              Total calories: {meal.calories}cal
            </div>
            {index < meals.length - 1 && (
              <div style={{ width: '100%', height: '1px', backgroundColor: 'rgba(255, 255, 255, 0.2)', marginTop: '24px' }}></div>
            )}
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="footer">
        <Header variant="dark" />
      </div>
    </div>
  )
}

export default NutritionDetail

