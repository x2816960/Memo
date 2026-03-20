import { defineStore } from 'pinia'
import { taskApi } from '@/api/tasks'

export const useTaskStore = defineStore('task', {
  state: () => ({
    tasks: [],
    total: 0,
    page: 1,
    pageSize: 20,
    pages: 0,
    stats: {
      total: 0,
      todo: 0,
      in_progress: 0,
      completed: 0,
      cancelled: 0,
      due_today: 0,
      overdue: 0
    },
    filters: {
      status: null,
      priority: null,
      search: ''
    }
  }),

  actions: {
    async fetchTasks() {
      const params = {
        page: this.page,
        page_size: this.pageSize,
        ...this.filters
      }
      const response = await taskApi.getTasks(params)
      this.tasks = response.data.tasks
      this.total = response.data.total
      this.pages = response.data.pages
    },

    async fetchStats() {
      const response = await taskApi.getStats()
      this.stats = response.data
    },

    async createTask(data) {
      await taskApi.createTask(data)
      await this.fetchTasks()
      await this.fetchStats()
    },

    async updateTask(id, data) {
      await taskApi.updateTask(id, data)
      await this.fetchTasks()
      await this.fetchStats()
    },

    async deleteTask(id) {
      await taskApi.deleteTask(id)
      await this.fetchTasks()
      await this.fetchStats()
    },

    async updateTaskStatus(id, status) {
      await taskApi.updateTaskStatus(id, status)
      await this.fetchTasks()
      await this.fetchStats()
    },

    async sortTasks(taskIds) {
      await taskApi.sortTasks(taskIds)
    },

    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
      this.page = 1
    },

    setPage(page) {
      this.page = page
    },

    setPageSize(pageSize) {
      this.pageSize = pageSize
      this.page = 1
    }
  }
})
