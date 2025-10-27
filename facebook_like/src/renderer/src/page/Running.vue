<template>
  <div class="running-container">
    <div class="running-content">
      <div class="running-header">
        <h1 class="running-title">运行中</h1>
        <div class="status-indicator">
          <div class="pulse-dot"></div>
          <span class="status-text">正在采集数据...</span>
        </div>
      </div>

      <div class="stats-box">
        <div class="stat-item">
          <div class="stat-value">{{ processedCount }}</div>
          <div class="stat-label">已处理帖子</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ collectedCount }}</div>
          <div class="stat-label">已采集用户</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ sponsorCount }}</div>
          <div class="stat-label">发现赞助帖</div>
        </div>
      </div>

      <div class="log-box">
        <div class="log-content" ref="logContainer">
          <div
            v-for="(log, index) in logs"
            :key="index"
            :class="['log-item', log.type]"
          >
            <span class="log-time">{{ log.timestamp }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

const processedCount = ref(0)
const collectedCount = ref(0)
const sponsorCount = ref(0)
const logs = ref([])
const logContainer = ref(null)

// 添加日志
const addLog = (logData) => {
  logs.value.push(logData)

  // 限制日志数量，保留最新的100条
  if (logs.value.length > 100) {
    logs.value.shift()
  }

  // 自动滚动到底部
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}

// 监听来自主进程的日志
const handleLogMessage = (event, logData) => {
  addLog(logData)

  // 从日志中提取统计数据
  if (logData.message.includes('处理完第')) {
    processedCount.value++
  }
  if (logData.message.includes('找到赞助元素')) {
    sponsorCount.value++
  }
  if (logData.message.includes('找到') && logData.message.includes('个用户')) {
    // 从日志中解析采集的用户数量
    const match = logData.message.match(/找到(\d+)个用户/)
    if (match) {
      collectedCount.value += parseInt(match[1])
    }
  }
  if (logData.message.includes('成功批量插入')) {
    const match = logData.message.match(/成功批量插入 (\d+)/)
    if (match) {
      sponsorCount.value++
    }
  }
}

onMounted(() => {
  // 注册监听器
  if (window.electronAPI) {
    window.electronAPI.onLogMessage?.(handleLogMessage)
  }
})

onUnmounted(() => {
  // 清理监听器
  if (window.electronAPI) {
    window.electronAPI.removeLogMessageListener?.(handleLogMessage)
  }
})
</script>

<style scoped lang="less">
.running-container {
  background: #ffffff;
  border-radius: 15px;
  height: 100vh;
  display: flex;
  justify-content: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  padding: 20px;
}

.running-content {
  width: 100%;
  max-width: 400px;
}

.running-header {
  text-align: center;
  margin-top: 5px;
}

.running-title {
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 15px 0;
}

.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.pulse-dot {
  width: 10px;
  height: 10px;
  background: #27ae60;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.status-text {
  color: #7f8c8d;
  font-size: 14px;
}

.stats-box {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.stat-item {
  flex: 1;
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #3498db;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #7f8c8d;
}

.log-box {
  background: #f8f9fa;
  height: 300px;
  border-radius: 8px;
  overflow: hidden;
}


.log-content {
  overflow-y: auto;
  padding: 10px;
  background: #1e1e1e;
  color: #d4d4d4;
}

.log-item {
  display: flex;
  gap: 10px;
  font-size: 11px;
  padding: 5px 0;
  border-bottom: 1px solid #3c3c3c;
  font-family: 'Courier New', monospace;

  &:last-child {
    border-bottom: none;
  }

  &.error {
    color: #f14c4c;
  }

  &.log {
    color: #4ec9b0;
  }
}

.log-time {
  color: #808080;
  flex-shrink: 0;
}

.log-message {
  flex: 1;
  word-break: break-all;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}
</style>
