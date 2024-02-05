<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import PostCard from '@/components/PostCard.vue'
import { requestFollowAuthor, unfollowAuthor } from '@/api/friendRequest'
import { useAuthStore } from '@/stores/auth.store'
import GithubActivity from '@/components/GithubActivity.vue'
import {getId} from '@/helpers/id-utils'
import { getMarkdownHTML } from '@/api/post';

const route = useRoute()
const author = ref(null)
const posts = ref([])
// Should be set based on current user info
const currentUser = useAuthStore()

const loadData = async () => {
  // const arr = route.params.id.split('/')
  // const authorId = arr[arr.length-1]
  const authorId = route.params.id;
  const authorResponse = await fetchWrapper.get(`/api/local/authors/${route.params.id}`)
  const postsResponse = await fetchWrapper.get(`/api/authors/${authorId}/profile`)
  const authorData = await authorResponse.json()
  const postsData = await postsResponse.json()
  author.value = authorData
  posts.value = postsData
}



watch(
  () => route.params,
  async () => {
    await loadData()
  }
)

onMounted(async () => {
  await loadData()
})

const followAuthor = async () => {
  await requestFollowAuthor(getId(author.value.id))
}

const unfollow = async () => {
  await unfollowAuthor(getId(author.value.id))
  author.value.followers = author.value.followers.filter((x)=> x.id !== currentUser.user.author.id);
}
</script>

<template>
  <div v-if="author">
    <div class="user-profile" v-if="author">
      <img :src="author.profileImage" alt="user profile image" width="200" height="200" id="pic" />
      <h1 id="disp">{{ author.displayName }}'s profile</h1>
      <h4 id="bio">{{ author.bio }}</h4>
    </div>
    <a id="git" :href="author.github" v-if="author.github">Check {{ author.displayName }} out on Github!</a>
    <div class="sideby">

    
    <div class="posts">
      <h4>{{author.displayName}}'s Posts:</h4>
      <div v-if="posts?.length">
        <div v-for="post in posts" :key="post.id" :post="post" class="postCard">
          <div v-if="post.unlisted && author.id === currentUser.currentUser?.author?.id || !post.unlisted">
          <h4>
            <router-link :to="{name: 'post', params: {id: getId(post.id)}}">{{
              post.title
            }}</router-link>
          </h4>
          <h5 v-if="post.contentType == 'image/png;base64' || post.contentType == 'image/jpeg;base64'">
            <img v-bind:src='post.content' :alt="post.description" id="postImage"></h5>
          <h5 id="content"
            v-else-if="post.contentType === 'text/markdown'"
            v-html="getMarkdownHTML(post.content)"
          ></h5>
          <h5 v-else id="content">{{ post.content }}</h5>
          <h5 >{{ post.count }} Comments</h5>
          </div>
        </div>
          <!-- <PostCard v-for="post in posts" :key="post.id" :post="post" class="post"/> -->
        
      </div>
      <p v-else>{{author.displayName}} has no posts yet.</p>
    </div>

    <div class="followers" v-if="author">
      <h4>{{author.followers.length}} Followers:</h4>
      <ul>
        <li v-for="follower in author.followers" :key="follower.id">
          <router-link :to="{ name: 'profile', params: { id: follower.id } }">{{
            follower.displayName
          }}</router-link>
        </li>
      </ul>
    </div>
  </div>
    <div v-if="author && (author.id !== currentUser.currentUser?.author?.id)">
      <button v-if="currentUser && author.followers.map((x)=>x.id).includes(currentUser.user.author.id)" class="btn btn-info" @click="unfollow">Unfollow</button>
      <button v-else class="btn btn-info" @click="followAuthor">Follow</button>
    </div>
  </div>
</template>

<style scoped>

.posts{
  flex: 1;
  justify-content: left;
  align-self: left;
  border: 6px solid #8758938f;

  padding: 1em;
  background-color: #dbd3e8;
  border-radius: 8px;
  margin-right: 10px;
  min-height:200px;
  max-height: 500px;
  overflow-y: scroll;
  scrollbar-color: rgba(81, 6, 129, 0.559) transparent;
  
}
.followers{
  background-color: #dbd3e8;
  flex: 1;
  align-self: right;
  border: 6px solid #61386b8f;
  border-radius: 8px;
  margin-left: 10px;
  scrollbar-color: rgba(81, 6, 129, 0.559) transparent;
  max-height: 500px;
  max-width: 200px;
  overflow-y: scroll;
}
.sideby {
  display: flex;
  min-height: 200px;
}

#content {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ' ... (click post title to view entire post)';
  max-width: 600px;
  color: #6719e3;
}
a {
  color: #6719e3;
  font-weight: 100;
}
a:hover {
  color: #4f3d6c;
  font-weight: 100;
}
#pic {
  width: 200px;
  height: 200px;
  justify-content: center;
  align-self: center;
  padding-bottom: 10;
  border-radius: 30px;
  border: 3px outset rgb(0, 0, 0);
}
#git{
  font-size: 150%;
}
.user-profile{
  display: flex;
  align-items: flex-end;
}
#disp{
  font-weight: bold;
  margin-left: 50px;
  margin-bottom:82px;
  height: fit-content;
  width: 100%;
  padding: 3px;
  border-color: #8758938f;
  border-radius: 10px;
}

li {
  background-color: inherit;
  font-size: large;
  padding: 8px;
  list-style-type: '\26B9';
}
h4{
  font-weight: bold;
}

.postCard{
  margin-left: 5px;
  margin-bottom: 5px;
  border-left: #58935a;
  border-width: 10px;
  border-radius: 5px;
  border-style: solid;
  border-bottom: none;
  border-top: none;
  border-right: none;

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

#postImage
{
  max-width: 100px;
  max-height: 100px;
  margin-left: 10px;
  border-radius: 10px;
  border: 3px solid rgba(0, 0, 0, 0);
}
</style>