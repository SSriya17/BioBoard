import React from 'react'

function Logo({ variant = 'light', width = 180 }) {
  // variant: 'light' => white on dark backgrounds (invert)
  // variant: 'dark' => dark on light backgrounds (original colors)
  const isLight = variant === 'light'
  return (
    <div className="logo" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <img
        src="/bioboard-logo.png"
        alt="BioBoard"
        style={{
          width,
          height: 'auto',
          // Invert for white-on-black header
          filter: isLight ? 'invert(1) hue-rotate(180deg) saturate(0)' : 'none',
        }}
      />
    </div>
  )
}

export default Logo


