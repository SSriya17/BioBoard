import React from 'react'
import { useNavigate } from 'react-router-dom'
import Logo from './Logo'

function Header({ variant = 'light', circular = false }) {
  const navigate = useNavigate()

  const handleLogoClick = () => {
    navigate('/')
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10, marginBottom: 24 }}>
      <div 
        onClick={handleLogoClick}
        style={{ 
          cursor: 'pointer',
          transition: 'opacity 0.2s ease'
        }}
        onMouseEnter={(e) => e.currentTarget.style.opacity = '0.8'}
        onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
      >
        <Logo variant={variant} width={150} circular={circular} />
      </div>
    </div>
  )
}

export default Header


