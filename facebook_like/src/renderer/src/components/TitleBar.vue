<template>
  <div class="title-bar">
    <div class="title-bar-content">
      <div class="title-bar-title">facebook_like</div>
      <div class="title-bar-controls">
        <button class="title-bar-button minimize" @click="minimizeWindow">−</button>
        <button class="title-bar-button close" @click="closeWindow">×</button>
      </div>
    </div>
  </div>
</template>

<script setup>

// 窗口控制函数
const minimizeWindow = () => {
  window.electronAPI?.minimizeWindow()
}

const closeWindow = () => {
  window.electronAPI?.closeWindow()
}
</script>

<style scoped lang="less">
.title-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 32px;
  background: rgba(248, 249, 250, 0);
  display: flex;
  align-items: center;
  z-index: 1000;
  -webkit-app-region: drag;
  user-select: none;
  border-radius: 16px 16px 0 0;
}

.title-bar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0 12px;
}

.title-bar-title {
  font-size: 20px;
  font-weight: bold;
  color: #555555;
}

.title-bar-controls {
  display: flex;
  gap: 8px;
}

.title-bar-button {
  width: 24px;
  height: 24px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
  color: #2a2b2b;
  transition: all 0.2s;
  -webkit-app-region: no-drag;
}

.title-bar-button:hover {
  background: rgba(233, 236, 239, 0.8);
}

.title-bar-button.close:hover {
  background: #dc3545;
  color: white;
}
</style>
