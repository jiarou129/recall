import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// Recall AI 前端构建配置
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: true, // 绑定 0.0.0.0，避免仅监听 IPv6 [::1] 导致部分环境/预览面板无法访问
    port: 5173,
    proxy: {
      // 开发期将 /api 代理到 FastAPI 后端（后端路由本身带 /api 前缀，直接透传）
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
