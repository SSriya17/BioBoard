import { useEffect, useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from './Header'
import Logo from './Logo'
import '../App.css'
import { getProgressForecast } from '../services/api'

// Simple projection logic: estimate weekly change from goal and activity
function useProjection(user) {
  return useMemo(() => {
    const weight = parseFloat(user.weight) || 165
    const goal = user.fitnessGoal || 'General Fitness'
    const activity = user.activityLevel || 'Moderate'
    const weeks = 12

    // base weekly delta in pounds (placeholder until ML model)
    const base = {
      'Weight Loss': -0.75,
      'Muscle Gain': 0.35,
      'Endurance': -0.25,
      'General Fitness': -0.10,
    }[goal] ?? -0.10

    const activityAdj = {
      Sedentary: 0.8,
      Light: 0.9,
      Moderate: 1.0,
      Active: 1.1,
      'Very Active': 1.2,
    }[activity] ?? 1.0

    const weeklyDelta = base * activityAdj

    const points = Array.from({ length: weeks + 1 }, (_, i) => ({
      week: i,
      weight: +(weight + weeklyDelta * i).toFixed(1),
    }))

    return { weeklyDelta, points }
  }, [user])
}

function ProgressDetail() {
  const [userData, setUserData] = useState(null)
  const [forecastData, setForecastData] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    const data = localStorage.getItem('userData')
    if (data) {
      const parsed = JSON.parse(data)
      setUserData(parsed)
      loadProgressForecast(parsed)
    } else {
      navigate('/')
    }
  }, [navigate])

  const loadProgressForecast = async (userData) => {
    setLoading(true)
    try {
      const apiForecast = await getProgressForecast(
        userData.weight,
        userData.fitnessGoal || 'General Fitness',
        userData.activityLevel || 'Moderate',
        12
      )
      
      if (apiForecast && apiForecast.points) {
        setForecastData(apiForecast)
      } else {
        // Fallback to frontend projection
        const weight = parseFloat(userData.weight) || 165
        const goal = userData.fitnessGoal || 'General Fitness'
        const activity = userData.activityLevel || 'Moderate'
        const weeks = 12
        
        const base = {
          'Weight Loss': -0.75,
          'Muscle Gain': 0.35,
          'Endurance': -0.25,
          'General Fitness': -0.10,
        }[goal] ?? -0.10
        
        const activityAdj = {
          Sedentary: 0.8,
          Light: 0.9,
          Moderate: 1.0,
          Active: 1.1,
          'Very Active': 1.2,
        }[activity] ?? 1.0
        
        const weeklyDelta = base * activityAdj
        const points = Array.from({ length: weeks + 1 }, (_, i) => ({
          week: i,
          weight: +(weight + weeklyDelta * i).toFixed(1),
        }))
        
        setForecastData({ weeklyDelta, points })
      }
    } catch (error) {
      console.error('Error loading progress forecast:', error)
      // Fallback to frontend projection
      const weight = parseFloat(userData.weight) || 165
      const goal = userData.fitnessGoal || 'General Fitness'
      const activity = userData.activityLevel || 'Moderate'
      const weeks = 12
      
      const base = {
        'Weight Loss': -0.75,
        'Muscle Gain': 0.35,
        'Endurance': -0.25,
        'General Fitness': -0.10,
      }[goal] ?? -0.10
      
      const activityAdj = {
        Sedentary: 0.8,
        Light: 0.9,
        Moderate: 1.0,
        Active: 1.1,
        'Very Active': 1.2,
      }[activity] ?? 1.0
      
      const weeklyDelta = base * activityAdj
      const points = Array.from({ length: weeks + 1 }, (_, i) => ({
        week: i,
        weight: +(weight + weeklyDelta * i).toFixed(1),
      }))
      
      setForecastData({ weeklyDelta, points })
    } finally {
      setLoading(false)
    }
  }

  if (!userData || loading) return <div>Loading...</div>
  if (!forecastData) return <div>Error loading progress forecast</div>

  const { weeklyDelta, points } = forecastData

  // Prepare a lightweight SVG chart (no external deps)
  const Chart = () => {
    const width = 900
    const height = 260
    const padding = { top: 20, right: 20, bottom: 30, left: 50 }
    const innerW = width - padding.left - padding.right
    const innerH = height - padding.top - padding.bottom
    const xs = points.map(p => p.week)
    const ys = points.map(p => p.weight)
    const xMin = Math.min(...xs)
    const xMax = Math.max(...xs)
    const yMin = Math.min(...ys)
    const yMax = Math.max(...ys)
    const xScale = (x) => padding.left + ((x - xMin) / (xMax - xMin)) * innerW
    const yScale = (y) => padding.top + innerH - ((y - yMin) / (yMax - yMin || 1)) * innerH
    const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${xScale(p.week)} ${yScale(p.weight)}`).join(' ')
    const yTicks = 4
    const yTickVals = Array.from({ length: yTicks + 1 }, (_, i) => +(yMin + (i * (yMax - yMin)) / yTicks).toFixed(1))
    const xTickVals = [0, 3, 6, 9, 12]
    const [hoverIdx, setHoverIdx] = useState(null)
    const tooltip = hoverIdx != null ? points[hoverIdx] : null

    return (
      <svg viewBox={`0 0 ${width} ${height}`} width="100%" height="260">
        <rect x="0" y="0" width={width} height={height} fill="transparent" />
        {/* Axes */}
        <line x1={padding.left} y1={padding.top} x2={padding.left} y2={height - padding.bottom} stroke="rgba(255,255,255,0.4)" />
        <line x1={padding.left} y1={height - padding.bottom} x2={width - padding.right} y2={height - padding.bottom} stroke="rgba(255,255,255,0.4)" />
        {/* Grid + Y ticks */}
        {yTickVals.map((v, i) => {
          const y = yScale(v)
          return (
            <g key={i}>
              <line x1={padding.left} y1={y} x2={width - padding.right} y2={y} stroke="rgba(255,255,255,0.1)" />
              <text x={padding.left - 8} y={y} fill="rgba(255,255,255,0.7)" fontSize="12" textAnchor="end" dominantBaseline="middle">
                {v}
              </text>
            </g>
          )
        })}
        {/* X ticks */}
        {xTickVals.map((v, i) => {
          const x = xScale(v)
          return (
            <g key={i}>
              <line x1={x} y1={height - padding.bottom} x2={x} y2={height - padding.bottom + 6} stroke="rgba(255,255,255,0.4)" />
              <text x={x} y={height - padding.bottom + 18} fill="rgba(255,255,255,0.7)" fontSize="12" textAnchor="middle">
                wk {v}
              </text>
            </g>
          )
        })}
        {/* Line path */}
        <path d={pathD} fill="none" stroke="#4A90E2" strokeWidth="3" />
        {/* Points */}
        {points.map((p, i) => {
          const cx = xScale(p.week)
          const cy = yScale(p.weight)
          const isHovered = hoverIdx === i
          return (
            <g key={i}>
              {/* Larger invisible hover target */}
              <circle
                cx={cx}
                cy={cy}
                r="10"
                fill="transparent"
                onMouseEnter={() => setHoverIdx(i)}
                onMouseLeave={() => setHoverIdx((cur) => (cur === i ? null : cur))}
              />
              <circle cx={cx} cy={cy} r={isHovered ? "6" : "3"} fill="#4A90E2" />
            </g>
          )
        })}
        {/* Tooltip */}
        {tooltip && (
          <g>
            {(() => {
              const tx = xScale(tooltip.week)
              const ty = yScale(tooltip.weight)
              const label = `Week ${tooltip.week} • ${tooltip.weight} lb`
              const bgX = Math.min(Math.max(tx - 60, padding.left + 4), width - padding.right - 120)
              const bgY = Math.max(ty - 40, padding.top + 4)
              return (
                <>
                  <line x1={tx} y1={ty} x2={tx} y2={height - padding.bottom} stroke="rgba(74,144,226,0.4)" strokeDasharray="4 4" />
                  <rect x={bgX} y={bgY} width="220" height="50" rx="4" fill="rgba(0,0,0,0.85)" stroke="rgba(255,255,255,0.2)" />
                  <text x={bgX + 12} y={bgY + 32} fill="#ffffff" fontSize="28" fontWeight="700">{label}</text>
                </>
              )
            })()}
          </g>
        )}
      </svg>
    )
  }

  return (
    <div style={{ minHeight: '100vh', padding: '40px 20px 160px 20px', maxWidth: 1000, margin: '0 auto' }}>
      <div className="page-header">
        <Header variant="light" />
        <h1>PERSONALIZED HEALTH</h1>
      </div>

      <button className="btn-primary" onClick={() => navigate('/dashboard')} style={{ marginBottom: 32 }}>
        ← Back to Dashboard
      </button>

      <div className="form-container fade-in" style={{ marginBottom: 24 }}>
        <h2 style={{ marginBottom: 12, fontSize: 24, fontWeight: 600 }}>12-Week Projection</h2>
        <div style={{ color: 'rgba(255,255,255,0.8)' }}>
          Estimated weekly change: <strong>{weeklyDelta > 0 ? '+' : ''}{weeklyDelta.toFixed(2)} lb/week</strong>
        </div>
      </div>

      <div className="form-container fade-in" style={{ marginBottom: 24 }}>
        <Chart />
      </div>

      <div className="form-container scale-in" style={{ paddingBottom: '48px', marginBottom: '40px' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', padding: '8px 6px', borderBottom: '1px solid rgba(255,255,255,0.2)' }}>Week</th>
                <th style={{ textAlign: 'left', padding: '8px 6px', borderBottom: '1px solid rgba(255,255,255,0.2)' }}>Projected Weight (lb)</th>
              </tr>
            </thead>
            <tbody>
              {points.map((p) => (
                <tr key={p.week}>
                  <td style={{ padding: '8px 6px' }}>{p.week}</td>
                  <td style={{ padding: '8px 6px' }}>{p.weight}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="footer">
        <Logo variant="dark" width={110} />
      </div>
    </div>
  )
}

export default ProgressDetail


