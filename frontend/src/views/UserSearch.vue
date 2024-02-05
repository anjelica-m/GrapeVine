<script setup>
import {getId} from '@/helpers/id-utils'
import { ref, watch } from 'vue'
import { fetchWrapper } from '@/helpers/fetch-wrapper'
import { debounce } from 'lodash' // your fetch wrapper

const searchQuery = ref('')
const foundAuthors = ref([])

const searchAuthors = async () => {
  if (!searchQuery.value) {
    foundAuthors.value = []
    return
  }

  try {
    const response = await fetchWrapper.get(`/api/search?username=${searchQuery.value}`)
    foundAuthors.value = (await response.json())['items']
  } catch (error) {
    console.error('Error fetching users:', error)
    foundAuthors.value = []
  }
}

const debouncedFetchUsers = debounce(searchAuthors, 500)

watch(searchQuery, debouncedFetchUsers)
</script>

<template>
  <div class="container mt-5">
    <h1 class="mb-4 text-center">Search for Authors</h1>
    <div class="input-group mb-3">
      <span class="input-group-text"><i class="bi bi-search"></i></span>
      <input
        v-model="searchQuery"
        type="text"
        class="form-control"
        placeholder="Type here to search for authors..."
        aria-label="Author's username"
      />
    </div>

    <div v-if="foundAuthors.length > 0">
      <ul class="list-group">
        <li v-for="author in foundAuthors" :key="author.id" class="list-group-item">
          <router-link :to="{ name: 'profile', params: { id: getId(author.id) } }">{{
            author.displayName
          }}</router-link>
        </li>
      </ul>
    </div>
    <p v-else class="text-center mt-4">No matching authors found, try again.</p>
  </div>
</template>

<style scoped>
.search-container {
  max-width: 600px;
  margin: auto;
  padding: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.search-input {
  width: 100%;
  padding: 10px 15px;
  margin-bottom: 20px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 16px;
}

.user-list-container {
  background-color: #f9f9f9;
  border-radius: 4px;
  padding: 10px;
}

.user-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.user-item {
  background-color: #ffffff;
  margin-bottom: 10px;
  padding: 10px 15px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: background-color 0.3s;
}

.user-item:hover {
  background-color: #e9e9e9;
}

.no-users-message {
  text-align: center;
  color: #666;
}
</style>
