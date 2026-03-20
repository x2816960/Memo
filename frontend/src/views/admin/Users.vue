<template>
  <div class="admin-page">
    <div class="header">
      <div class="header-left">
        <el-button text @click="$router.back()">
          <el-icon><arrow-left /></el-icon>
        </el-button>
        <h1>用户管理</h1>
      </div>
      <div class="header-nav">
        <el-button text @click="$router.replace('/admin/stats')">统计中心</el-button>
        <el-button text type="primary">用户管理</el-button>
        <el-button text @click="$router.replace('/admin/config')">系统配置</el-button>
      </div>
    </div>

    <div class="main-content">
      <el-table :data="users" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="nickname" label="昵称" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
              {{ row.role === 'admin' ? '管理员' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '正常' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="handleToggleStatus(row)" :type="row.status === 'active' ? 'danger' : 'success'">
              {{ row.status === 'active' ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" type="warning" @click="handleResetPassword(row)">
              重置密码
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '@/api/admin'

const users = ref([])
const loading = ref(false)

onMounted(async () => {
  await fetchUsers()
})

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await adminApi.getUsers()
    users.value = response.data
  } catch (error) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleToggleStatus = async (user) => {
  const action = user.status === 'active' ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 ${user.username} 吗？`, '提示', {
      type: 'warning'
    })
    await adminApi.toggleUserStatus(user.id, user.status !== 'active')
    ElMessage.success(`${action}成功`)
    await fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`${action}失败`)
    }
  }
}

const handleResetPassword = async (user) => {
  try {
    await ElMessageBox.prompt('请输入新密码', `重置 ${user.username} 的密码`, {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /^.{8,32}$/,
      inputErrorMessage: '密码长度应为8-32位'
    })
    const newPassword = '123456' // Default reset password
    await adminApi.resetUserPassword(user.id, newPassword)
    ElMessage.success('密码已重置为: 123456')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重置失败')
    }
  }
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}
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

.header-nav {
  display: flex;
  gap: 10px;
}

.main-content {
  max-width: 1200px;
  margin: 20px auto;
  padding: 0 20px;
}
</style>
