<template>
  <div class="app-container">
    <!-- 主要内容区域 -->
    <div class="main-content">
      <div class="login-wrapper">
        <!-- 自定义标题栏覆盖在登录组件上 -->
        <div class="title-bar" id="title-bar">
          <div class="title-bar-content">
            <div class="title-bar-title">登录应用</div>
            <div class="title-bar-controls">
              <button class="title-bar-button minimize" @click="minimizeWindow">−</button>
              <button class="title-bar-button close" @click="closeWindow">×</button>
            </div>
          </div>
        </div>
        <Login/>
      </div>
    </div>
  </div>
</template>

<script setup>
import Login from './page/Loin.vue'

// 窗口控制函数
const minimizeWindow = () => {
  window.electronAPI?.minimizeWindow()
}

const closeWindow = () => {
  window.electronAPI?.closeWindow()
}
</script>

<style lang="less">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  overflow: hidden; /* 禁止滚动 */
}

body {
  overflow: hidden; /* 禁止滚动 */
}

.app-container {
  height: 100vh;
  position: relative;
  overflow: hidden; /* 禁止滚动 */
}

.title-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 32px;
  background: rgba(248, 249, 250, 0); /* 半透明背景 */
  backdrop-filter: blur(10px); /* 毛玻璃效果 */
  border-bottom: 1px solid rgba(233, 236, 239, 0.3);
  display: flex;
  align-items: center;
  z-index: 1000; /* 确保在最顶层 */
  -webkit-app-region: drag; /* 允许拖拽 */
  user-select: none;
}

.title-bar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 0 12px;
}

.title-bar-title {
  font-size: 14px;
  font-weight: 500;
  color: #495057;
}

.title-bar-controls {
  display: flex;
  gap: 8px;
  -webkit-app-region: no-drag; /* 按钮区域不允许拖拽 */
}

.title-bar-button {
  width: 24px;
  height: 24px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
  color: #6c757d;
  transition: all 0.2s;
}

.title-bar-button:hover {
  background: rgba(233, 236, 239, 0.8);
}

.title-bar-button.close:hover {
  background: #dc3545;
  color: white;
}

.main-content {
  height: 100vh;
  overflow: hidden; /* 禁止滚动 */
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-wrapper {
  position: relative;
  width: 100%;
  max-width: 400px;
}

.title-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 32px;
  background: rgba(248, 249, 250, 0.9); /* 半透明背景 */
  backdrop-filter: blur(10px); /* 毛玻璃效果 */
  border-bottom: 1px solid rgba(233, 236, 239, 0.3);
  display: flex;
  align-items: center;
  z-index: 1000; /* 确保在登录组件之上 */
  -webkit-app-region: drag; /* 允许拖拽 */
  user-select: none;
  border-radius: 16px 16px 0 0; /* 顶部圆角 */
}
</style>
