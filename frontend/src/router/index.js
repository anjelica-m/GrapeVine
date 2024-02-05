import { createRouter, createWebHashHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth.store'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import UserSearch from '@/views/UserSearch.vue'
import ProfileView from '@/views/ProfileView.vue'
import PostCreateView from '@/views/PostCreateView.vue'
import SignUpView from '@/views/SignUpView.vue'
import PostView from '@/views/PostView.vue'
import PostUpdateView from '@/views/PostUpdateView.vue'

export const router = createRouter({
  history: createWebHashHistory(),
  linkActiveClass: 'active',
  routes: [
    { path: '/', component: HomeView, name: 'home' },
    { path: '/login', component: LoginView, name: 'login' },
    { path: '/search', component: UserSearch, name: 'search' },
    { path: '/profile/:id', component: ProfileView, name: 'profile' },
    { path: '/post/:id', component: PostView, name: 'post' },
    { path: '/post/:id/update', component: PostUpdateView, name: 'post-update' },
    { path: '/create-post', component: PostCreateView, name: 'create-post' },
    { path: '/settings', component: HomeView, name: 'settings' },
    { path: '/signup', component: SignUpView, name: 'signup' }
  ]
})

router.beforeEach(async (to, from, next) => {
  // redirect to login page if not logged in and trying to access a restricted page
  const publicPages = ['/login', '/signup']
  const authRequired = !publicPages.includes(to.path)
  const auth = useAuthStore()

  if (authRequired && !auth.authenticated) {
    auth.returnUrl = to.fullPath
    next('/login')
  } else {
    next()
  }
})

export default router
