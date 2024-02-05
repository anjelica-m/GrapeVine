<script setup>
import { Form, Field } from 'vee-validate'
import * as Yup from 'yup'
import { useAuthStore } from '@/stores/auth.store'

const schema = Yup.object().shape({
  username: Yup.string().required('Username is required'),
  password: Yup.string().required('Password is required')
})

function onSubmit(values, { setErrors }) {
  const authStore = useAuthStore()
  const { username, password } = values

  return authStore.login(username, password).catch((error) => setErrors({ apiError: error }))
}
</script>
import { createApp } from 'vue' createApp({ data() { return { btnClass: "button", } }, methods:{
toggleColor() { if(this.btnClass === "but") { this.btnClass = "clicked"; } else { this.btnClass =
"but"; } } } }).mount('#app')

<template>
  <div id="login">
    <h2>Login</h2>
    <Form @submit="onSubmit" :validation-schema="schema" v-slot="{ errors, isSubmitting }">
      <div class="form-group">
        <label>Username</label>
        <Field
          name="username"
          type="text"
          class="form-control"
          :class="{ 'is-invalid': errors.username }"
        />
        <div class="invalid-feedback">{{ errors.username }}</div>
      </div>
      <div class="form-group">
        <label>Password</label>
        <Field
          name="password"
          type="password"
          class="form-control"
          :class="{ 'is-invalid': errors.password }"
        />
        <div class="invalid-feedback">{{ errors.password }}</div>
      </div>
      <div class="form-group">
        <th>
          <button class="btn" :disabled="isSubmitting">
            <span v-show="isSubmitting" class="spinner-border spinner-border-sm mr-1"></span>
            Login
          </button>
        </th>
      </div>
      <div v-if="errors.apiError" class="alert alert-danger mt-3 mb-0">{{ errors.apiError }}</div>
    </Form>
    <h4>New to Grapevine?</h4>
    <router-link :to="{ name: 'signup' }" id="signup">Create an Account</router-link>
  </div>
</template>

<style scoped>
.btn {
  color: #f9ecfd;
  background-color: #8565b9;
  border-color: #8565b9;
}
.btn:hover {
  color: #f8f8f8;
  background-color: #58935a;
  border-color: #58935a;
}
.btn:active {
  color: #8565b9;
  background-color: #cfa9db;
  border-color: #cfa9db;
}
.btn:focus,
.btn.focus {
  outline: none !important;
  box-shadow: none !important;
  color: #8565b9;
  background-color: #cfa9db;
  border-color: #cfa9db;
}
#signup {
  color: #8565b9;
}
</style>
