import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Logo from './Logo'
import '../App.css'

function Dashboard() {
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

  const heightDisplay = `${userData.heightFeet}'${userData.heightInches}"`

  return (
    <div style={{ minHeight: '100vh', padding: '40px 20px 100px 20px' }}>
      {/* Header */}
      <div className="page-header">
        <div style={{ marginBottom: '16px' }}><Logo variant="light" width={220} /></div>
        <h1>PERSONALIZED HEALTH</h1>
      </div>

      {/* Profile Section */}
      <div className="form-container" style={{ marginBottom: '32px' }}>
        <h2 style={{ marginBottom: '24px', fontSize: '20px', fontWeight: '600' }}>Your profile</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '24px' }}>
          <div>
            <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '8px' }}>AGE</div>
            <div style={{ fontSize: '18px', fontWeight: '600' }}>{userData.age}</div>
          </div>
          <div>
            <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '8px' }}>HEIGHT/WEIGHT</div>
            <div style={{ fontSize: '18px', fontWeight: '600' }}>{heightDisplay}/{userData.weight}</div>
          </div>
          <div>
            <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '8px' }}>ACTIVITY LEVEL</div>
            <div style={{ fontSize: '18px', fontWeight: '600' }}>{userData.activityLevel}</div>
          </div>
          <div>
            <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '8px' }}>PRIMARY GOAL</div>
            <div style={{ fontSize: '18px', fontWeight: '600' }}>{userData.fitnessGoal}</div>
          </div>
        </div>
      </div>

      {/* Main Content Sections */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px', maxWidth: '1200px', margin: '0 auto' }}>
        {/* Nutrition Section */}
        <div className="form-container" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '600' }}>Nutrition</h2>
            <span style={{ fontSize: '24px' }}>🍴</span>
          </div>
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '24px', flex: 1 }}>
            Custom Meal Plan & Targets
          </p>
          <button
            className="btn-primary"
            onClick={() => navigate('/nutrition')}
            style={{ marginTop: 'auto' }}
          >
            View plan
          </button>
        </div>

        {/* Workout Regimen Section */}
        <div className="form-container" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '600' }}>Workout Regimen</h2>
            <span style={{ fontSize: '24px' }}>🏋️</span>
          </div>
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '24px', flex: 1 }}>
            Custom Lifting Program
          </p>
          <button className="btn-primary" style={{ marginTop: 'auto' }}>
            View plan
          </button>
        </div>

        {/* Progress Forecast Section */}
        <div className="form-container" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '600' }}>Progress Forecast</h2>
          </div>
          <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '24px', flex: 1 }}>
            12-Week Projection
          </p>
          <button className="btn-primary" style={{ marginTop: 'auto' }}>
            View plan
          </button>
        </div>
      </div>

      {/* Footer */}
      <div className="footer">
        <Logo variant="dark" width={160} />
      </div>
    </div>
  )
}

export default Dashboard

