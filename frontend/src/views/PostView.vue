<script setup>
import { onMounted, reactive, ref } from 'vue'
import {
  fetchPost,
  fetchComments,
  likePost,
  createComment,
  unlikePost,
  likeComment,
  unlikeComment,
  sharePost,
  updatePost,
  deletePost
} from '@/api/post' // assuming that createComment function exists in the API
import { useRoute, useRouter } from 'vue-router'
import PostCard from '@/components/PostCard.vue'
import CommentCard from '@/components/CommentCard.vue'
import { useAuthStore } from '@/stores/auth.store'
import { RouterLink } from 'vue-router'
import {getId} from '@/helpers/id-utils'


const auth = useAuthStore()
const route = useRoute()
const post = ref({})
const comments = ref([])
const newComment = ref('') // for storing the new comment
const router = useRouter()

// Function to add comment
const addComment = async () => {
  const authorId = getId(auth.user.author.id);
  const response = await createComment(authorId, getId(route.params.id), newComment.value)
  response.like_count = 0
  comments.value.push(response)
  newComment.value = '' // reset the input field
  post.value.comment_count++;
}

const onPostLike = async (postId) => {
  await likePost(postId)
  await reloadPost()
}

const onPostUnlike = async (postId) => {
  await unlikePost(postId)
  await reloadPost()
}

const reloadPost = async () => {
  post.value = await fetchPost(route.params.id)
  comments.value = await fetchComments(route.params.id)
}

const onLikeComment = async (comment) => {
  await likeComment(getId(comment.id))
  //await reloadPost();
  updateComment(comment, { liked_by_me: true, like_count: comment.like_count + 1 })
}

const onDelete = async () => {
  await deletePost(route.params.id)
  router.push({"name": "home"})
}

const onUpdate = async (content) => {
  await updatePost(route.params.id, content);
}

// const onUnlikeComment = async (comment) => {
//   await unlikeComment(comment.id);
//   //await reloadPost();
//   updateComment(comment, {liked_by_me: false, like_count: comment.like_count - 1})
// }

const updateComment = (existingComment, newData) => {
  const index = comments.value.findIndex((c) => c.id === existingComment.id)
  if (index !== -1) {
    comments.value = [
      ...comments.value.slice(0, index),
      { ...comments.value[index], ...newData },
      ...comments.value.slice(index + 1)
    ]
  }
}



onMounted(async () => {
  await reloadPost()
})
</script>

<template>
  
  <div class="post" v-if="post">
    <div>
      <PostCard :post="post" />
    </div> 
    <i v-if="!post.liked_by_me" class="bi bi-hand-thumbs-up" @click="onPostLike(post.id)"> Like</i>
    <i v-else class="bi bi-hand-thumbs-up-fill" id="liked"> Liked</i>
    <button class="btn" @click="sharePost(post)" v-if="!post.unlisted">Share</button>
    <h3 id="commentTitle">Comments</h3>
    <div class="commentSection">
      <div id="commentSection" v-if="comments.length > 0">
        <CommentCard
          id="comment"
          v-for="comment in comments"
          :comment="comment"
          :key="comment.id"
          @like-comment="onLikeComment(comment)"
        />
      </div>
      <div v-else><h3 id="none">No comments so far, be the first!</h3></div>
    </div>
    <div class="my-3">
      <p>Add comment:</p>
      <textarea
        v-model="newComment"
        class="form-control"
        placeholder="Write your comment..."
      ></textarea>
      <button id="cmt" class="btn" @click="addComment">Comment</button>
    </div>
    <div v-if="auth.currentUser?.author?.id === post.author.id" id="control">
      <div v-if="post.contentType === 'image/png;base64' || post.contentType === 'image/jpeg;base64'">
        <router-link to="{name: 'home'}" class="btn btn-danger" @click="onDelete" id="del">Delete Post</router-link>
      </div>
      <div v-else>

        <router-link id='edit' class="btn" :to="{name: 'post-update', params: {id: post.id}}">Edit Post</router-link>
        <router-link :to='{name: home}' class="btn btn-danger" @click="onDelete" id="del">Delete Post</router-link>
      </div>
    
    
    </div>
  </div>
</template>

<style scoped>
#cmt, .btn {
  color: #f9ecfd;
  background-color: #8565b9;
  border-color: #8565b9;
  font-size: calc(8px + 0.5vw);
  min-width: fit-content;
  margin-top: 5px;
  margin-right: 5px;
}

#cmt:hover, .btn:hover, #edit,
#edit:hover,
#edit:active,
#edit:focus {
  color: #f8f8f8;
  background-color: #58935a;
  border-color: #58935a;
}
#cmt:active, .btn:active {
  color: #f8f8f8;
  background-color: #58935a;
  border-color: #58935a;
}
#cmt:focus, .btn:focus,
#cmt.focus {
  outline: none !important;
  box-shadow: none !important;
  color: #f9ecfd;
  background-color: #8565b9;
  border-color: #8565b9;
}
p {
  font-size: large;
}
.my-3 {
  flex: 1;
  bottom: 0px;
  position: static;
}
textarea {
  width: calc(57vw- 500px);
  resize: none;
}
.post {
  display: flex;
  flex-direction: column;
  padding: 10px;
}
.commentSection {
  max-height: 300px;
  min-height: 100px;
  overflow-y: scroll;
  padding-top: 10px;
  padding-left: 10px;
  padding-bottom: 10px;
  border: 3px #58935a46 solid;
  background-color: #58935a29;
  scrollbar-color: #58935a transparent;
}

#none {
  background-color: #58935a00;
}
#commentTitle {
  justify-content: center;
  align-self: center;
  font-variant: small-caps;
}
#commentSection {
  background-color: transparent;
  background-size: contain;
}
#control{
  justify-content: flex-end;
  position: relative;
  padding-bottom: 10px;
  display: flex;
  align-items: right;
  justify-content: right;
  z-index: 10;
  padding-right: 5px;
}
</style>
