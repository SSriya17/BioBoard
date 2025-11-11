import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from './Header'
import '../App.css'

function generateWorkoutPlan(user) {
  const goal = user.fitnessGoal || 'General Fitness'
  const activity = user.activityLevel || 'Moderate'

  // Force a 5-day split regardless of activity level
  const daysPerWeek = 5

  const templates = {
    'Weight Loss': [
      { day: 'Day 1', focus: 'Full Body Circuit', details: ['Squat 3x12', 'Push-ups 3x12', 'Rows 3x12', 'Plank 3x45s', '20 min Zone 2 cardio'] },
      { day: 'Day 2', focus: 'Cardio + Core', details: ['30-40 min Zone 2 cardio', 'Hanging knee raises 3x12', 'Side plank 3x30s/side'] },
      { day: 'Day 3', focus: 'Upper Body + Intervals', details: ['Incline DB Press 4x10', 'Lat Pulldown 4x10', 'Shoulder Press 3x12', 'Bike: 8x30s hard / 90s easy'] },
      { day: 'Day 4', focus: 'Lower Body + Steps', details: ['Deadlift 4x6', 'Lunges 3x12/leg', 'Leg Curl 3x12', '8-10k steps'] },
      { day: 'Optional', focus: 'Active Recovery', details: ['Walk 45-60 min or yoga / mobility'] },
    ],
    'Muscle Gain': [
      { day: 'Day 1', focus: 'Upper Push', details: ['Bench Press 5x5', 'Incline DB Press 4x8', 'Overhead Press 4x8', 'Lateral Raises 4x12', 'Triceps 3x12'] },
      { day: 'Day 2', focus: 'Lower Strength', details: ['Back Squat 5x5', 'RDL 4x8', 'Leg Press 4x10', 'Calf Raise 4x15'] },
      { day: 'Day 3', focus: 'Upper Pull', details: ['Pull-ups 5xAMRAP', 'Barbell Row 4x8', 'Face Pull 4x12', 'Biceps 3x12'] },
      { day: 'Day 4', focus: 'Lower Hypertrophy', details: ['Front Squat 4x8', 'Hip Thrust 4x10', 'Leg Curl 4x12', 'Walking Lunges 3x12/leg'] },
      { day: 'Optional', focus: 'Arms/Delts + Cardio', details: ['Supersets arms/delts 30 min', 'Zone 2 20 min'] },
    ],
    'Endurance': [
      { day: 'Day 1', focus: 'Zone 2 Base', details: ['Run/Cycle/Row 45-60 min Zone 2'] },
      { day: 'Day 2', focus: 'Strength Maintenance', details: ['Full Body 3x10: Squat, Press, Row, Lunge, Core'] },
      { day: 'Day 3', focus: 'Intervals', details: ['10x2 min hard / 2 min easy'] },
      { day: 'Day 4', focus: 'Long Session', details: ['75-90 min Zone 2'] },
      { day: 'Optional', focus: 'Mobility + Easy 30', details: ['Mobility 20 min', 'Easy cardio 30 min'] },
    ],
    'General Fitness': [
      { day: 'Day 1', focus: 'Full Body A', details: ['Goblet Squat 4x10', 'Push-ups 4xAMRAP', 'Rows 4x10', 'Plank 3x45s'] },
      { day: 'Day 2', focus: 'Cardio 30-40', details: ['Zone 2 steady 30-40 min'] },
      { day: 'Day 3', focus: 'Full Body B', details: ['Deadlift 4x6', 'Overhead Press 4x8', 'Lat Pulldown 4x10', 'Side Plank 3x30s/side'] },
      { day: 'Day 4', focus: 'Intervals + Steps', details: ['6x1 min hard / 2 min easy', '8-10k steps'] },
      { day: 'Day 5', focus: 'Mobility + Core', details: ['Mobility flow 20 min', 'Farmer Carry 4x40m', 'Hollow Hold 3x30s', 'Walk 30-45 min'] },
    ],
  }

  const plan = templates[goal] || templates['General Fitness']
  return { daysPerWeek, goal, activity, plan }
}

function WorkoutDetail() {
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

  if (!userData) return <div>Loading...</div>

  const { daysPerWeek, goal, activity, plan } = generateWorkoutPlan(userData)

  return (
    <div style={{ minHeight: '100vh', padding: '40px 20px 100px 20px', maxWidth: 1000, margin: '0 auto' }}>
      <div className="page-header">
        <Header variant="light" />
        <h1>PERSONALIZED HEALTH</h1>
      </div>

      <button className="btn-primary" onClick={() => navigate('/dashboard')} style={{ marginBottom: 32 }}>
        ← Back to Dashboard
      </button>

      <div className="form-container" style={{ marginBottom: 24 }}>
        <h2 style={{ marginBottom: 12, fontSize: 24, fontWeight: 600 }}>Workout Regimen</h2>
        <div style={{ color: 'rgba(255,255,255,0.8)', marginBottom: 8 }}>
          Goal: <strong>{goal}</strong> • Activity Level: <strong>{activity}</strong> • Target Days/Week: <strong>{daysPerWeek}</strong>
        </div>
      </div>

      <div className="form-container">
        {plan.slice(0, daysPerWeek).map((block, idx) => (
          <div key={idx} style={{ marginBottom: idx < daysPerWeek - 1 ? 24 : 0 }}>
            <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>{block.day} — {block.focus}</div>
            <ul style={{ paddingLeft: 18 }}>
              {block.details.map((d, i) => (
                <li key={i} style={{ marginBottom: 4 }}>{d}</li>
              ))}
            </ul>
            {idx < daysPerWeek - 1 && <div style={{ width: '100%', height: 1, backgroundColor: 'rgba(255,255,255,0.2)', marginTop: 16 }}></div>}
          </div>
        ))}
      </div>

      <div className="footer">
        <Header variant="dark" />
      </div>
    </div>
  )
}

export default WorkoutDetail


