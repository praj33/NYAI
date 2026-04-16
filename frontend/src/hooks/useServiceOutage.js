// useServiceOutage.js — React hook to subscribe to backend service outage state
// Returns isServiceOutage flag and error details when backend is down
import { useState, useEffect } from 'react'
import { onServiceOutage, isBackendOutage, clearServiceOutage } from '../services/nyayaApi.js'

/**
 * Hook to detect and respond to backend service outages
 * 
 * @returns {{
 *   isServiceOutage: boolean,
 *   outageError: { status?: number, message?: string, trace_id?: string } | null,
 *   clearOutage: () => void
 * }}
 */
export function useServiceOutage() {
  const [isServiceOutage, setIsServiceOutage] = useState(() => isBackendOutage())
  const [outageError, setOutageError] = useState(null)

  useEffect(() => {
    // Subscribe to service outage events from global interceptor
    const unsubscribe = onServiceOutage(({ isOutage, error }) => {
      setIsServiceOutage(isOutage)
      setOutageError(isOutage ? error : null)
    })

    return unsubscribe
  }, [])

  const clearOutage = () => {
    clearServiceOutage()
  }

  return {
    isServiceOutage,
    outageError,
    clearOutage
  }
}

export default useServiceOutage
