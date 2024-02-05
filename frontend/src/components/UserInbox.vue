<script setup>
import FriendRequest from '@/components/FriendRequest.vue'
import { useFriendRequests } from '@/stores/friendRequests'
import { onMounted, ref, watch } from 'vue'
import GithubActivity from '@/components/GithubActivity.vue'
import { fetchNotifs } from '@/api/post'
import { useAuthStore } from '@/stores/auth.store'
import {RouterLink} from 'vue-router'
import {getId} from '@/helpers/id-utils'

const auth = useAuthStore()
const friendRequestsStore = useFriendRequests()
const notifications = ref([])

onMounted(async () => {
  friendRequestsStore.loadFriendRequests()
  if (auth.user) {
    notifications.value = await fetchNotifs(auth.user.author.id);
  }
})

watch(auth, async () => {
  notifications.value = await fetchNotifs(auth.user.author.id);
})
</script>

<template>
  <div style="position:static;" class="inboxBar">
    <v-btn onclick="document.getElementById('inbox').scrollIntoView();" class="btn">Inbox</v-btn>
    <v-btn onclick="document.getElementById('req').scrollIntoView();" class="btn">Friend Requests</v-btn>
  </div>
  <div class="allIn">
    <div class="inbox" id="inbox">
      <h2>Inbox</h2>
      <div v-if="notifications" v-for="notif in notifications">
        <!-- <a :href="notif.link">{{ notif.message }}</a> -->
        <router-link :to="{ name: 'post', params: {id: getId(notif.link)} }">{{notif.message}}</router-link>
        <!-- <p>{{ notif.message }}</p> -->
      </div>
      
    </div>
    <!-- Friend request processing -->
    <div class="friendReq" id="req">
      <h2>Friend Requests</h2>
      <div v-if="friendRequestsStore.friendRequests.length > 0">
        <div class="allReq">
          <friend-request
            id="fr"
            :friendRequest="fr"
            :key="fr.id"
            v-for="fr in friendRequestsStore.friendRequests"
          />
        </div>
      </div>
      <h4 v-else>You have no active friend requests &#9785;</h4>
    </div>
  </div>
</template>

<style scoped>
.inbox {
  background-color: inherit;
  max-width: 555px;
  min-width: 250px;
  min-height: 250px;
}
.friendReq, .github  {
  background-color: inherit;
  max-width: 555px;
  min-width: 250px;
}
h2 {
  background-color: inherit;
  font-size: calc(10px + 1.75vw);
  font-variant: small-caps;
  text-decoration: underline black 2px;
}
.allReq {
  background-color: inherit;
  padding-left: 25px;
}

h4 {
  background-color: inherit;
  color: #58935a;
}
.allIn {
  background-color: transparent;
}
p {
  background-color: inherit;
}
.inboxBar{
  top: 0;
  position: sticky;
  margin-bottom: 5px;
  z-index: 99;
}
.btn {
  color: #f9ecfd;
  background-color: #8565b9;
  border-color: #8565b9;
  font-size: calc(8px + 0.5vw);
  min-width: fit-content;
  margin-right: 10px;
  align-content: center;
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
</style>
