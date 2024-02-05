<script setup>
import { useFriendRequests } from '@/stores/friendRequests'

const props = defineProps(['friendRequest'])
const friendRequestStore = useFriendRequests()
</script>

<template>
  <div>
    <li id="name">
      {{ props.friendRequest.follower.displayName }} wants to follow you.

      <button
        class="btn btn-sm btn-success mr-1"
        @click="friendRequestStore.accept(friendRequest.id)"
      >
        Accept
      </button>
      <button
        class="btn btn-sm btn-danger"
        @click="friendRequestStore.decline(props.friendRequest.id)"
      >
        Decline
      </button>
    </li>
  </div>
</template>

<style scoped>
li {
  background-color: inherit;
  font-size: large;
  padding: 8px;
  list-style-type: '\26B9';
}
#name {
  font-weight: bold;
}
</style>
