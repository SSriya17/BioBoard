import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from './Header'
import '../App.css'

function LandingPage() {
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    age: '',
    weight: '',
    heightFeet: '',
    heightInches: '',
    activityLevel: '',
    fitnessGoal: '',
    dietaryPreferences: '',
    mealsPerDay: ''
  })
  const navigate = useNavigate()

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleNext = () => {
    if (step < 3) {
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

  return (
    <div style={{ minHeight: '100vh', padding: '40px 20px 100px 20px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      {/* Header */}
      <div className="page-header">
        <Header variant="light" />
        <h1>PERSONALIZED HEALTH</h1>
      </div>

      {/* Step Indicator */}
      <div className="step-indicator">Step {step} of 3</div>
      <div className="step-divider"></div>

      {/* Form Container */}
      <div className="form-container">
        {step === 1 && (
          <>
            <div className="form-group">
              <label>Age</label>
              <input
                type="number"
                className="input-field"
                placeholder="ageinput"
                value={formData.age}
                onChange={(e) => handleInputChange('age', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Weight</label>
              <input
                type="number"
                className="input-field"
                placeholder="weightinput"
                value={formData.weight}
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
                    placeholder="feet"
                    value={formData.heightFeet}
                    onChange={(e) => handleInputChange('heightFeet', e.target.value)}
                  />
                </div>
                <div className="form-group" style={{ marginBottom: 0 }}>
                  <input
                    type="number"
                    className="input-field"
                    placeholder="inches"
                    value={formData.heightInches}
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
        <Header variant="dark" />
      </div>
    </div>
  )
}

export default LandingPage

