import { createRouter, createWebHistory } from 'vue-router'

// Lazy-load all route components for code splitting
const routes = [
  {
    path: '/',
    name: 'map',
    component: () => import('@/views/MapView.vue'),
    meta: { tab: 'map' }
  },
  {
    path: '/list',
    name: 'list',
    component: () => import('@/views/ListView.vue'),
    meta: { tab: 'list' }
  },
  {
    path: '/library',
    name: 'library',
    component: () => import('@/views/LibraryView.vue'),
    meta: { tab: 'library' }
  },
  {
    path: '/contribute',
    name: 'contribute',
    component: () => import('@/views/ContributeView.vue'),
    meta: { tab: 'contribute' }
  },
  {
    path: '/book/:id',
    name: 'book-detail',
    component: () => import('@/views/BookDetailView.vue'),
  },
  {
    path: '/book/:id/journey',
    name: 'book-journey',
    component: () => import('@/views/BookJourneyView.vue'),
  },
  {
    path: '/author/:name',
    name: 'author-profile',
    component: () => import('@/views/AuthorProfileView.vue'),
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
