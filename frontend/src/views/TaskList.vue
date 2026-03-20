<template>
  <div class="task-page">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <h1 class="logo">Memo</h1>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            {{ userStore.user?.nickname || userStore.user?.username }}
            <el-icon><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="settings">个人设置</el-dropdown-item>
              <template v-if="userStore.isAdmin">
                <el-dropdown-item command="admin-stats" divided>统计中心</el-dropdown-item>
                <el-dropdown-item command="admin-users">用户管理</el-dropdown-item>
                <el-dropdown-item command="admin-config">系统配置</el-dropdown-item>
              </template>
              <el-dropdown-item command="logout" :divided="!userStore.isAdmin">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Stats Cards -->
      <div class="stats-cards">
        <div class="stat-card" :class="{ active: taskStore.filters.status === null }" @click="filterByStatus(null)">
          <div class="stat-value">{{ taskStore.stats.total }}</div>
          <div class="stat-label">全部</div>
        </div>
        <div class="stat-card todo" :class="{ active: taskStore.filters.status === 'todo' }" @click="filterByStatus('todo')">
          <div class="stat-value">{{ taskStore.stats.todo }}</div>
          <div class="stat-label">待办</div>
        </div>
        <div class="stat-card in-progress" :class="{ active: taskStore.filters.status === 'in_progress' }" @click="filterByStatus('in_progress')">
          <div class="stat-value">{{ taskStore.stats.in_progress }}</div>
          <div class="stat-label">进行中</div>
        </div>
        <div class="stat-card completed" :class="{ active: taskStore.filters.status === 'completed' }" @click="filterByStatus('completed')">
          <div class="stat-value">{{ taskStore.stats.completed }}</div>
          <div class="stat-label">已完成</div>
        </div>
        <div class="stat-card overdue" :class="{ active: taskStore.filters.status === 'overdue' }" @click="filterByStatus('overdue')">
          <div class="stat-value">{{ taskStore.stats.overdue }}</div>
          <div class="stat-label">已过期</div>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters">
        <el-select v-model="priorityFilter" placeholder="优先级" clearable @change="handlePriorityChange" style="width: 120px">
          <el-option label="全部" :value="null" />
          <el-option label="高" value="high" />
          <el-option label="中" value="medium" />
          <el-option label="低" value="low" />
        </el-select>

        <el-input v-model="searchQuery" placeholder="搜索任务..." clearable style="width: 200px" @input="handleSearch">
          <template #prefix>
            <el-icon><search /></el-icon>
          </template>
        </el-input>

        <el-button type="primary" @click="openCreateDialog">
          <el-icon><plus /></el-icon>
          新建任务
        </el-button>
      </div>

      <!-- Task List -->
      <div class="task-list">
        <el-empty v-if="taskStore.tasks.length === 0" description="暂无任务，点击新建">
          <el-button type="primary" @click="openCreateDialog">新建任务</el-button>
        </el-empty>

        <draggable
          v-else
          v-model="localTasks"
          item-key="id"
          handle=".drag-handle"
          @end="handleDragEnd"
          class="task-list-inner"
        >
          <template #item="{ element }">
            <div class="task-wrapper">
              <div class="task-item" :class="{ overdue: isOverdue(element) }">
                <div class="drag-handle">
                  <el-icon><rank /></el-icon>
                </div>

                <div class="task-content" @click="openEditDialog(element)">
                  <div class="task-title">{{ element.title }}</div>
                  <div class="task-desc" v-if="element.description">{{ element.description }}</div>
                </div>

                <div class="task-priority">
                  <el-tag :type="getPriorityType(element.priority)" size="small">
                    {{ getPriorityLabel(element.priority) }}
                  </el-tag>
                </div>

                <div class="task-status">
                  <el-dropdown @command="(status) => handleStatusChange(element.id, status)">
                    <el-tag :type="getStatusType(element.status)" class="status-tag">
                      {{ getStatusLabel(element.status) }}
                      <el-icon class="el-icon--right"><arrow-down /></el-icon>
                    </el-tag>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="todo" :disabled="!canChangeTo(element, 'todo')">待办</el-dropdown-item>
                        <el-dropdown-item command="in_progress" :disabled="!canChangeTo(element, 'in_progress')">进行中</el-dropdown-item>
                        <el-dropdown-item command="completed" :disabled="!canChangeTo(element, 'completed')">已完成</el-dropdown-item>
                        <el-dropdown-item command="cancelled" :disabled="!canChangeTo(element, 'cancelled')">已取消</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>

                <div class="task-due" :class="{ 'is-overdue': isOverdue(element) }">
                  <el-icon><calendar /></el-icon>
                  {{ formatDueDate(element.due_date) }}
                </div>

                <div class="task-attachments" v-if="element.attachments?.length" @click.stop="toggleExpand(element.id)">
                  <el-icon><paperclip /></el-icon>
                  {{ element.attachments.length }}
                  <el-icon class="expand-icon" :class="{ expanded: expandedTasks.has(element.id) }">
                    <arrow-down />
                  </el-icon>
                </div>

                <div class="task-actions">
                  <el-button size="small" @click.stop="openEditDialog(element)">
                    <el-icon><edit /></el-icon>
                  </el-button>
                  <el-button size="small" type="danger" @click.stop="handleDelete(element.id)">
                    <el-icon><delete /></el-icon>
                  </el-button>
                </div>
              </div>

              <!-- Expanded Attachment View -->
              <div v-if="expandedTasks.has(element.id)" class="task-expanded">
                <div class="attachment-grid">
                  <div v-for="att in element.attachments" :key="att.id" class="attachment-card">
                    <!-- Image Preview -->
                    <div v-if="att.file_type === 'image'" class="attachment-preview image-preview">
                      <img v-if="attachmentUrls[att.id]" :src="attachmentUrls[att.id]" :alt="att.file_name" @click="openPreview(att)" />
                      <div v-else class="loading-placeholder">加载中...</div>
                    </div>
                    <!-- Video Preview -->
                    <div v-else-if="att.file_type === 'video'" class="attachment-preview video-preview">
                      <video v-if="attachmentUrls[att.id]" :src="attachmentUrls[att.id]" controls />
                      <div v-else class="loading-placeholder">加载中...</div>
                    </div>
                    <!-- Other File -->
                    <div v-else class="attachment-preview file-preview">
                      <el-icon><document /></el-icon>
                      <span class="file-name">{{ att.file_name }}</span>
                    </div>
                    <div class="attachment-info">
                      <span class="file-size">{{ formatFileSize(att.file_size) }}</span>
                      <div class="attachment-actions">
                        <el-button size="small" @click="downloadAttachment(att.id, att.file_name)">
                          <el-icon><Download /></el-icon>
                        </el-button>
                        <el-button size="small" type="danger" @click="handleDeleteAttachmentFromTask(element.id, att.id)">
                          <el-icon><delete /></el-icon>
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </draggable>

        <!-- Pagination -->
        <div class="pagination" v-if="taskStore.pages > 1">
          <el-pagination
            v-model:current-page="taskStore.page"
            :page-size="taskStore.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="taskStore.total"
            layout="sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </div>
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑任务' : '新建任务'" width="600px">
      <el-form ref="taskFormRef" :model="taskForm" :rules="taskRules" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="taskForm.title" placeholder="任务标题" maxlength="100" show-word-limit />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input v-model="taskForm.description" type="textarea" :rows="3" placeholder="任务描述" maxlength="2000" show-word-limit />
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="taskForm.priority">
            <el-radio label="high">高</el-radio>
            <el-radio label="medium">中</el-radio>
            <el-radio label="low">低</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="截止时间" prop="due_date">
          <el-date-picker v-model="taskForm.due_date" type="datetime" placeholder="选择截止时间" style="width: 100%" />
        </el-form-item>

        <el-form-item label="附件" v-if="isEdit">
          <div class="attachment-list">
            <div v-for="att in taskForm.attachments" :key="att.id" class="attachment-item">
              <el-icon v-if="att.file_type === 'image'"><picture /></el-icon>
              <el-icon v-else-if="att.file_type === 'video'"><video-play /></el-icon>
              <el-icon v-else><document /></el-icon>
              <span>{{ att.file_name }}</span>
              <el-button size="small" @click="downloadAttachment(att.id, att.file_name)">
                <el-icon><Download /></el-icon>
              </el-button>
              <el-button size="small" type="danger" @click="handleDeleteAttachment(att.id)">
                <el-icon><delete /></el-icon>
              </el-button>
            </div>
          </div>
          <el-upload
            ref="uploadRef"
            :auto-upload="true"
            :limit="10"
            :on-exceed="handleUploadExceed"
            :http-request="handleFileUpload"
            accept="image/*,video/*,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.zip,.rar"
            drag
          >
            <div class="upload-drag-area">
              <el-icon class="upload-icon"><UploadFilled /></el-icon>
              <div>将文件拖到此处，或<em>点击上传</em></div>
              <div class="upload-tip">支持图片、视频及常见文件格式</div>
            </div>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- Image Preview Dialog -->
    <el-dialog v-model="previewVisible" title="图片预览" width="800px">
      <img :src="previewUrl" style="max-width: 100%; display: block; margin: 0 auto;" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import draggable from 'vuedraggable'
