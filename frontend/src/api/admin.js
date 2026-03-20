import api from './index'

export const adminApi = {
  getUsers() {
    return api.get('/admin/users')
  },

  toggleUserStatus(userId, enabled) {
    return api.patch(`/admin/users/${userId}`, null, { params: { enabled } })
  },

  resetUserPassword(userId, newPassword) {
    return api.post(`/admin/users/${userId}/reset-password`, null, { params: { new_password: newPassword } })
  },

  getSystemStats() {
    return api.get('/admin/stats')
  },

  getConfig() {
    return api.get('/admin/config')
  },

  updateConfig(data) {
    return api.put('/admin/config', data)
  }
}
