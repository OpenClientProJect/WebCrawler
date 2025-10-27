<template>
  <div class="app-container">
    <!-- 主要内容区域 -->
    <div class="main-content">
      <div class="login-wrapper">
        <TitleBar/>
        <SetUp v-if="currentComponent === 'setup'"/>
        <Login v-if="currentComponent === 'login'"/>
        <Running v-if="currentComponent === 'running'"/>
      </div>
    </div>
  </div>
</template>

<script setup>
import Login from './page/Loin.vue'
import SetUp from "./page/SetUp.vue";
import TitleBar from "./components/TitleBar.vue";
import {onMounted, onUnmounted, ref} from "vue";
import Running from "./page/Running.vue";

const currentComponent = ref('setup')

const handleSwitchToLogin = () => {
  currentComponent.value = 'login'
}

const handleLoginSuccess = () => {
  currentComponent.value = 'running'  // 登录成功后切换到运行页面
}

onMounted(() => {
  // 注册监听器
  window.electronAPI?.onSwitchToLogin(handleSwitchToLogin)
  if (window.electronAPI) {
    window.electronAPI.onLoginSuccess?.(handleLoginSuccess)
  }
})

onUnmounted(() => {
  // 清理监听器
  window.electronAPI?.removeSwitchToLoginListener(handleSwitchToLogin)
  if (window.electronAPI) {
    window.electronAPI.removeLoginSuccessListener?.(handleLoginSuccess)
  }
})
</script>

<style lang="less">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>
