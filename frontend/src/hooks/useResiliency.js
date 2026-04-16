// useResiliency.js — Degraded mode state, failure detection, recovery polling
import { useState, useEffect, useCallback, useRef } from 'react'
import { offlineStore } from '../services/offlineStore.js'
import { healthService, onBackendFailure } from '../services/nyayaApi.js'

const POLL_INTERVAL_MS = 15000 // probe every 15s while offline

export function useResiliency(caseIntakeRef) {
  const [isOffline, setIsOffline] = useState(false)
  const [isSyncing, setIsSyncing] = useState(false)
  const [hasPending, setHasPending] = useState(() => offlineStore.hasPendingSync())
  const pollRef = useRef(null)

  // Subscribe to global interceptor failure events
  useEffect(() => {
    const unsubscribe = onBackendFailure(() => {
      setIsOffline(true)
      const snapshot = caseIntakeRef?.current
      if (snapshot) {
        offlineStore.save(snapshot)
        offlineStore.markPendingSync(snapshot)
        setHasPending(true)
      }
    })
    return unsubscribe
  }, [caseIntakeRef])

  // Persist case intake data continuously during active sessions
  const persistIntake = useCallback((data) => {
    offlineStore.save(data)
  }, [])

  // Probe /health to detect recovery
  const probeHealth = useCallback(async () => {
    const result = await healthService.checkHealth()
    if (result.success) {
      setIsOffline(false)
    }
  }, [])

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current)
      pollRef.current = null
    }
  }, [])

  // Start polling when offline, stop when recovered
  useEffect(() => {
    if (isOffline) {
      pollRef.current = setInterval(probeHealth, POLL_INTERVAL_MS)
    } else {
      stopPolling()
    }
    return stopPolling
  }, [isOffline, probeHealth, stopPolling])

  // Sync pending case data to server once back online
  const syncToServer = useCallback(async (submitFn) => {
    const pending = offlineStore.getPendingSync()
    if (!pending || !submitFn) return

    setIsSyncing(true)
    try {
      await submitFn(pending)
      offlineStore.clearPendingSync()
      setHasPending(false)
    } finally {
      setIsSyncing(false)
    }
  }, [])

  return {
    isOffline,
    isSyncing,
    hasPending,
    persistIntake,
    syncToServer,
    restoredIntake: offlineStore.load()
  }
}
