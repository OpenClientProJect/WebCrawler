<template>
  <div class="login-box">
    <div class="login-header">
      <h1 class="login-title">facebook登錄</h1>
      <p class="login-subtitle">请输入您的登录信息</p>
    </div>

    <form class="login-form">
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
        type="button"
        class="login-button"
        :disabled="isLoading"
        @click="handleLogin"
      >
        <span v-if="isLoading">登录中...</span>
        <span v-else>登录</span>
      </button>
    </form>
  </div>
</template>

<script setup>
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

  try {
    console.log('开始登录流程...')

    const credentials = {
      username: username.value,
      password: password.value
    }
    // 打开 Puppeteer 浏览器
    const success = await window.electronAPI?.login(credentials)
    console.log('openPuppeteerBrowser 返回结果:', success)
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped lang="less">
.login-box {
  background: #ffffff;
  border-radius: 15px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-title {
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.login-subtitle {
  color: #7f8c8d;
  font-size: 14px;
  margin: 0;
  font-weight: 400;
}

.login-form {
  border-radius: 8px;
  padding: 30px;
  width: 100%;
  max-width: 350px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 6px;
  color: #2c3e50;
  font-weight: 500;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s ease;
  background: #fff;
  color: #2c3e50;
  outline: none;
  box-sizing: border-box;

  &:focus {
    border-color: #3498db;
  }

  &::placeholder {
    color: #95a5a6;
  }
}

.login-button {
  width: 100%;
  padding: 12px 24px;
  background: #3498db;
  color: white;
  border: none;
  margin-top: 30px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
  margin-bottom: 20px;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &:not(:disabled):hover {
    background: #2980b9;
  }
}

.forgot-password,
.register-link {
  color: #3498db;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s ease;

  &:hover {
    color: #2980b9;
    text-decoration: none;
  }
}
</style>
