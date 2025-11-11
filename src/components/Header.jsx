import React from 'react'
import Logo from './Logo'

function Header({ variant = 'light', circular = false }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, marginBottom: 24 }}>
      <Logo variant={variant} width={160} circular={circular} />
    </div>
  )
}

export default Header


