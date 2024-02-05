<script setup>
import { useAuthStore } from '@/stores/auth.store'
import { computed, onMounted, ref, watch } from 'vue'
import { formatEvent } from '../helpers/github'

const auth = useAuthStore()

const items = ref([])

const messages = computed(() => {
  return items.value.map((e) => formatEvent(e))
})

const fetchGithubActivity = async (username) => {
  const resp = await fetch(`https://api.github.com/users/${username}/events`, {
    headers: {
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
    }
  })
  const data = await resp.json()
  items.value = [...data]
}

watch(
  () => auth.user,
  async () => {
    fetchGithubActivity(auth.githubUsername)
  }
)

onMounted(async () => {
  if (auth.githubUsername) {
    fetchGithubActivity(auth.githubUsername)
  }
})
</script>

<template>
  <div v-if="auth.githubUsername != null">
    <p v-for="(message, index) in messages" :key="`message-${index}`" v-html="message" />
  </div>
  <div v-else>
    <p>There is no github username associated with your account.</p>
  </div>
</template>

<style scoped></style>
