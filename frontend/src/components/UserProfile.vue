<script setup>
const props = defineProps(['author'])
const author = props.author
</script>

<template>
  <div class="user-profile">
    <!-- Note: remove hardcoded properties for image -->

    <img :src="author.profileImage" alt="user profile image" width="100" height="100" />

    <h1 id="disp">{{ author.displayName }}</h1>
    <a id="git" href="{{ author.github }}">Check me out on Github</a>

    <h4 id="bio">{{ author.bio }}</h4>
  </div>
</template>

<style scoped></style>
