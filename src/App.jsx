import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import LandingPage from './components/LandingPage'
import Dashboard from './components/Dashboard'
import NutritionDetail from './components/NutritionDetail'
import WorkoutDetail from './components/WorkoutDetail'
import ProgressDetail from './components/ProgressDetail'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/nutrition" element={<NutritionDetail />} />
          <Route path="/workout" element={<WorkoutDetail />} />
          <Route path="/progress" element={<ProgressDetail />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
