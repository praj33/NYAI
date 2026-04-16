// offlineStore.js — Case intake persistence layer (localStorage)
// Priority: Data Preservation over Analysis Results during outages.

const STORE_KEY = 'gravitas_case_intake'
const PENDING_SYNC_KEY = 'gravitas_pending_sync'

export const offlineStore = {
  // Persist current case intake snapshot
  save(data) {
    try {
      localStorage.setItem(STORE_KEY, JSON.stringify({
        ...data,
        _savedAt: Date.now()
      }))
    } catch {
      // Storage quota exceeded — silently fail, data already in memory
    }
  },

  load() {
    try {
      const raw = localStorage.getItem(STORE_KEY)
      return raw ? JSON.parse(raw) : null
    } catch {
      return null
    }
  },

  // Mark current snapshot as pending server sync
  markPendingSync(data) {
    try {
      localStorage.setItem(PENDING_SYNC_KEY, JSON.stringify({
        ...data,
        _pendingSince: Date.now()
      }))
    } catch {}
  },

  getPendingSync() {
    try {
      const raw = localStorage.getItem(PENDING_SYNC_KEY)
      return raw ? JSON.parse(raw) : null
    } catch {
      return null
    }
  },

  clearPendingSync() {
    localStorage.removeItem(PENDING_SYNC_KEY)
  },

  hasPendingSync() {
    return localStorage.getItem(PENDING_SYNC_KEY) !== null
  }
}
