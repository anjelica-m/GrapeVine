import { defineStore } from 'pinia'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import router from '@/router'

export const useAuthStore = defineStore({
  id: 'auth',
  state: () => ({
    credentials: null,
    returnUrl: null,
    tokenRefreshInterval: null,
    user: null
  }),
  actions: {
    setup() {
      this.credentials = JSON.parse(localStorage.getItem('credentials'))
      if (this.authenticated) {
        this.startTokenRefreshInterval()
      }
      this.initializeUser()
    },
    async login(username, password) {
      const resp = await fetchWrapper.post(`/api/local/token/`, { username, password })
      if (!resp.ok) {
        throw new Error('Invalid username or password')
      }
      const credentials = await resp.json()
      this.credentials = credentials
      localStorage.setItem('credentials', JSON.stringify(credentials))
      await this.fetchUserData()
      router.push(this.returnUrl || '/')
      this.startTokenRefreshInterval()
    },
    async initializeUser() {
      if (this.authenticated && this.credentials) {
        await this.fetchUserData()
      }
    },
    async fetchUserData() {
      if (!this.credentials) {
        console.error('No credentials available')
        return
      }
      const response = await fetchWrapper.get(`/api/local/users/me/`, null)
      this.user = await response.json()
    },
    async refreshToken() {
      try {
        const response = await fetchWrapper.post(`/api/local/token/refresh/`, {
          refresh: this.credentials.refresh
        })
        const data = await response.json()
        this.credentials.access = data.access
        localStorage.setItem('credentials', JSON.stringify(this.credentials))
      } catch (error) {
        console.error('Error refreshing token:', error)
        this.logout()
      }
    },
    startTokenRefreshInterval() {
      // Clear existing interval if any
      if (this.tokenRefreshInterval) {
        clearInterval(this.tokenRefreshInterval)
      }

      // Set up a new interval
      this.tokenRefreshInterval = setInterval(async () => {
        if (this.isAccessTokenAlmostExpired()) {
          await this.refreshToken()
        }
      }, 60000) // Check every minute
    },
    isAccessTokenAlmostExpired() {
      const accessToken = this.credentials?.access
      if (!accessToken) return true

      const payload = JSON.parse(atob(accessToken.split('.')[1]))
      const now = Date.now() / 1000
      const timeLeft = payload.exp - now
      return timeLeft < 120 // less than 2 minutes remaining
    },
    logout() {
      this.credentials = null
      this.user = null
      localStorage.removeItem('credentials')
      clearInterval(this.tokenRefreshInterval)
      router.push('/login')
    }
  },
  getters: {
    authenticated(state) {
      return !!state.credentials
    },
    currentUser(state) {
      return state.user
    },
    githubUsername(state) {
      const gh = state.user?.author?.github
      if (!gh) return null
      return gh.replace('https://github.com/', '')
    }
  }
})
