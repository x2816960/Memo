<template>
  <div class="admin-page">
    <div class="header">
      <div class="header-left">
        <el-button text @click="$router.back()">
          <el-icon><arrow-left /></el-icon>
        </el-button>
        <h1>系统统计</h1>
      </div>
    </div>

    <div class="main-content">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="stat-card">
            <div class="stat-value">{{ stats.total_users }}</div>
            <div class="stat-label">总用户数</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card">
            <div class="stat-value">{{ stats.total_tasks }}</div>
            <div class="stat-label">总任务数</div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card class="stat-card">
            <div class="stat-value">{{ totalTaskRate }}%</div>
            <div class="stat-label">完成任务率</div>
          </el-card>
        </el-col>
      </el-row>

      <el-card style="margin-top: 20px">
        <template #header>任务状态分布</template>
        <div class="status-chart">
          <div class="status-bar">
            <div class="status-item todo" :style="{ width: getPercentage('todo') + '%' }">
              <span>待办 {{ stats.status_counts?.todo || 0 }}</span>
            </div>
            <div class="status-item in-progress" :style="{ width: getPercentage('in_progress') + '%' }">
              <span>进行中 {{ stats.status_counts?.in_progress || 0 }}</span>
            </div>
            <div class="status-item completed" :style="{ width: getPercentage('completed') + '%' }">
              <span>已完成 {{ stats.status_counts?.completed || 0 }}</span>
            </div>
            <div class="status-item cancelled" :style="{ width: getPercentage('cancelled') + '%' }">
              <span>已取消 {{ stats.status_counts?.cancelled || 0 }}</span>
            </div>
          </div>
        </div>
      </el-card>

      <div class="quick-links" style="margin-top: 20px">
        <el-button type="primary" @click="$router.push('/admin/users')">用户管理</el-button>
        <el-button type="primary" @click="$router.push('/admin/config')">系统配置</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api/admin'

const stats = ref({
  total_users: 0,
  total_tasks: 0,
  status_counts: {
    todo: 0,
    in_progress: 0,
    completed: 0,
    cancelled: 0
  }
})

const totalTaskRate = computed(() => {
  if (stats.value.total_tasks === 0) return 0
  const completed = stats.value.status_counts?.completed || 0
  return Math.round((completed / stats.value.total_tasks) * 100)
})

const getPercentage = (status) => {
  if (stats.value.total_tasks === 0) return 0
  const count = stats.value.status_counts?.[status] || 0
  return Math.round((count / stats.value.total_tasks) * 100)
}

onMounted(async () => {
  try {
    const response = await adminApi.getSystemStats()
    stats.value = response.data
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
})
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  background: white;
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header h1 {
  font-size: 20px;
  margin: 0;
}

.main-content {
  max-width: 1000px;
  margin: 20px auto;
  padding: 0 20px;
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 48px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 10px;
}

.status-chart {
  padding: 20px 0;
}

.status-bar {
  display: flex;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
}

.status-item {
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  transition: width 0.3s;
}

.status-item.todo {
  background: #909399;
}

.status-item.in-progress {
  background: #409eff;
}

.status-item.completed {
  background: #67c23a;
}

.status-item.cancelled {
  background: #e6e6e6;
  color: #909399;
}

.quick-links {
  display: flex;
  gap: 10px;
}
</style>
