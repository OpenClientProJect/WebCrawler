<template>
  <div class="app-container">
    <!-- 主要内容区域 -->
    <div class="main-content">
      <div class="login-wrapper">
        <TitleBar/>
        <Login/>
      </div>
    </div>
  </div>
</template>

<script setup>
import Login from './page/Loin.vue'
import SetUp from "./page/SetUp.vue";
import TitleBar from "./components/TitleBar.vue";
</script>

<style lang="less">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>
