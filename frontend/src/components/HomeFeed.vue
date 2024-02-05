<script setup>
import { onMounted, ref, watch } from 'vue'
import { fetchInbox } from '@/api/post'
import { useAuthStore } from '@/stores/auth.store'
import PostCard from '@/components/PostCard.vue'
import PostContent from '@/components/PostContent.vue'
import GithubActivity from '@/components/GithubActivity.vue'
import {getId} from '@/helpers/id-utils'
// 'post/'+post.id.split('/').slice(post.id.split('/').length-1,post.id.split('/').length).join().replace(/,/g,'/')
const store = useAuthStore()
const posts = ref([])

const loadPosts = async (authorId) => {
  posts.value = await fetchInbox(authorId, null);
}

onMounted(async () => {
  if (store.user) {
    await loadPosts(store.user.author.id)
  }
})

watch(
  () => store.user,
  async (newUser) => {
    if (newUser && newUser.author) {
      await loadPosts(newUser.author.id)
    }
  }
)
</script>

<template>
  <div class="feed">
    <div style="position:static;" class="feedBar">
    <v-btn onclick="document.getElementById('posts').scrollIntoView();" class="btn">Posts</v-btn>
    <v-btn onclick="document.getElementById('git').scrollIntoView();" class="btn">Github Activity</v-btn>
  </div>
  <h3>Posts</h3>
    <div class="posts" id="posts">
      
      <div v-if="posts && posts.length" class="all">
        <div v-for="post in posts" :key="post.id" >
          <div v-if="!post.unlisted" class="post">
          <h4>
            <router-link :to="{ name: 'post', params: { id: getId(post.id) } }">{{
              post.title
            }}</router-link>
          </h4>

          <h5 v-if="post.contentType === 'image/png;base64' || post.contentType === 'image/jpeg;base64'">
            <img v-bind:src='post.content' :alt="post.description" id="postImage"></h5>
          <h5 v-else id="content">{{ post.content }}</h5>
          <h5>{{ post.count }} Comments</h5>
        </div>
        </div>
      </div>
      <p v-else>No posts are available.</p>
    </div>
    <div class="github" id="git">
      <h3>Github Activity</h3>
      <github-activity />
    </div>
  </div>
</template>

<style scoped>
.posts {
  display: flex;
  flex-direction: row;
  background-color: transparent;
}
.all {
  background-color: transparent;
  flex: 1;
}
.post {
  background-color: #8565b948;
  border: 3px solid #8565b996;
  max-width: 446px;
  min-width: 25vw;
  margin-top: 5px;
}

#content {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: '... click title to view!';
  max-width: 400px;
  font-style: italic;
  color: white;
}
#cont {
  color: rgb(0, 0, 0);
  font-style: normal;
}
a {
  color: #6719e3;
  font-weight: 100;
}
a:hover {
  color: #ffffff;
}
h4,
h5 {
  background-color: #8565b900;
}
h3 {
  background-color: inherit;
  
  font-size: calc(10px + 1.75vw);
  font-variant: small-caps;
  text-decoration: underline black 2px;
}
.feed {
  background-color: transparent;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.feedBar{
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
#postImage{
  max-width: 100px;
  max-height: 100px;
  margin-left: 10px;
  border-radius: 10px;
  border: 3px solid rgba(0, 0, 0, 0);
}
</style>
