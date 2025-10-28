<template>
  <div class="setup-container">
    <div class="">
      <div class="setup-header">
        <h1 class="setup-title">系统设置</h1>
      </div>

      <form class="setup-form" @submit.prevent="saveSettings">
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
<!--        <div class="form-group">-->
<!--          <label for="refreshCount" class="form-label">-->
<!--            <span class="label-text">刷新数</span>-->
<!--            <span class="label-required">*</span>-->
<!--          </label>-->
<!--          <input-->
<!--            id="refreshCount"-->
<!--            v-model.number="refreshCount"-->
<!--            type="number"-->
<!--            class="form-input"-->
<!--            placeholder="10"-->
<!--            min="1"-->
<!--            max="1000"-->
<!--            required-->
<!--          />-->
<!--        </div>-->

        <div class="form-group">
          <label for="collectCount" class="form-label">
            <span class="label-text">采集帖子数量</span>
            <span class="label-required">*</span>
          </label>
          <input
            id="collectCount"
            v-model.number="postCount"
            type="number"
            class="form-input"
            placeholder="50"
            min="1"
            max="10000"
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

        <!-- URL输入框列表 -->
        <div class="form-group">
          <label class="form-label">
            <span style="font-weight: bold" class="label-text">采集链接<span style="font-size: 11px; margin-left: 2px">(回车确认)</span></span>
          </label>
          <div class="url-input-list-container">
            <div class="url-input-list">
            <div
              v-for="(url, index) in urlList"
              :key="index"
              class="url-input-item"
            >
              <input
                v-model="urlList[index]"
                type="text"
                class="form-input url-input"
                :placeholder="`请输入链接 ${index + 1}`"
                @keydown.enter="handleUrlEnter(index, $event)"
              />
              <button
                v-if="urlList.length > 1"
                type="button"
                class="delete-button"
                @click="removeUrl(index)"
              >
                删除
              </button>
            </div>
          </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <button
            type="button"
            class="action-button reset-button"
            :disabled="isLoading"
            @click="resetSettings"
          >
            重置设置
          </button>
          <button type="submit" class="action-button save-button" :disabled="isLoading">
            <span v-if="isLoading">保存中...</span>
            <span v-else>保存设置</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 设置数据
const deviceId = ref('')
const refreshCount = ref(null)
const collectCount = ref(null)
const postCount = ref(null)
const isLoading = ref(false)
const urlList = ref(['']) // 初始一个空输入框

// 处理URL输入框回车事件
const handleUrlEnter = (index, event) => {
  event.preventDefault()
  // 如果当前输入框有内容，添加新输入框
  if (urlList.value[index].trim() && index === urlList.value.length - 1) {
    urlList.value.push('')
  }
  // 如果不是最后一个输入框，移动到下一个
  if (index < urlList.value.length - 1) {
    const nextInput = document.querySelectorAll('.url-input')[index + 1]
    if (nextInput) {
      nextInput.focus()
    }
  }
}

// 删除URL输入框
const removeUrl = (index) => {
  if (urlList.value.length > 1) {
    urlList.value.splice(index, 1)
  }
}

// 保存设置
const saveSettings = async () => {
  if (!deviceId.value.trim()) {
    alert('请输入设备号')
    return
  }

  if (!refreshCount.value || refreshCount.value < 1 || refreshCount.value > 1000) {
    alert('请输入有效的刷新数(1-1000)')
    return
  }

  if (!collectCount.value || collectCount.value < 1 || collectCount.value > 10000) {
    alert('请输入有效的采集数(1-10000)')
    return
  }

  isLoading.value = true

  try {
    const settings = {
      deviceId: deviceId.value.trim(),
      refreshCount: refreshCount.value,
      collectCount: collectCount.value,
      postCount: postCount.value,
      urlList: urlList.value.filter(url => url.trim()) // 只保存非空URL
    }

    // 先保存设置到主进程
    const saveResult = await window.electronAPI?.saveSettings(settings)

    if (saveResult && saveResult.success) {
      // 保存成功后可以继续其他操作，比如打开浏览器
      const browserSuccess = await window.electronAPI?.openPuppeteerBrowser(settings)
    } else {
      const errors = saveResult?.errors || ['保存失败']
      alert('设置保存失败：' + errors.join(', '))
    }
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
  refreshCount.value = null
  collectCount.value = null
  postCount.value = null
  urlList.value = [''] // 重置为单个空输入框
}

// 加载设置
const loadSettings = async () => {
  try {
    // 从主进程获取设置
    const settings = await window.electronAPI?.getSettings()
    if (settings) {
      deviceId.value = settings.deviceId || ''
      refreshCount.value = settings.refreshCount || null
      collectCount.value = settings.collectCount || null
      urlList.value = settings.urlList && settings.urlList.length > 0
        ? settings.urlList
        : ['']
    }
  } catch (error) {
    console.error('加载设置失败:', error)
    // 如果从主进程加载失败，尝试从本地存储加载
    const savedSettings = localStorage.getItem('appSettings')
    if (savedSettings) {
      try {
        const settings = JSON.parse(savedSettings)
        deviceId.value = settings.deviceId || ''
        refreshCount.value = settings.refreshCount || null
        collectCount.value = settings.collectCount || null
      } catch (parseError) {
        console.error('解析本地设置失败:', parseError)
      }
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
  margin-bottom: 8px;
}

.setup-title {
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.setup-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-group {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 2px;
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

// URL输入框样式
.url-input-list-container {
  height: 200px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 8px;
  background: #f8f9fa;

  // 自定义滚动条
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 3px;

    &:hover {
      background: #555;
    }
  }
}

.url-input-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.url-input-item {
  display: flex;
  gap: 8px;
  align-items: center;
}

.url-input {
  flex: 1;
}

.delete-button {
  padding: 8px 16px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;

  &:hover {
    background: #c0392b;
  }
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