import { useUserStore } from '@/stores/user'
import { useTaskStore } from '@/stores/task'
import api from '@/api/index'
import { taskApi } from '@/api/tasks'

const router = useRouter()
const userStore = useUserStore()
const taskStore = useTaskStore()

// Local tasks for draggable
const localTasks = ref([])

// Filters
const priorityFilter = ref(null)
const searchQuery = ref('')

// Dialog
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const taskFormRef = ref()
const uploadRef = ref()

// Expanded tasks
const expandedTasks = ref(new Set())

// Preview
const previewVisible = ref(false)
const previewUrl = ref('')

// Attachment blob URLs cache
const attachmentUrls = ref({})

const taskForm = reactive({
  id: null,
  title: '',
  description: '',
  priority: 'medium',
  due_date: null,
  attachments: []
})

const taskRules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }]
}

const validTransitions = {
  todo: ['in_progress', 'cancelled'],
  in_progress: ['completed', 'todo'],
  completed: [],
  cancelled: ['todo']
}

watch(() => taskStore.tasks, (newTasks) => {
  localTasks.value = [...newTasks]
}, { immediate: true })

onMounted(async () => {
  await taskStore.fetchStats()
  await taskStore.fetchTasks()
})

const handleCommand = async (command) => {
  if (command === 'settings') {
    router.push('/settings')
  } else if (command === 'logout') {
    await userStore.logout()
    router.push('/login')
  } else if (command === 'admin-stats') {
    router.push('/admin/stats')
  } else if (command === 'admin-users') {
    router.push('/admin/users')
  } else if (command === 'admin-config') {
    router.push('/admin/config')
  }
}

