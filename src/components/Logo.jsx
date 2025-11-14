import React, { useState, useCallback } from 'react'

function Logo({ variant = 'light', width = 260, circular = false }) {
  // Render exactly the provided image. Place your file at public/logo-wave.png
  const [srcIndex, setSrcIndex] = useState(0)
  
  // Use different logo sources based on variant
  // Light variant (header) uses inverted-logo-color.png, dark variant (footer) uses inverted-logo-color.png
  const lightSources = [
    '/inverted-logo-color.png',
    '/BioBoard Logo.png',
    '/logo-wave.png',
    '/bioboard-logo.png',
    '/logo-wave.svg',
    '/logo.png',
    '/bioboard.jpg',
  ]
  
  const darkSources = [
    '/inverted-logo-color.png',
    '/bioboard.png',
    '/logo-wave.png',
    '/bioboard-logo.png',
    '/logo-wave.svg',
    '/logo.png',
    '/bioboard.jpg',
  ]
  
  const sources = variant === 'dark' ? darkSources : lightSources
  const src = sources[srcIndex] || sources[0]
  const [hidden, setHidden] = useState(false)

  const handleError = useCallback(() => {
    // Try next candidate filename
    setSrcIndex((i) => {
      const currentSources = variant === 'dark' ? darkSources : lightSources
      const next = i + 1
      if (next >= currentSources.length) {
        setHidden(true)
      }
      return next
    })
  }, [variant])

  return (
    <div className="logo" style={{ display: 'inline-flex', alignItems: 'center' }}>
      <img
        src={src}
        alt=""
        style={{
          width,
          height: circular ? width : 'auto',
          display: hidden ? 'none' : 'block',
          objectFit: circular ? 'cover' : 'contain',
          borderRadius: circular ? '50%' : 0,
          // Show the image exactly as provided; no color transforms
          filter: 'none',
        }}
        onError={handleError}
      />
    </div>
  )
}

export default Logo


