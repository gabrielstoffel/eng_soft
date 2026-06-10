// Lightweight admin-auth helpers: token storage + an authenticated fetch wrapper.

const TOKEN_KEY = 'sigbah_admin_token'
const USER_KEY = 'sigbah_admin_user'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function getUser() {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function setSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function isAuthenticated() {
  return !!getToken()
}

const PPG_LABELS = { ppgfis: 'PPGFís', ppgenfis: 'PPGEnFis' }
export function ppgLabel(ppg) {
  return PPG_LABELS[ppg] || ppg
}

// fetch() wrapper that attaches the bearer token. On 401 it clears the session
// and bounces to the login page (the caller's promise rejects).
export async function apiFetch(url, options = {}) {
  const token = getToken()
  const headers = { ...(options.headers || {}) }
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(url, { ...options, headers })
  if (res.status === 401) {
    clearSession()
    if (window.location.pathname !== '/admin/login') {
      window.location.assign('/admin/login')
    }
    throw new Error('Sessão expirada. Faça login novamente.')
  }
  return res
}
