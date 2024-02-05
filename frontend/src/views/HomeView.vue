<script setup>
import Inbox from '@/components/UserInbox.vue'
import Feed from '@/components/HomeFeed.vue'
import { useAuthStore } from '@/stores/auth.store'

const auth = useAuthStore()
</script>

<template>
  <div class="home">
    <div class="user-profile" v-if="auth.currentUser">
      <img :src="auth.currentUser?.author?.profileImage" alt="User image" />

      <div class="user-details">
        <h2 id="stream-name"> Welcome to Grapevine {{ auth.currentUser?.author?.displayName }}, we're glad you're here!</h2>
      </div>
    </div>
    <div class="sideby">
      <div class="inSpace">
        <inbox class="inbox" />
      </div>
      <div class="feedSpace">
        <feed class="feed" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.btn {
  color: #f9ecfd;
  background-color: #8565b9;
  border-color: #8565b9;
}

.btn:hover {
  color: #f8f8f8;
  background-color: #58935a;
  border-color: #58935a;
}
img {
  width: 200px;
  height: 200px;
  justify-content: center;
  align-self: center;
  padding-bottom: 10;
  border-radius: 30px;
  border: 3px outset rgb(0, 0, 0);
}
.inSpace {
  flex: 1;
  justify-content: left;
  align-self: left;
  border: 6px solid #58935a8f;
  padding: 1em;
  background-color: #58935a3b;
  border-radius: 8px;
  margin-right: 10px;
  max-height: 500px;
  overflow-y: scroll;
  scrollbar-color: rgba(6, 129, 72, 0.469) transparent;
}
.feedSpace {
  background-color: #dbd3e8;
  flex: 1;
  padding: 1em;
  display: flex;
  flex-direction: row;
  border: 6px solid #8758938f;
  border-radius: 8px;
  scrollbar-color: rgba(81, 6, 129, 0.559) transparent;
  max-height: 500px;
  overflow-y: scroll;
}
.sideby {
  display: flex;
}
.feed {
  max-width: 553px;
  min-width: 250px;
}
.inbox {
  max-width: 553px;
  min-width: 250px;
}
.user-profile {
  display: flex;
  flex: 1;
  flex-direction: row;
  justify-content: left;
  align-items: center;
  padding: 10px;
}

#stream-name{
  padding-left: 15px;
}
</style>
