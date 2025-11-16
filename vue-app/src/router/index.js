import { createRouter, createWebHistory } from 'vue-router'
import MapView from '@/views/MapView.vue'
import ListView from '@/views/ListView.vue'
import LibraryView from '@/views/LibraryView.vue'
import ContributeView from '@/views/ContributeView.vue'
import BookDetailView from '@/views/BookDetailView.vue'
import AuthorProfileView from '@/views/AuthorProfileView.vue'

const routes = [
  {
    path: '/',
    name: 'map',
    component: MapView,
    meta: { tab: 'map' }
  },
  {
    path: '/list',
    name: 'list',
    component: ListView,
    meta: { tab: 'list' }
  },
  {
    path: '/library',
    name: 'library',
    component: LibraryView,
    meta: { tab: 'library' }
  },
  {
    path: '/contribute',
    name: 'contribute',
    component: ContributeView,
    meta: { tab: 'contribute' }
  },
  {
    path: '/book/:id',
    name: 'book-detail',
    component: BookDetailView,
  },
  {
    path: '/author/:name',
    name: 'author-profile',
    component: AuthorProfileView,
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
