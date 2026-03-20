<template>
  <div class="settings-page">
    <div class="header">
      <div class="header-left">
        <el-button text @click="$router.back()">
          <el-icon><arrow-left /></el-icon>
        </el-button>
        <h1>个人设置</h1>
      </div>
    </div>

    <div class="main-content">
      <el-card>
        <template #header>修改密码</template>
        <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="100px">
          <el-form-item label="旧密码" v-if="!userStore.mustChangePassword" prop="oldPassword">
            <el-input v-model="passwordForm.oldPassword" type="password" show-password />
          </el-form-item>

          <el-form-item label="新密码" prop="newPassword">
            <el-input v-model="passwordForm.newPassword" type="password" show-password />
          </el-form-item>

          <el-form-item label="确认新密码" prop="confirmPassword">
            <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="loading" @click="handleChangePassword">
              保存
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card style="margin-top: 20px">
        <template #header>账号信息</template>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="用户名">{{ userStore.user?.username }}</el-descriptions-item>
          <el-descriptions-item label="昵称">
            <el-input v-if="editing" v-model="nicknameForm.nickname" style="width: 200px" />
            <span v-else>{{ userStore.user?.nickname || '-' }}</span>
            <el-button v-if="!editing" size="small" @click="editing = true">编辑</el-button>
            <template v-else>
              <el-button size="small" type="primary" @click="handleUpdateNickname">保存</el-button>
              <el-button size="small" @click="editing = false">取消</el-button>
            </template>
          </el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ userStore.user?.email || '-' }}</el-descriptions-item>
          <el-descriptions-item label="注册时间">{{ formatDate(userStore.user?.created_at) }}</el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const editing = ref(false)

const passwordFormRef = ref()
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const nicknameForm = reactive({
  nickname: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  oldPassword: [
    { required: !userStore.mustChangePassword, message: '请输入旧密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, max: 32, message: '密码长度为8-32位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleChangePassword = async () => {
  const valid = await passwordFormRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    if (userStore.mustChangePassword) {
      await userStore.adminChangePassword(passwordForm.newPassword)
    } else {
      await userStore.changePassword(passwordForm.oldPassword, passwordForm.newPassword)
    }
    ElMessage.success('密码修改成功')
    passwordForm.oldPassword = ''
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    router.push('/tasks')
  } catch (error) {
    // Error handled by interceptor
  } finally {
    loading.value = false
  }
}

const handleUpdateNickname = async () => {
  try {
    await authApi.updateProfile({ nickname: nicknameForm.nickname })
    await userStore.fetchUser()
    editing.value = false
    ElMessage.success('昵称已更新')
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.settings-page {
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
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}
</style>
