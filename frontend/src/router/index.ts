import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue'), meta: { title: '错题集' } },
    { path: '/chat', name: 'chat', component: () => import('@/views/ChatView.vue'), meta: { title: 'AI 答疑' } },
    { path: '/dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue'), meta: { title: '数据看板' } },
    { path: '/settings', name: 'settings', component: () => import('@/views/SettingsView.vue'), meta: { title: '模型设置' } },
    { path: '/help', name: 'help', component: () => import('@/views/HelpView.vue'), meta: { title: '帮助中心' } },
  ],
})

export default router
