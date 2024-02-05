

<template>
  <div class="post-card">
    <span id="header">
      <h1><router-link :to="{name: 'post', params: {id: getId(post.id)}}">{{
              post.title
            }}</router-link></h1>
     <h2> by {{ props.post?.author?.displayName }}</h2>
    </span>
    <div id="content">
    <div v-if="props.post.contentType == 'image/png;base64'">
    <img v-bind:src="props.post.content" :alt="post.description">
    </div>
    <div v-else-if="props.post.contentType == 'image/jpeg;base64'">
    <img v-bind:src="props.post.content" :alt="post.description">
  </div>
    <div v-else>
      <PostContent :post="props.post" />
    </div>
  </div>
    
    <p class="likesComments">
      {{ props.post.like_count }} Likes {{ props.post.comment_count }} Comments
    </p>
  </div>
</template>

<script setup>
import {getId} from '@/helpers/id-utils'
import PostContent from '@/components/PostContent.vue'
import { Parser, HtmlRenderer } from 'commonmark'
const props = defineProps({
  post: {
    type: Object
  }
})


const getMarkdownHTML = function (data) {
  const reader = new Parser()
  const writer = new HtmlRenderer({ safe: true })
  const parsed = reader.parse(data)
  const result = writer.render(parsed)
  return result
}
</script>
<style scoped>
h3,
h2 {
  color: #58935a;
  flex-direction: row;
  justify-content: center;
  align-self: center;
  display: flex;
}

.content {
  font-size: 30px;
}

.likesComments {
  font-size: 22px;
}
img{
  max-width: 200px;
  max-height: 200px;
}
#content{
  border: 4px solid #8758938f;
  border-radius: 10px;
  padding: 10px;
  text-align:left;
  line-height: 160%;
  vertical-align: bottom;
  font-size: 120%;
}
#header{
  text-align: center;
  line-height: 50px;
  top: calc(50%);
}
a, a:hover{
  color: black;
  padding-right: 10px;
  
}
</style>
