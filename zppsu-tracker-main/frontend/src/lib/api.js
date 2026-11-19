// Thin fetch wrapper for the GeoTrack FastAPI backend.
// Set VITE_API_URL (e.g. in frontend/.env.local) when the API is not on localhost:8000.

export const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')
export const SESSION_KEY = 'geotrack.session'

let onUnauthorized = () => {}
export function setUnauthorizedHandler(fn) {
  onUnauthorized = fn
}

function token() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY) || 'null')?.token || null
  } catch {
    return null
  }
}

function messageFrom(body, status) {
  const detail = body?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length) {
    // FastAPI validation errors: [{ loc: ['body', 'password'], msg: '...' }]
    return detail.map((d) => `${(d.loc || []).filter((p) => p !== 'body').join('.')}: ${d.msg}`).join('; ')
  }
  return `Request failed (${status})`
}

async function request(method, path, body) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  const t = token()
  if (t) headers.Authorization = `Bearer ${t}`

  let res
  try {
    res = await fetch(`${API_URL}${path}`, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) })
  } catch {
    throw new Error('Cannot reach the server. Check your connection and that the API is running.')
  }

  if (res.status === 204) return null
  const data = await res.json().catch(() => null)
  if (!res.ok) {
    // A 401 on /auth/login just means wrong credentials; anywhere else it means the session expired.
    if (res.status === 401 && !path.startsWith('/api/auth/login')) onUnauthorized()
    throw new Error(messageFrom(data, res.status))
  }
  return data
}

export const api = {
  get: (path) => request('GET', path),
  post: (path, body) => request('POST', path, body ?? {}),
  put: (path, body) => request('PUT', path, body),
  patch: (path, body) => request('PATCH', path, body),
  delete: (path) => request('DELETE', path),
}
