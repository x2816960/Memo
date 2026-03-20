<template>
  <div class="admin-page">
    <div class="header">
      <div class="header-left">
        <el-button text @click="$router.back()">
          <el-icon><arrow-left /></el-icon>
        </el-button>
        <h1>系统配置</h1>
      </div>
    </div>

    <div class="main-content">
      <el-card>
        <template #header>附件上传限制</template>
        <el-form ref="configFormRef" :model="configForm" label-width="150px">
          <el-form-item label="图片最大文件大小">
            <el-input-number v-model="configForm.image_max_size" :min="1" :max="100" :step="1" />
            <span class="form-tip">MB (范围: 1-100MB)</span>
          </el-form-item>

          <el-form-item label="视频最大文件大小">
            <el-input-number v-model="configForm.video_max_size" :min="10" :max="2000" :step="10" />
            <span class="form-tip">MB (范围: 10MB-2GB)</span>
          </el-form-item>

          <el-form-item label="其他附件大小">
            <el-input-number v-model="configForm.other_max_size" :min="1" :max="500" :step="1" />
            <span class="form-tip">MB (范围: 1-500MB)</span>
          </el-form-item>

          <el-form-item label="每任务最大附件数">
            <el-input-number v-model="configForm.max_attachments_per_task" :min="1" :max="50" :step="1" />
            <span class="form-tip">个 (范围: 1-50)</span>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="loading" @click="handleSaveConfig">
              保存配置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '@/api/admin'

const loading = ref(false)

const configForm = reactive({
  image_max_size: 10,
  video_max_size: 200,
  other_max_size: 50,
  max_attachments_per_task: 10
})

onMounted(async () => {
  await fetchConfig()
})

const fetchConfig = async () => {
  try {
    const response = await adminApi.getConfig()
    configForm.image_max_size = response.data.image_max_size / (1024 * 1024)
    configForm.video_max_size = response.data.video_max_size / (1024 * 1024)
    configForm.other_max_size = response.data.other_max_size / (1024 * 1024)
    configForm.max_attachments_per_task = response.data.max_attachments_per_task
  } catch (error) {
    ElMessage.error('获取配置失败')
  }
}

const handleSaveConfig = async () => {
  loading.value = true
  try {
    await adminApi.updateConfig({
      image_max_size: configForm.image_max_size * 1024 * 1024,
      video_max_size: configForm.video_max_size * 1024 * 1024,
      other_max_size: configForm.other_max_size * 1024 * 1024,
      max_attachments_per_task: configForm.max_attachments_per_task
    })
    ElMessage.success('配置已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    loading.value = false
  }
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

.main-content {
  max-width: 800px;
  margin: 20px auto;
  padding: 0 20px;
}

.form-tip {
  margin-left: 10px;
  color: #909399;
  font-size: 13px;
}
</style>
