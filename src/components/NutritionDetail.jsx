import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from './Header'
import Logo from './Logo'
import '../App.css'
import { getNutritionalTargets, getMealRecommendations } from '../services/api'

function NutritionDetail() {
  const [userData, setUserData] = useState(null)
  const [targets, setTargets] = useState(null)
  const [meals, setMeals] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  // All meal recommendations now come ONLY from the ML model via the backend API
  // No frontend fallback database - ensures we always use the real dataset

  useEffect(() => {
    const data = localStorage.getItem('userData')
    if (data) {
      const parsed = JSON.parse(data)
      setUserData(parsed)
      loadNutritionData(parsed)
    } else {
      navigate('/')
    }
  }, [navigate])

  const loadNutritionData = useCallback(async (userData) => {
    setLoading(true)
    try {
      // Get nutritional targets from API
      const apiTargets = await getNutritionalTargets(userData)
      
      if (apiTargets) {
        setTargets(apiTargets)
        
        // Get meal recommendations from API
        const numMeals = parseInt(userData.mealsPerDay) || 3
        const apiMeals = await getMealRecommendations(
          apiTargets.calories,
          userData.dietaryPreferences || 'Omnivore',
          numMeals
        )
        
        if (apiMeals && apiMeals.length > 0) {
          console.log('✓ API meals received from ML model:', apiMeals)
          setMeals(apiMeals)
        } else {
          console.error('✗ API returned no meals. Check backend server and ML model.')
          setMeals([])
        }
      } else {
        console.error('✗ API failed to return nutritional targets. Check backend server.')
        setTargets(null)
        setMeals([])
      }
    } catch (error) {
      console.error('✗ Error loading nutrition data:', error)
      setTargets(null)
      setMeals([])
    } finally {
      setLoading(false)
    }
  }, [])

  if (!userData || loading) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center',
        padding: '40px 20px'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: '600', marginBottom: '16px' }}>
            Loading Your Personalized Meal Plan...
          </div>
          <div style={{ fontSize: '16px', color: 'rgba(255, 255, 255, 0.7)' }}>
            Processing {userData ? `${userData.mealsPerDay || 3} meals` : 'meals'} from our database
          </div>
          <div style={{ 
            marginTop: '32px',
            width: '200px',
            height: '4px',
            backgroundColor: 'rgba(255, 255, 255, 0.2)',
            borderRadius: '2px',
            overflow: 'hidden',
            marginLeft: 'auto',
            marginRight: 'auto'
          }}>
            <div style={{
              width: '100%',
              height: '100%',
              backgroundColor: '#4A90E2',
              animation: 'progressBar 2s ease-in-out infinite'
            }}></div>
          </div>
          <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.5)', marginTop: '24px' }}>
            This may take 30-60 seconds on first load...
          </div>
        </div>
      </div>
    )
  }

  if (!targets) {
    return <div>Error loading nutritional data</div>
  }

  return (
    <div style={{ minHeight: '100vh', padding: '40px 20px 160px 20px', maxWidth: '1000px', margin: '0 auto' }}>
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
      <div className="form-container fade-in" style={{ marginBottom: '32px' }}>
        <h2 style={{ marginBottom: '24px', fontSize: '24px', fontWeight: '600' }}>Nutritional Targets</h2>
        
        <div style={{ marginBottom: '32px' }}>
          <div style={{ fontSize: '48px', fontWeight: '700', marginBottom: '8px' }}>{targets.calories}</div>
          <div style={{ fontSize: '18px', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '16px' }}>Calories</div>
          <div style={{ width: '100%', height: '8px', backgroundColor: 'rgba(255, 255, 255, 0.2)', borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ width: '60%', height: '100%', backgroundColor: '#4A90E2', borderRadius: '4px', animation: 'progressBar 1.5s ease-out forwards' }}></div>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
          <div className="stagger-1">
            <div style={{ fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>{targets.protein}g</div>
            <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.7)' }}>PROTEIN</div>
            <div style={{ width: '100%', height: '2px', backgroundColor: '#ffffff', marginTop: '12px' }}></div>
          </div>
          <div className="stagger-2">
            <div style={{ fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>{targets.carbs}g</div>
            <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.7)' }}>CARBS</div>
            <div style={{ width: '100%', height: '2px', backgroundColor: '#ffffff', marginTop: '12px' }}></div>
          </div>
          <div className="stagger-3">
            <div style={{ fontSize: '32px', fontWeight: '700', marginBottom: '8px' }}>{targets.fats}g</div>
            <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.7)' }}>Fats</div>
            <div style={{ width: '100%', height: '2px', backgroundColor: '#ffffff', marginTop: '12px' }}></div>
          </div>
        </div>
      </div>

      {/* Suggested Meal Plan Section */}
      <div className="form-container scale-in" style={{ paddingBottom: '48px', marginBottom: '40px' }}>
        <h2 style={{ marginBottom: '24px', fontSize: '24px', fontWeight: '600' }}>Suggested Meal Plan</h2>
        
        {loading ? (
          <div style={{ color: 'rgba(255, 255, 255, 0.7)', textAlign: 'center', padding: '20px' }}>
            Loading meal plan...
          </div>
        ) : meals && meals.length > 0 ? (
          meals.map((meal, index) => (
          <div key={index} className="fade-in" style={{ marginBottom: index < meals.length - 1 ? '32px' : '16px', animationDelay: `${index * 0.15}s`, opacity: 0 }}>
            <div style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px', color: '#4A90E2' }}>{meal.type}</div>
            <div style={{ fontSize: '18px', marginBottom: '16px', fontWeight: '500' }}>{meal.name}</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '12px' }}>
              <div style={{ padding: '12px', backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
                <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.6)', marginBottom: '4px' }}>PROTEIN</div>
                <div style={{ fontSize: '18px', fontWeight: '700' }}>{meal.protein}g</div>
              </div>
              <div style={{ padding: '12px', backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
                <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.6)', marginBottom: '4px' }}>CARBS</div>
                <div style={{ fontSize: '18px', fontWeight: '700' }}>{meal.carbs}g</div>
              </div>
              <div style={{ padding: '12px', backgroundColor: 'rgba(255, 255, 255, 0.05)', borderRadius: '6px', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
                <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.6)', marginBottom: '4px' }}>FAT</div>
                <div style={{ fontSize: '18px', fontWeight: '700' }}>{meal.fats}g</div>
              </div>
            </div>
            <div style={{ fontSize: '16px', fontWeight: '600', color: '#4A90E2', marginTop: '8px' }}>
              Total calories: {meal.calories} cal
            </div>
            {index < meals.length - 1 && (
              <div style={{ width: '100%', height: '1px', backgroundColor: 'rgba(255, 255, 255, 0.2)', marginTop: '24px' }}></div>
            )}
          </div>
          ))
        ) : (
          <div style={{ color: 'rgba(255, 255, 255, 0.7)', textAlign: 'center', padding: '20px' }}>
            {loading ? 'Loading meal plan from ML model...' : 'No meals available. Make sure backend server is running on port 5001.'}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="footer">
        <Logo variant="dark" width={110} />
      </div>
    </div>
  )
}

export default NutritionDetail

