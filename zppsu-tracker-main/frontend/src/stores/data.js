import { defineStore } from 'pinia'
import { api } from '../lib/api'
import { useAuthStore } from './auth'

const emptyState = () => ({
  organizations: [],
  admins: [],
  programs: [],
  locations: [],
  interns: [],
  attendanceRecords: [],
  failedAttempts: [],
  dailyLogs: [],
  evaluations: [],
  auditLogs: [],
  notifications: [],
  overview: null, // super-admin platform stats
  currentInternId: null,
  loading: false,
  loaded: false,
  loadError: '',
})

// Swap a row in-place by id (or add it when new) so views holding the array stay reactive.
function upsert(list, row, { prepend = false } = {}) {
  const i = list.findIndex((r) => r.id === row.id)
  if (i >= 0) list[i] = row
  else if (prepend) list.unshift(row)
  else list.push(row)
}

export const useDataStore = defineStore('data', {
  state: emptyState,
  getters: {
    currentIntern: (state) => state.interns.find((i) => i.id === state.currentInternId),
    unreadNotifications: (state) => state.notifications.filter((n) => !n.read).length,
    internAttendance: (state) => (internId) => state.attendanceRecords.filter((a) => a.internId === internId).sort((a, b) => b.timestamp.localeCompare(a.timestamp)),
    internLogs: (state) => (internId) => state.dailyLogs.filter((l) => l.internId === internId).sort((a, b) => b.date.localeCompare(a.date)),
    internEvaluations: (state) => (internId) => state.evaluations.filter((e) => e.internId === internId),
    pendingApplications: (state) => state.interns.filter((i) => i.applicationStatus === 'Pending'),
    pendingLogs: (state) => state.dailyLogs.filter((l) => l.status === 'Pending'),
    orgLocations: (state) => (orgId) => state.locations.filter((l) => l.orgId === orgId),
    orgInterns: (state) => (orgId) => state.interns.filter((i) => i.orgId === orgId),
  },
  actions: {
    reset() {
      Object.assign(this, emptyState())
    },

    /** Load everything the signed-in role needs from the API into the store. */
    async load() {
      const auth = useAuthStore()
      if (!auth.user) return
      this.loading = true
      this.loadError = ''
      try {
        if (auth.role === 'intern') await this._loadIntern(auth.user.id)
        else if (auth.role === 'admin') await this._loadAdmin()
        else if (auth.role === 'super-admin') await this._loadSuperAdmin()
        this.loaded = true
      } catch (e) {
        this.loadError = e.message
      } finally {
        this.loading = false
      }
    },

    async _loadIntern(userId) {
      const [profile, attendance, failed, logs, evaluations, notifications] = await Promise.all([
        api.get('/api/intern/profile'),
        api.get('/api/intern/attendance'),
        api.get('/api/intern/failed-attempts'),
        api.get('/api/intern/daily-logs'),
        api.get('/api/intern/evaluations'),
        api.get('/api/intern/notifications'),
      ])
      this.currentInternId = userId
      this.interns = [profile.intern]
      this.organizations = profile.organization ? [profile.organization] : []
      this.programs = profile.program ? [profile.program] : []
      this.locations = profile.locations
      this.attendanceRecords = attendance
      this.failedAttempts = failed
      this.dailyLogs = logs
      this.evaluations = evaluations
      this.notifications = notifications
    },

    async _loadAdmin() {
      const [interns, attendance, failed, logs, evaluations, locations, audit] = await Promise.all([
        api.get('/api/admin/interns'),
        api.get('/api/admin/attendance'),
        api.get('/api/admin/failed-attempts'),
        api.get('/api/admin/daily-logs'),
        api.get('/api/admin/evaluations'),
        api.get('/api/admin/locations'),
        api.get('/api/admin/audit-logs'),
      ])
      Object.assign(this, {
        interns, attendanceRecords: attendance, failedAttempts: failed, dailyLogs: logs, evaluations, locations, auditLogs: audit,
      })
    },

    async _loadSuperAdmin() {
      const [overview, organizations, admins, interns, audit] = await Promise.all([
        api.get('/api/super-admin/overview'),
        api.get('/api/super-admin/organizations'),
        api.get('/api/super-admin/admins'),
        api.get('/api/super-admin/applications'),
        api.get('/api/super-admin/audit-logs'),
      ])
      Object.assign(this, { overview, organizations, admins, interns, auditLogs: audit })
    },

    async refreshAuditLogs() {
      const auth = useAuthStore()
      if (auth.role === 'super-admin') this.auditLogs = await api.get('/api/super-admin/audit-logs')
      else if (auth.role === 'admin') this.auditLogs = await api.get('/api/admin/audit-logs')
    },

    /** After a super-admin write: refresh the derived numbers and the audit feed (best effort). */
    async _syncSuper() {
      try {
        const [overview, organizations, audit] = await Promise.all([
          api.get('/api/super-admin/overview'),
          api.get('/api/super-admin/organizations'),
          api.get('/api/super-admin/audit-logs'),
        ])
        Object.assign(this, { overview, organizations, auditLogs: audit })
      } catch { /* the write itself succeeded; the next full load will catch up */ }
    },

    // ---- OJT trainee --------------------------------------------------------------------

    async submitDailyLog(entry) {
      const log = await api.post('/api/intern/daily-logs', entry)
      upsert(this.dailyLogs, log, { prepend: true })
      return log
    },

    /** Time In / Time Out. The server validates the geofence and decides which one it is. */
    async clock({ locationId, latitude, longitude, method }) {
      try {
        const record = await api.post('/api/intern/attendance', { locationId, latitude, longitude, method })
        upsert(this.attendanceRecords, record, { prepend: true })
        const profile = await api.get('/api/intern/profile') // refreshed rendered hours
        this.interns = [profile.intern]
        return record
      } catch (e) {
        this.failedAttempts = await api.get('/api/intern/failed-attempts').catch(() => this.failedAttempts)
        throw e
      }
    },

    async markNotificationsRead() {
      const auth = useAuthStore()
      if (auth.role !== 'intern' || !this.unreadNotifications) return
      this.notifications.forEach((n) => (n.read = true))
      await api.post('/api/intern/notifications/read').catch(() => {})
    },

    // ---- Admin --------------------------------------------------------------------------

    async reviewDailyLog(logId, status, comment) {
      const log = await api.post(`/api/admin/daily-logs/${logId}/review`, { status, comment: comment || '' })
      upsert(this.dailyLogs, log)
      return log
    },

    async addEvaluation(payload) {
      const ev = await api.post('/api/admin/evaluations', payload)
      upsert(this.evaluations, ev, { prepend: true })
      return ev
    },

    async addLocation(loc) {
      const row = await api.post('/api/admin/locations', { status: 'Active', ...loc })
      upsert(this.locations, row)
      return row
    },
    async updateLocation(id, patch) {
      const current = this.locations.find((l) => l.id === id)
      const row = await api.put(`/api/admin/locations/${id}`, { ...current, ...patch })
      upsert(this.locations, row)
      return row
    },
    async removeLocation(id) {
      await api.delete(`/api/admin/locations/${id}`)
      this.locations = this.locations.filter((l) => l.id !== id)
    },

    // ---- Super admin --------------------------------------------------------------------

    async approveApplication(internId, orgId) {
      const row = await api.post(`/api/super-admin/applications/${internId}/approve`, { orgId })
      upsert(this.interns, row)
      await this._syncSuper()
      return row
    },
    async deployIntern(internId, orgId) {
      const row = await api.post(`/api/super-admin/applications/${internId}/deploy`, { orgId })
      upsert(this.interns, row)
      await this._syncSuper()
      return row
    },
    async rejectApplication(internId) {
      const row = await api.post(`/api/super-admin/applications/${internId}/reject`)
      upsert(this.interns, row)
      await this._syncSuper()
      return row
    },

    async addOrganization(org) {
      const row = await api.post('/api/super-admin/organizations', org)
      upsert(this.organizations, row)
      await this._syncSuper()
      return row
    },
    async updateOrganization(id, patch) {
      const current = this.organizations.find((o) => o.id === id)
      const row = await api.put(`/api/super-admin/organizations/${id}`, {
        name: current.name, address: current.address || '', status: current.status, ...patch,
      })
      upsert(this.organizations, row)
      await this._syncSuper()
      return row
    },

    async addAdmin(admin) {
      const row = await api.post('/api/super-admin/admins', admin)
      upsert(this.admins, row)
      await this._syncSuper()
      return row
    },
  },
})
