import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import Header from './Header'
import Logo from './Logo'
import '../App.css'

function LandingPage() {
  const location = useLocation()
  const isEditMode = location.pathname === '/profile'
  
  // Initialize form data from localStorage if editing, otherwise empty
  const existingData = localStorage.getItem('userData')
  const initialFormData = isEditMode && existingData ? JSON.parse(existingData) : {
    age: '',
    weight: '',
    heightFeet: '',
    heightInches: '',
    activityLevel: '',
    fitnessGoal: '',
    dietaryPreferences: '',
    mealsPerDay: ''
  }
  
  const [step, setStep] = useState(isEditMode ? 1 : 0) // Skip splash screen if editing
  const [formData, setFormData] = useState(initialFormData)
  const navigate = useNavigate()

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleNext = () => {
    if (step === 0) {
      // Move from splash to form
      setStep(1)
    } else if (step < 3) {
      setStep(step + 1)
    } else {
      // Save to localStorage and navigate to dashboard
      localStorage.setItem('userData', JSON.stringify(formData))
      navigate('/dashboard')
    }
  }

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1)
    }
  }

  const isStepValid = () => {
    if (step === 1) {
      return formData.age && formData.weight && formData.heightFeet && formData.heightInches
    } else if (step === 2) {
      return formData.activityLevel && formData.fitnessGoal
    } else if (step === 3) {
      return formData.dietaryPreferences && formData.mealsPerDay
    }
    return false
  }

  // Splash Screen (only show if not in edit mode)
  if (step === 0 && !isEditMode) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'center',
        padding: '40px 20px'
      }}>
        {/* Animated Logo */}
        <div className="splash-logo" style={{ marginBottom: '40px' }}>
          <Logo variant="light" width={200} />
        </div>

        {/* Animated Title */}
        <div className="splash-title" style={{ marginBottom: '60px' }}>
          <h1 style={{ 
            fontSize: '36px', 
            fontWeight: '600', 
            textAlign: 'center',
            letterSpacing: '2px'
          }}>
            PERSONALIZED HEALTH APP
          </h1>
        </div>

        {/* Start Button */}
        <div className="splash-button" style={{ marginTop: '20px' }}>
          <button 
            className="btn-primary" 
            onClick={handleNext}
            style={{ 
              padding: '16px 48px', 
              fontSize: '18px',
              minWidth: '200px'
            }}
          >
            Input Your Data
          </button>
        </div>

        {/* Footer */}
        <div className="footer">
          <Logo variant="dark" width={110} />
        </div>
      </div>
    )
  }

  return (
    <div style={{ minHeight: '100vh', padding: '40px 20px 120px 20px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      {/* Header */}
      <div className="page-header">
        <Header variant="light" />
        <h1>{isEditMode ? 'EDIT PROFILE' : 'PERSONALIZED HEALTH'}</h1>
      </div>

      {/* Back to Dashboard button if editing */}
      {isEditMode && (
        <button
          className="btn-primary"
          onClick={() => navigate('/dashboard')}
          style={{ 
            marginBottom: '24px',
            padding: '10px 20px', 
            fontSize: '14px'
          }}
        >
          ← Back to Dashboard
        </button>
      )}

      {/* Step Indicator */}
      <div className="step-indicator">Step {step} of 3</div>
      <div className="step-divider"></div>

      {/* Form Container */}
      <div className="form-container fade-in">
        {step === 1 && (
          <>
            <div className="form-group">
              <label>Age</label>
              <input
                type="number"
                className="input-field"
                value={formData.age}
                min="0"
                onChange={(e) => handleInputChange('age', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Weight (lbs)</label>
              <input
                type="number"
                className="input-field"
                value={formData.weight}
                min="0"
                step="0.1"
                onChange={(e) => handleInputChange('weight', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Height</label>
              <div className="form-row">
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <input
                    type="number"
                    className="input-field"
                    placeholder="Feet"
                    value={formData.heightFeet}
                    min="0"
                    max="8"
                    onChange={(e) => handleInputChange('heightFeet', e.target.value)}
                  />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <input
                    type="number"
                    className="input-field"
                    placeholder="Inches"
                    value={formData.heightInches}
                    min="0"
                    max="11"
                    onChange={(e) => handleInputChange('heightInches', e.target.value)}
                  />
                </div>
              </div>
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <div className="form-group">
              <label>Activity Level</label>
              <select
                className="select-field"
                value={formData.activityLevel}
                onChange={(e) => handleInputChange('activityLevel', e.target.value)}
              >
                <option value="">Select your activity level</option>
                <option value="Sedentary">Sedentary</option>
                <option value="Light">Light</option>
                <option value="Moderate">Moderate</option>
                <option value="Active">Active</option>
                <option value="Very Active">Very Active</option>
              </select>
            </div>
            <div className="form-group">
              <label>Fitness Goal</label>
              <select
                className="select-field"
                value={formData.fitnessGoal}
                onChange={(e) => handleInputChange('fitnessGoal', e.target.value)}
              >
                <option value="">Select your primary goal</option>
                <option value="Weight Loss">Weight Loss</option>
                <option value="Muscle Gain">Muscle Gain</option>
                <option value="Endurance">Endurance</option>
                <option value="General Fitness">General Fitness</option>
              </select>
            </div>
          </>
        )}

        {step === 3 && (
          <>
            <div className="form-group">
              <label>Dietary Preferences</label>
              <select
                className="select-field"
                value={formData.dietaryPreferences}
                onChange={(e) => handleInputChange('dietaryPreferences', e.target.value)}
              >
                <option value="">Select your diet type</option>
                <option value="Omnivore">Omnivore</option>
                <option value="Vegetarian">Vegetarian</option>
                <option value="Vegan">Vegan</option>
                <option value="Keto">Keto</option>
                <option value="Paleo">Paleo</option>
                <option value="Mediterranean">Mediterranean</option>
              </select>
            </div>
            <div className="form-group">
              <label>Meals Per Day</label>
              <select
                className="select-field"
                value={formData.mealsPerDay}
                onChange={(e) => handleInputChange('mealsPerDay', e.target.value)}
              >
                <option value="">Select meals per day</option>
                <option value="2">2 meals</option>
                <option value="3">3 meals</option>
                <option value="4">4 meals</option>
                <option value="5">5 meals</option>
                <option value="6">6 meals</option>
              </select>
            </div>
          </>
        )}

        {/* Navigation Buttons */}
        <div style={{ display: 'flex', gap: '16px', marginTop: '32px', justifyContent: 'space-between' }}>
          {step > 1 && (
            <button className="btn-primary" onClick={handleBack} style={{ flex: 1 }}>
              Back
            </button>
          )}
          <button
            className="btn-primary"
            onClick={handleNext}
            disabled={!isStepValid()}
            style={{
              flex: 1,
              opacity: isStepValid() ? 1 : 0.5,
              cursor: isStepValid() ? 'pointer' : 'not-allowed'
            }}
          >
            {step === 3 ? 'Submit' : 'Next'}
          </button>
        </div>
      </div>

      {/* Footer */}
      <div className="footer">
        <Logo variant="dark" width={110} />
      </div>
    </div>
  )
}

export default LandingPage

