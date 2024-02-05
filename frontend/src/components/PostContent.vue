<script setup>
import { getMarkdownHTML } from '@/api/post';
const props = defineProps({
  post: {
    type: Object
  }
})


</script>

<template>
  <div v-if="props.post.contentType?.startsWith('image/')">
    <img :src="props.post.content" />
  </div>
  <div
    v-else-if="props.post.contentType === 'text/markdown'"
    v-html="getMarkdownHTML(props.post.content)"
  ></div>
  <div v-else>
    <p class="content">{{ props.post.content }}</p>
  </div>
</template>

<style scoped>
img {
  width: 90%;
}
</style>
