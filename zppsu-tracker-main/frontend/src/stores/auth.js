import { defineStore } from 'pinia'
import { api, SESSION_KEY } from '../lib/api'

function readSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY) || 'null')
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => {
    const session = readSession()
    return { user: session?.user ?? null, token: session?.token ?? null }
  },
  getters: {
    isAuthenticated: (state) => !!state.user && !!state.token,
    role: (state) => state.user?.role ?? null,
    initials: (state) => {
      if (!state.user?.name) return '?'
      return state.user.name
        .split(' ')
        .map((p) => p[0])
        .slice(0, 2)
        .join('')
        .toUpperCase()
    },
    homePath: (state) => {
      switch (state.user?.role) {
        case 'admin': return '/admin/dashboard'
        case 'super-admin': return '/super-admin/dashboard'
        case 'intern': return '/intern/dashboard'
        default: return '/login'
      }
    },
  },
  actions: {
    async login(email, password) {
      const session = await api.post('/api/auth/login', { email, password })
      this.user = session.user
      this.token = session.token
      localStorage.setItem(SESSION_KEY, JSON.stringify(session))
      return this.user
    },
    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem(SESSION_KEY)
    },
  },
})
