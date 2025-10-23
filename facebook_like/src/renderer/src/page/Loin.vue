<template>
  <div class="login-box">
    <div class="login-header">
      <h1 class="login-title">用户登录</h1>
      <p class="login-subtitle">请输入您的登录信息</p>
    </div>

    <form @submit.prevent="handleLogin" class="login-form">
      <div class="form-group">
        <label for="username" class="form-label">用户名</label>
        <input
          id="username"
          v-model="username"
          type="text"
          class="form-input"
          placeholder="请输入用户名"
          required
        />
      </div>

      <div class="form-group">
        <label for="password" class="form-label">密码</label>
        <input
          id="password"
          v-model="password"
          type="password"
          class="form-input"
          placeholder="请输入密码"
          required
        />
      </div>

      <button
        type="submit"
        class="login-button"
        :disabled="isLoading"
      >
        <span v-if="isLoading">登录中...</span>
        <span v-else>登录</span>
      </button>
    </form>

    <div class="login-footer">
      <a href="#" class="forgot-password">忘记密码？</a>
      <a href="#" class="register-link">注册新账户</a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const username = ref('')
const password = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  if (!username.value || !password.value) {
    alert('请输入用户名和密码')
    return
  }

  isLoading.value = true

  // 模拟登录请求
  setTimeout(() => {
    isLoading.value = false
    alert(`欢迎 ${username.value}！`)
  }, 1500)
}

</script>


<style scoped lang="less">
@import '../assets/css/styles.less';
</style>
