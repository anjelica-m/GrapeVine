<script setup>
import {getId} from '@/helpers/id-utils'
import { computed, ref, onMounted } from 'vue'
import { createPost, fetchPost, updatePost } from '@/api/post'
import { useRouter, useRoute } from 'vue-router'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import { debounce } from 'lodash' // your fetch wrapper

const title = ref('')
const description = ref('')
const content = ref('')
const categories = ref('')
const visibility = ref('PUBLIC')
const private_receiver = ref('')
const unlisted = ref(false)
const router = useRouter()
const route = useRoute()

const postContentTypes = ref([
  ['plain', 'Plain Text'],
  ['markdown', 'CommonMark'],
  ['image', 'Image']
])



const selectedContentType = ref('plain')
const imageContentType = ref('')
const fileInfo = ref('')

const contentType = computed(() => {
  if (selectedContentType.value === 'plain') return 'text/plain'
  if (selectedContentType.value === 'markdown') return 'text/markdown'
  if (selectedContentType.value === 'image') return `${imageContentType.value};base64`
  return ''
})

const handleSubmit = async () => {
  let postData;

  if (visibility.value !== "PRIVATE") {
    postData = {
      title: title.value,
      description: description.value,
      contentType: contentType.value,
      content: content.value,
      categories: categories.value,
      visibility: visibility.value,
      private_receiver: null,
      unlisted: unlisted.value
    };
  }
  else {
    postData = {
      title: title.value,
      description: description.value,
      contentType: contentType.value,
      content: content.value,
      categories: categories.value,
      visibility: visibility.value,
      private_reciever: private_receiver.value,
      unlisted: unlisted.value
    };
    console.log("receiver: " + private_receiver.value)
  }

  // const post = await createPost(postData)
  // router.push({ name: 'post', params: { id: post.id } })
  let post;

  if (route.name === 'post-update'){
    post = await updatePost(route.params.id, postData);
  } else {
    post = await createPost(postData);
  }
  router.push({name: "post", params: {id: getId(post.id)}})
}

const onFileSelected = (event) => {
  const file = event.target.files[0]
  imageContentType.value = file.type
  const reader = new FileReader()
  reader.onload = (e) => {
    content.value = e.target.result
  }
  reader.readAsDataURL(file)
}


onMounted(async () => {
  if (route.name === 'post-update'){
    const postData = await fetchPost(route.params.id)
    title.value = postData.title
    description.value = postData.description
    contentType.value = postData.contentType
    if (contentType.value === 'image/jpeg' || contentType.value === 'image/png'){
      document.getElementById("id_content-type").value = 'image'}
    content.value = postData.content
    categories.value = postData.categories
    visibility.value = postData.visibility
    unlisted.value = postData.unlisted
  }
  await loadData()
})


const authors = ref([])

const loadData = async () => {
  const response = await fetchWrapper.get('api/local/authors/')
  const data = await response.json()
  authors.value = data
}
</script>

<template>
  <form
    @submit.prevent="handleSubmit"
    method="POST"
    enctype="multipart/form-data"
    class="container mt-5"
    autocomplete="off"
  >
    <div class="mb-3">
      <label for="id_title" class="form-label">Title:</label>
      <input
        v-model="title"
        type="text"
        class="form-control"
        name="title"
        maxlength="50"
        required
        id="id_title"
      />
    </div>

    <div class="mb-3">
      <label for="id_description" class="form-label">Description:</label>
      <input
        v-model="description"
        type="text"
        class="form-control"
        name="description"
        maxlength="200"
        required
        id="id_description"
      />
    </div>

    <div class="mb-3">
      <label for="id_content-type" class="form-label">Content Type:</label>
      <select
        class="form-select"
        name="contentType"
        id="id_content-type"
        v-model="selectedContentType"
      >
        <option v-for="ct in postContentTypes" :value="ct[0]" :key="`ct-${ct}`">{{ ct[1] }}</option>
      </select>
    </div>

    <div class="mb-3" v-if="selectedContentType === 'image'">
      <label for="id_content" class="form-label">Attach image</label>
      <input type="file" id="id_content" accept="image/png, image/jpeg" @change="onFileSelected" />
      <p id="fileInfo">{{ fileInfo }}</p>
    </div>
    <div class="mb-3" v-else>
      <label for="id_content" class="form-label">Content:</label>
      <textarea
        v-model="content"
        class="form-control"
        name="content"
        maxlength="600"
        required
        id="id_content"
      ></textarea>
    </div>

    <div class="mb-3">
      <label for="id_categories" class="form-label">Categories:</label>
      <input
        v-model="categories"
        type="text"
        class="form-control"
        name="categories"
        maxlength="200"
        required
        id="id_categories"
      />
    </div>

    <div class="mb-3">
      <label for="id_visibility" class="form-label">Visibility:</label>
      <select v-model="visibility" class="form-select" name="visibility" id="id_visibility">
        <option value="PUBLIC">Public</option>
        <option value="PRIVATE">Private</option>
        <option value="FRIENDS_ONLY">Friends Only</option>
      </select>
    </div>

    <div class="mb-3" v-if="visibility === 'PRIVATE'">
      <label for="id_private_receiver" class="form-label">Private Post Receiver</label>
      <select
        v-model="privateReceiver"
        type="text"
        class="form-control"
        id="id_private_receiver">
        <option v-for="author in authors" :value="author.id">{{ author.displayName }}</option>
      </select>
    </div>

    <div class="mb-3 form-check">
      <input
        v-model="unlisted"
        type="checkbox"
        class="form-check-input"
        name="unlisted"
        id="id_unlisted"
      />
      <label class="form-check-label" for="id_unlisted">Unlisted?</label>
      <span class="checkmark"></span>
    </div>
    <button type="submit" class="btn">Create Post</button>
  </form>
</template>

<style scoped>
input,
textarea {
  border-color: #78b38b4d;
  border-width: medium;
  outline: none !important;
  box-shadow: none !important;
}
::selection,
::-moz-selection,
::-webkit-selection {
  background: #997fed74;
  color: #311672;
}
.btn {
  color: #f9ecfd;
  background-color: #8565b9;
  border-color: #8565b9;
}

.btn:hover,
.btn:active {
  color: #f8f8f8;
  background-color: #58935a;
  border-color: #58935a;
}
select {
  border-radius: 10px;
  border-color: #58935a6c;
  width: 127px;
}
input:checked {
  background-color: #8565b9;
}
</style>
