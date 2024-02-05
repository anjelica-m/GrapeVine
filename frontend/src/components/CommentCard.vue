<script setup>
import {getId} from '@/helpers/id-utils'
import { getMarkdownHTML } from '@/api/post';
const props = defineProps(['comment'])
const emit = defineEmits(['likeComment', 'unlikeComment'])


</script>

<template>
  <h5>
    <router-link id="auth" :to="{ name: 'profile', params: { id: getId(props.comment.author.id) } }">{{
      props.comment.author.displayName
    }} commented: </router-link>
  </h5>

  <div v-if="props.comment.contentType === 'text/markdown'" v-html="getMarkdownHTML(props.comment.comment)">
  </div>
  <div v-else>
    <p class="content">{{ props.comment.comment }}</p>
  </div>
  <p>
    {{ props.comment.like_count }}
    <i
      class="bi bi-hand-thumbs-up-fill"
      v-if="props.comment.liked_by_me"
      @click="emit('unlikeComment', props.comment.id)"
    ></i>
    <i class="bi bi-hand-thumbs-up" v-else @click="emit('likeComment', props.comment.id)"></i>
  </p>
</template>

<style scoped>
#auth {
  color: #58935a;
}
p {
  background-color: transparent;
}
i {
  background-color: transparent;
}
h5 {
  background-color: transparent;
}
</style>
