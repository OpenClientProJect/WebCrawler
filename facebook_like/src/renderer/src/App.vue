<template>
  <div class="app-container">
    <!-- 主要内容区域 -->
    <div class="main-content">
      <div class="login-wrapper">
        <TitleBar/>
        <SetUp v-if="currentComponent === 'setup'"/>
        <Login v-if="currentComponent === 'login'"/>
      </div>
    </div>
  </div>
</template>

<script setup>
import Login from './page/Loin.vue'
import SetUp from "./page/SetUp.vue";
import TitleBar from "./components/TitleBar.vue";
import {onMounted, onUnmounted, ref} from "vue";

const currentComponent = ref('setup')

const handleSwitchToLogin = () => {
  currentComponent.value = 'login'
}

onMounted(() => {
  // 注册监听器
  window.electronAPI?.onSwitchToLogin(handleSwitchToLogin)
})

onUnmounted(() => {
  // 清理监听器
  window.electronAPI?.removeSwitchToLoginListener(handleSwitchToLogin)
})
</script>

<style lang="less">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>
