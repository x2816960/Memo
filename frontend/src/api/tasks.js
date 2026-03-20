import api from './index'

export const taskApi = {
  getTasks(params) {
    return api.get('/tasks', { params })
  },

  getTask(id) {
    return api.get(`/tasks/${id}`)
  },

  createTask(data) {
    return api.post('/tasks', data)
  },

  updateTask(id, data) {
    return api.put(`/tasks/${id}`, data)
  },

  deleteTask(id) {
    return api.delete(`/tasks/${id}`)
  },

  updateTaskStatus(id, status) {
    return api.patch(`/tasks/${id}/status`, { status })
  },

  sortTasks(taskIds) {
    return api.put('/tasks/sort', { task_ids: taskIds })
  },

  getStats() {
    return api.get('/tasks/stats')
  },

  // Attachments
  uploadAttachment(taskId, file) {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/tasks/${taskId}/attachments`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  getAttachments(taskId) {
    return api.get(`/tasks/${taskId}/attachments`)
  },

  deleteAttachment(attachmentId) {
    return api.delete(`/attachments/${attachmentId}`)
  },

  getDownloadUrl(attachmentId) {
    return `/api/attachments/${attachmentId}/download`
  }
}
