import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/camera',
    name: 'Camera',
    component: () => import('@/views/CameraDetection.vue')
  },
  {
    path: '/video',
    name: 'Video',
    component: () => import('@/views/VideoDetection.vue')
  },
  {
    path: '/image',
    name: 'Image',
    component: () => import('@/views/ImageDetection.vue')
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/DetectionHistory.vue')
  },
  {
    path: '/evaluation',
    name: 'Evaluation',
    component: () => import('@/views/EvaluationHistory.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