const filterByStatus = (status) => {
  taskStore.setFilters({ status })
  taskStore.fetchTasks()
}

const handlePriorityChange = (priority) => {
  taskStore.setFilters({ priority })
  taskStore.fetchTasks()
}

const handleSearch = () => {
  taskStore.setFilters({ search: searchQuery.value })
  taskStore.fetchTasks()
}

const handlePageChange = (page) => {
  taskStore.setPage(page)
  taskStore.fetchTasks()
}

const handleSizeChange = (size) => {
  taskStore.setPageSize(size)
  taskStore.fetchTasks()
}

const handleDragEnd = async () => {
  const taskIds = localTasks.value.map(t => t.id)
  await taskApi.sortTasks(taskIds)
  await taskStore.fetchTasks()
}

const openCreateDialog = () => {
  isEdit.value = false
  Object.assign(taskForm, {
    id: null,
    title: '',
    description: '',
    priority: 'medium',
    due_date: null,
    attachments: []
  })
  dialogVisible.value = true
}

const openEditDialog = async (task) => {
  isEdit.value = true
  try {
    const response = await taskApi.getTask(task.id)
    const taskData = response.data
    Object.assign(taskForm, {
      id: taskData.id,
      title: taskData.title,
      description: taskData.description,
      priority: taskData.priority,
      due_date: taskData.due_date,
      attachments: taskData.attachments || []
    })
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取任务详情失败')
  }
}

