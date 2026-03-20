import { defineStore } from 'pinia'
import { authApi } from '@/api/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    token: localStorage.getItem('token') || '',
    isLoggedIn: !!localStorage.getItem('token')
  }),

  getters: {
    isAdmin: (state) => state.user?.role === 'admin',
    mustChangePassword: (state) => state.user?.must_change_password
  },

  actions: {
    async login(username, password, rememberMe = false) {
      const response = await authApi.login(username, password, rememberMe)
      this.token = response.data.access_token
      localStorage.setItem('token', this.token)
      await this.fetchUser()
      return response.data
    },

    async fetchUser() {
      try {
        const response = await authApi.getMe()
        this.user = response.data
        localStorage.setItem('user', JSON.stringify(response.data))
        this.isLoggedIn = true
      } catch (error) {
        this.logout()
        throw error
      }
    },

    async logout() {
      try {
        await authApi.logout()
      } catch (e) {
        // Ignore logout errors
      }
      this.user = null
      this.token = ''
      this.isLoggedIn = false
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },

    async changePassword(oldPassword, newPassword) {
      await authApi.changePassword(oldPassword, newPassword)
      await this.fetchUser()
    },

    async adminChangePassword(newPassword) {
      await authApi.adminChangePassword(newPassword)
      await this.fetchUser()
    }
  }
})
