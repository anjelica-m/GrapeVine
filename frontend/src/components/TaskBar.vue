<!--  https://www.tutorialspoint.com/shake-a-button-on-hover-using-html-and-css#:~:text=We%20need%20to%20create%20a,user%20hovers%20over%20the%20button. -->

<script setup>
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'

const authStore = useAuthStore()
</script>

<template>
  <div class="task_bar">
    <div class="center_nav">
      <router-link class="btn" :to="{ name: 'home' }">Home</router-link>
      
      <router-link
        class="btn"
        :to="{ name: 'profile', params: { id: authStore.user?.author?.id || 0 } }"
        >Profile</router-link
      >
      <router-link class="btn" role="button" :to="{ name: 'create-post' }"
        >Create a post</router-link
      >
      <router-link class="btn" :to="{ name: 'search' }">Search</router-link>
      <a @click="authStore.logout()" class="btn" id="log">Logout</a>
    </div>
  </div>
</template>

<style scoped>
.task_bar {
  padding: 0 1em;
  justify-content: flex-start;
  position: relative;
  padding-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 20px;
}

.center_nav {
  margin-top: 10px;
  flex: 0 1 auto;
  position: absolute;
  gap: 0.5em;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-self: center;
}

.btn {
  color: #f9ecfd;
  background-color: #8565b9;
  border-color: #8565b9;
  font-size: calc(8px + 0.5vw);
  min-width: fit-content;
}

.btn:hover {
  color: #f8f8f8;
  background-color: #58935a;
  border-color: #58935a;
}
.btn:active {
  color: #f8f8f8;
  background-color: #58935a;
  border-color: #58935a;
}
.btn:focus,
.btn.focus {
  outline: none !important;
  box-shadow: none !important;
  color: #f9ecfd;
  background-color: #8565b9;
  border-color: #8565b9;
}
#log:hover{
  background-color: #1d361e;
  border-color: #1d361e;

}
#log:hover {animation: shaking 0.5s infinite;}
      @keyframes shaking {
         0% {transform: rotate(0deg);}
         20% {transform: rotate(-4deg);}
         50% {transform: rotate(0deg);}
         70% {transform: rotate(4deg);}
         100% {transform: rotate(0deg);}
      }
</style>
