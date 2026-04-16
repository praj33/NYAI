import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// Hide loading overlay when React app is ready
window.addEventListener('load', () => {
  const loadingOverlay = document.getElementById('loading-overlay')
  if (loadingOverlay) {
    setTimeout(() => {
      loadingOverlay.classList.add('hidden')
    }, 500)
  }
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)