import { createRouter, createWebHistory } from 'vue-router'
import ShowcaseView from '../views/ShowcaseView.vue'
import AdminView from '../views/AdminView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'showcase', component: ShowcaseView },
    { path: '/admin', name: 'admin', component: AdminView }
  ]
})

export default router
