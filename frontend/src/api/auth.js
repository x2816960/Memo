import api from './index'

export const authApi = {
  login(username, password, rememberMe = false) {
    return api.post('/auth/login', { username, password, remember_me: rememberMe })
  },

  register(data) {
    return api.post('/auth/register', data)
  },

  logout() {
    return api.post('/auth/logout')
  },

  getMe() {
    return api.get('/auth/me')
  },

  changePassword(oldPassword, newPassword) {
    return api.put('/auth/password', { old_password: oldPassword, new_password: newPassword })
  },

  adminChangePassword(newPassword, oldPassword = '') {
    return api.put('/auth/password/admin', { old_password: oldPassword, new_password: newPassword })
  }
}