const handleSubmit = async () => {
  const valid = await taskFormRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data = {
      title: taskForm.title,
      description: taskForm.description,
      priority: taskForm.priority,
      due_date: taskForm.due_date
    }

    if (isEdit.value) {
      await taskStore.updateTask(taskForm.id, data)
    } else {
      await taskStore.createTask(data)
    }
    dialogVisible.value = false
    ElMessage.success(isEdit.value ? '任务已更新' : '任务已创建')
  } catch (error) {
    // Error handled by store
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个任务吗？', '提示', {
      type: 'warning'
    })
    await taskStore.deleteTask(id)
    ElMessage.success('任务已删除')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleStatusChange = async (id, status) => {
  try {
    await taskStore.updateTaskStatus(id, status)
    ElMessage.success('状态已更新')
  } catch (error) {
    // Error handled by store
  }
}

const handleDeleteAttachment = async (attId) => {
  try {
    await taskApi.deleteAttachment(attId)
    taskForm.attachments = taskForm.attachments.filter(a => a.id !== attId)
    ElMessage.success('附件已删除')
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

const handleUploadExceed = () => {
  ElMessage.warning('最多上传10个附件')
}

const handleFileUpload = async (options) => {
  try {
    const response = await taskApi.uploadAttachment(taskForm.id, options.file)
    taskForm.attachments.push(response.data)
    ElMessage.success('上传成功')
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

const isOverdue = (task) => {
  if (!task.due_date || task.status === 'completed' || task.status === 'cancelled') return false
  return new Date(task.due_date) < new Date()
}

const formatDueDate = (date) => {
  if (!date) return '-'
  const d = new Date(date)
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const getPriorityType = (priority) => {
  const map = { high: 'danger', medium: 'warning', low: 'success' }
  return map[priority] || 'info'
}

const getPriorityLabel = (priority) => {
  const map = { high: '高', medium: '中', low: '低' }
  return map[priority] || priority
}

const getStatusType = (status) => {
  const map = { todo: 'info', in_progress: 'primary', completed: 'success', cancelled: 'info' }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = { todo: '待办', in_progress: '进行中', completed: '已完成', cancelled: '已取消' }
  return map[status] || status
}

const canChangeTo = (task, targetStatus) => {
  return validTransitions[task.status]?.includes(targetStatus)
}

// Toggle task expanded state
const toggleExpand = async (taskId) => {
  if (expandedTasks.value.has(taskId)) {
    expandedTasks.value.delete(taskId)
  } else {
    expandedTasks.value.add(taskId)
    // Load blob URLs for attachments
    const task = localTasks.value.find(t => t.id === taskId)
    if (task?.attachments) {
      for (const att of task.attachments) {
        if (att.file_type === 'image' || att.file_type === 'video') {
          if (!attachmentUrls.value[att.id]) {
            try {
              const blobUrl = await getAttachmentBlobUrl(att.id)
              attachmentUrls.value[att.id] = blobUrl
              attachmentUrls.value = { ...attachmentUrls.value }
            } catch (e) {
              console.error('Failed to load attachment:', e)
            }
          }
        }
      }
    }
  }
  expandedTasks.value = new Set(expandedTasks.value)
}

// Get attachment URL for display
const getAttachmentUrl = (attachmentId) => {
  return taskApi.getDownloadUrl(attachmentId)
}

// Get attachment as blob URL for img/video tags
const getAttachmentBlobUrl = async (attachmentId) => {
  const token = localStorage.getItem('token')
  const response = await fetch(`/api/attachments/${attachmentId}/download`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  if (!response.ok) {
    throw new Error('Failed to load attachment')
  }
  const blob = await response.blob()
  return URL.createObjectURL(blob)
}

// Download attachment
const downloadAttachment = async (attachmentId, fileName) => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`/api/attachments/${attachmentId}/download`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (!response.ok) {
      throw new Error('Download failed')
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// Format file size
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Open image preview
const openPreview = (att) => {
  if (att.file_type === 'image') {
    // Use the blob URL that was already loaded with auth header
    previewUrl.value = attachmentUrls.value[att.id] || getAttachmentUrl(att.id)
    previewVisible.value = true
  }
}

// Delete attachment from task (in expanded view)
const handleDeleteAttachmentFromTask = async (taskId, attId) => {
  try {
    await ElMessageBox.confirm('确定要删除这个附件吗？', '提示', { type: 'warning' })
    await taskApi.deleteAttachment(attId)
    const taskIndex = localTasks.value.findIndex(t => t.id === taskId)
    if (taskIndex !== -1) {
      const task = localTasks.value[taskIndex]
      task.attachments = task.attachments.filter(a => a.id !== attId)
    }
    ElMessage.success('附件已删除')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.task-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  background: white;
  padding: 0 20px;
  height: 60px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin: 0;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.stats-cards {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-card.active {
  border-color: #409eff;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.stat-card.todo .stat-value { color: #909399; }
.stat-card.in-progress .stat-value { color: #409eff; }
.stat-card.completed .stat-value { color: #67c23a; }
.stat-card.overdue .stat-value { color: #f56c6c; }

.filters {
  background: white;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  display: flex;
  gap: 15px;
  align-items: center;
}

.filters .el-input {
  flex: 1;
  max-width: 300px;
}

.task-list {
  background: white;
  border-radius: 8px;
  padding: 15px;
}

.task-list-inner {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-wrapper {
  display: flex;
  flex-direction: column;
}

.task-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  gap: 15px;
  transition: all 0.3s;
}

.task-item:hover {
  background: #f5f7fa;
}

.task-item.overdue {
  border-color: #f56c6c;
  background: #fef0f0;
}

.drag-handle {
  cursor: grab;
  color: #909399;
}

.drag-handle:active {
  cursor: grabbing;
}

.task-content {
  flex: 1;
  cursor: pointer;
}

.task-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.task-desc {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 300px;
}

.task-status .status-tag {
  cursor: pointer;
}

.task-due {
  font-size: 13px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
}

.task-due.is-overdue {
  color: #f56c6c;
}

.task-attachments {
  font-size: 13px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.task-attachments:hover {
  background: #f5f7fa;
  color: #409eff;
}

.task-actions {
  display: flex;
  gap: 5px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 10px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}

.attachment-item span {
  flex: 1;
}

/* Expand icon */
.expand-icon {
  margin-left: 4px;
  transition: transform 0.3s;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

/* Task expanded area */
.task-expanded {
  padding: 15px;
  background: #fafafa;
  border-top: 1px solid #ebeef5;
  margin-top: -5px;
  border-radius: 0 0 8px 8px;
}

.attachment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
}

.attachment-card {
  background: white;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.attachment-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.attachment-preview {
  width: 100%;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  overflow: hidden;
}

.attachment-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  cursor: pointer;
}

.attachment-preview video {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.attachment-preview.file-preview {
  flex-direction: column;
  gap: 8px;
  color: #909399;
}

.attachment-preview.file-preview .file-name {
  font-size: 12px;
  text-align: center;
  padding: 0 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

.attachment-info {
  padding: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-size {
  font-size: 12px;
  color: #909399;
}

.attachment-actions {
  display: flex;
  gap: 4px;
}

/* Upload drag area */
.upload-drag-area {
  padding: 20px;
  text-align: center;
}

.upload-icon {
  font-size: 32px;
  color: #909399;
  margin-bottom: 10px;
}

.upload-drag-area div {
  color: #606266;
}

.upload-drag-area em {
  color: #409eff;
  font-style: normal;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.loading-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: #909399;
  font-size: 13px;
}
</style>
