const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const TOKEN_KEY = 'demo-showcase-admin-token'

function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

function setToken(token) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {})
  const token = getToken()

  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  })

  if (!response.ok) {
    let detail = 'An error occurred.'
    try {
      const data = await response.json()
      detail = data.detail || detail
    } catch {
      // ignore
    }
    if (response.status === 401) {
      setToken(null)
    }
    throw new Error(detail)
  }

  if (response.status === 204) {
    return null
  }

  return response.json()
}

export const api = {
  getApiBase() {
    return API_BASE
  },
  getToken,
  isAuthenticated() {
    return !!getToken()
  },
  logout() {
    setToken(null)
  },
  async login(username, password) {
    const data = await request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    })
    setToken(data.access_token)
    return data
  },
  listDemos(tag) {
    const query = tag ? `?tag=${encodeURIComponent(tag)}` : ''
    return request(`/api/demos${query}`)
  },
  listAdminDemos() {
    return request('/api/admin/demos')
  },
  listTags() {
    return request('/api/tags')
  },
  createDemo(payload) {
    return request('/api/demos', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
  },
  updateDemo(id, payload) {
    return request(`/api/demos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    })
  },
  updateDemoVisibility(id, isVisible) {
    return request(`/api/demos/${id}/visibility`, {
      method: 'PATCH',
      body: JSON.stringify({ is_visible: isVisible })
    })
  },
  deleteDemo(id) {
    return request(`/api/demos/${id}`, {
      method: 'DELETE'
    })
  },
  uploadImage(file) {
    const formData = new FormData()
    formData.append('file', file)
    return request('/api/upload-image', {
      method: 'POST',
      body: formData
    })
  }
}