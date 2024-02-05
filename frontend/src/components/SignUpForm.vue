<script setup>
import { useForm, useField } from 'vee-validate'
import * as yup from 'yup'
import { checkUsername, signUp } from '@/api/signup'
import { useRouter } from 'vue-router'
import { computed } from 'vue'

const schema = yup.object().shape({
  username: yup
    .string()
    .required()
    .test('unique-username', 'Username is already taken', checkUsername),
  github: yup
    .string()
    .matches(
      /(^https:\/\/github\.com\/[a-zA-Z0-9-]+$)|(^$)/,
      'Enter a valid GitHub profile URL or username'
    ),
  password1: yup.string().required().min(8, 'Must be at least 8 characters'),
  password2: yup.string().oneOf([yup.ref('password1')], 'Passwords must match')
})

const { handleSubmit, isSubmitting, errors } = useForm({ validationSchema: schema })

const { value: username } = useField('username')
const { value: github } = useField('github')
const { value: password1 } = useField('password1')
const { value: password2 } = useField('password2')

const router = useRouter()

const onSubmit = async (values) => {
  await signUp(values)
  router.push({ name: 'login' })
}
const submitForm = handleSubmit(onSubmit)

const canSend = computed(() => {
  return Object.keys(errors.value).length === 0 && !isSubmitting.value
})
</script>

<template>
  <div class="signup-prompts container mt-5">
    <h2 class="mb-4">Sign up</h2>
    <form @submit.prevent="submitForm" class="needs-validation" novalidate>
      <div class="mb-3">
        <label for="id_username" class="form-label">Username:</label>
        <input
          type="text"
          class="form-control"
          data-vv-delay="1000"
          :class="{ 'is-invalid': errors.username }"
          id="id_username"
          v-model="username"
        />
        <div class="invalid-feedback">{{ errors.username }}</div>
        <small class="form-text text-muted">Enter a unique username</small>
      </div>

      <div class="mb-3">
        <label for="id_github" class="form-label">Github:</label>
        <input
          type="text"
          id="id_github"
          class="form-control"
          name="github"
          :class="{ 'is-invalid': errors.github }"
          v-model="github"
        />
        <div class="invalid-feedback">{{ errors.github }}</div>
        <small class="form-text text-muted">Optional</small>
      </div>

      <div class="mb-3">
        <label for="id_password1" class="form-label">Password:</label>
        <input
          type="password"
          id="id_password1"
          class="form-control"
          name="password1"
          required
          :class="{ 'is-invalid': errors.password1 }"
          v-model="password1"
        />
        <div class="invalid-feedback">{{ errors.password1 }}</div>
        <small class="form-text text-muted">
          <ul>
            <li>Your password can’t be too similar to your other personal information.</li>
            <li>Your password must contain at least 8 characters.</li>
            <li>Your password can’t be a commonly used password.</li>
            <li>Your password can’t be entirely numeric.</li>
          </ul>
        </small>
      </div>

      <div class="mb-3">
        <label for="id_password2" class="form-label">Password confirmation:</label>
        <input
          type="password"
          id="id_password2"
          class="form-control"
          name="password2"
          required
          :class="{ 'is-invalid': errors.password2 }"
          v-model="password2"
        />
        <div class="invalid-feedback">{{ errors.password2 }}</div>
        <small class="form-text text-muted"
          >Enter the same password as before, for verification.</small
        >
      </div>

      <button type="submit" class="btn" :disabled="!canSend">
        <span v-if="isSubmitting">Submitting...</span>
        <span v-else>Sign Up</span>
      </button>
    </form>
    <div class="mt-4">
      <h4>Already have an account?</h4>
      <router-link to="/login">Log In</router-link>
    </div>
  </div>
</template>

<style scoped>
.btn {
  color: #f9ecfd;
  background-color: #8565b9;
  border-color: #8565b9;
  font-size: calc(8px + 0.5vw);
  min-width: fit-content;
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
a {
  color: #8565b9;
}
</style>
