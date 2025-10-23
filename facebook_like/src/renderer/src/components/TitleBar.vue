<template>
  <div class="title-bar" id="title-bar">
    <div class="title-bar-content">
      <div class="title-bar-title">登录应用</div>
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

</style>
