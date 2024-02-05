import { useAuthStore } from '@/stores/auth.store'

const baseUrl = `${import.meta.env.VITE_API_URL || ''}`

export const fetchWrapper = {
  get: request('GET'),
  post: request('POST'),
  put: request('PUT'),
  delete: request('DELETE')
}

function request(method) {
  return (url, body) => {
    const requestOptions = {
      method,
      headers: authHeader()
    }
    if (body) {
      requestOptions.headers['Content-Type'] = 'application/json'
      requestOptions.body = JSON.stringify(body)
    }
    return fetch(`${baseUrl}${url}`, requestOptions).then(handleResponse)
  }
}

// helper functions

function authHeader() {
  // return auth header with jwt if user is logged in and request is to the api url
  const { credentials } = useAuthStore()
  const isLoggedIn = !!credentials?.access
  if (isLoggedIn) {
    return { Authorization: `Bearer ${credentials.access}` }
  } else {
    return {}
  }
}

function handleResponse(response) {
  if (!response.ok) {
    const { user, logout } = useAuthStore()
    if (response.status === 401 && user) {
      logout()
    }
  }
  return response
}
