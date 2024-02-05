<script setup>
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import Taskbar from '@/components/TaskBar.vue'

const authStore = useAuthStore()
authStore.setup()
authStore.initializeUser()
</script>

<template>
  <div class="app-container">
    <div class="logo">
      <header class="main-header">
        <img src="../src/assets/logogrape.png" class="grvine" />
      </header>
    </div>
    <taskbar v-if="authStore.authenticated" />
    <div class="container pt-4 pb-4">
      <RouterView />
    </div>
  </div>
</template>

<style>
*{
  line-height: 130%;
}
.main-header {
  margin: 1em;
}

.grvine {
  margin-top: 15px;
  height: 85px;
  width: 400px;
  margin-bottom: -15px;
}
.logo {
  display: flex;
  align-items: center;
  justify-content: center;
}

.app-container {
  font-family: Arial, Verdana, Geneva, Tahoma, sans-serif;
  background-color: #f8f8f8;
  background: linear-gradient(180deg, rgb(255, 231, 184) 0%, #cba7de7c 0%, transparent 100%);
  height: 100vh;
  overflow-y: scroll;
  scrollbar-color: #2a006056 transparent;
}
</style>
