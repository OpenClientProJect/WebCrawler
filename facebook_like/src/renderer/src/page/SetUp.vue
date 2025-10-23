<template>
  <div class="setup-container">
    <div class="">
      <div class="setup-header">
        <h1 class="setup-title">系统设置</h1>
      </div>

      <form @submit.prevent="saveSettings" class="setup-form">
        <!-- 设备号设置 -->
        <div class="form-group">
          <label for="deviceId" class="form-label">
            <span class="label-text">设备号</span>
            <span class="label-required">*</span>
          </label>
          <input
            id="deviceId"
            v-model="deviceId"
            type="text"
            class="form-input"
            placeholder="请输入设备唯一标识"
            required
          />
        </div>

        <!-- 刷新数设置 -->
        <div class="form-group">
          <label for="refreshCount" class="form-label">
            <span class="label-text">刷新数</span>
            <span class="label-required">*</span>
          </label>
          <input
            id="refreshCount"
            v-model.number="refreshCount"
            type="number"
            class="form-input"
            placeholder="10"
            min="1"
            max="1000"
            required
          />
        </div>

        <!-- 采集数设置 -->
        <div class="form-group">
          <label for="collectCount" class="form-label">
            <span class="label-text">采集数</span>
            <span class="label-required">*</span>
          </label>
          <input
            id="collectCount"
            v-model.number="collectCount"
            type="number"
            class="form-input"
            placeholder="50"
            min="1"
            max="10000"
            required
          />
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <button
            type="button"
            @click="resetSettings"
            class="action-button reset-button"
            :disabled="isLoading"
          >
            重置设置
          </button>
          <button
            type="submit"
            class="action-button save-button"
            :disabled="isLoading"
          >
            <span v-if="isLoading">保存中...</span>
            <span v-else>保存设置</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue'

// 设置数据
const deviceId = ref('')
const refreshCount = ref(10)
const collectCount = ref(50)
const isLoading = ref(false)

// 保存设置
const saveSettings = async () => {
  if (!deviceId.value.trim()) {
    alert('请输入设备号')
    return
  }

  if (refreshCount.value < 1 || refreshCount.value > 1000) {
    alert('刷新数必须在1-1000之间')
    return
  }

  if (collectCount.value < 1 || collectCount.value > 10000) {
    alert('采集数必须在1-10000之间')
    return
  }

  isLoading.value = true

  try {
    const settings = {
      deviceId: deviceId.value.trim(),
      refreshCount: refreshCount.value,
      collectCount: collectCount.value
    }
    const success = await window.electronAPI?.openPuppeteerBrowser(settings)
  } catch (error) {
    console.error('保存设置失败:', error)
    alert('保存设置失败，请重试')
  } finally {
    isLoading.value = false
  }
}

// 重置设置
const resetSettings = () => {
  deviceId.value = ''
  refreshCount.value = 10
  collectCount.value = 50
}

// 加载设置
const loadSettings = () => {
  // 这里可以从本地存储或主进程加载设置
  const savedSettings = localStorage.getItem('appSettings')
  if (savedSettings) {
    try {
      const settings = JSON.parse(savedSettings)
      deviceId.value = settings.deviceId || ''
      refreshCount.value = settings.refreshCount || 10
      collectCount.value = settings.collectCount || 50
    } catch (error) {
      console.error('加载设置失败:', error)
    }
  }
}

// 组件挂载时加载设置
onMounted(() => {
  loadSettings()
})
</script>

<style scoped lang="less">
.setup-container {
  background: #ffffff;
  border-radius: 15px;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.setup-header {
  text-align: center;
  margin-bottom: 30px;
}

.setup-title {
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
  margin: 0;
}

.setup-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
  color: #34495e;
  font-size: 14px;
}

.label-text {
  font-size: 15px;
}

.label-required {
  color: #e74c3c;
  font-weight: bold;
  font-size: 16px;
}

.form-input {
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
  background: #fff;
  color: #2c3e50;
  outline: none;

  &:focus {
    border-color: #3498db;
  }

  &::placeholder {
    color: #95a5a6;
  }
}

.form-actions {
  display: flex;
  gap: 16px;
  margin-top: 20px;
  justify-content: flex-end;
}

.action-button {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
  min-width: 100px;
}

.reset-button {
  background: #95a5a6;
  color: white;

  &:not(:disabled):hover {
    background: #7f8c8d;
  }
}

.save-button {
  background: #3498db;
  color: white;

  &:not(:disabled):hover {
    background: #2980b9;
  }
}


.action-button:disabled span {
  animation: pulse 1.5s infinite;
}

// 加载动画
@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

</style>
