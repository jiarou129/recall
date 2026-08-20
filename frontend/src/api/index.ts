import axios from 'axios'
import type {
  Category,
  ChatMessage,
  ChatSession,
  DashboardStats,
  HelpDoc,
  Mistake,
  Settings,
} from '@/types'

const http = axios.create({ baseURL: '/api', timeout: 60000 })

// ---------------- 错题 ----------------
export const mistakesApi = {
  list: (params?: { category_id?: number; subject?: string; status?: string; q?: string }) =>
    http.get<Mistake[]>('/mistakes', { params }).then((r) => r.data),
  get: (id: number) => http.get<Mistake>(`/mistakes/${id}`).then((r) => r.data),
  create: (data: Partial<Mistake>) => http.post<Mistake>('/mistakes', data).then((r) => r.data),
  update: (id: number, data: Partial<Mistake>) =>
    http.put<Mistake>(`/mistakes/${id}`, data).then((r) => r.data),
  remove: (id: number) => http.delete(`/mistakes/${id}`),
  review: (id: number) => http.post<Mistake>(`/mistakes/${id}/review`).then((r) => r.data),
  semantic: (q: string, n = 5) =>
    http.post<Mistake[]>('/mistakes/semantic', { q, n }).then((r) => r.data),
  exportPdf: async (ids?: number[]) => {
    try {
      const url = ids && ids.length ? `/mistakes/export?ids=${ids.join(',')}` : `/mistakes/export`
      const r = await http.get<Blob>(url, { responseType: 'blob' })
      const blob = new Blob([r.data], { type: 'application/pdf' })
      if (!blob.size) throw new Error('导出内容为空')
      const objectUrl = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = objectUrl
      a.download = `recall-mistakes-${new Date().toISOString().slice(0, 10)}.pdf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(objectUrl)
    } catch (e) {
      console.error('导出失败', e)
      alert('导出失败，请稍后重试')
    }
  },
  snooze: (id: number, days?: number) =>
    http.post<Mistake>(`/mistakes/${id}/snooze`, days ? { days } : undefined).then((r) => r.data),
}

// ---------------- 分类 ----------------
export const categoriesApi = {
  list: () => http.get<Category[]>('/mistakes/categories').then((r) => r.data),
  create: (data: { name: string; color: number }) =>
    http.post<Category>('/mistakes/categories', data).then((r) => r.data),
  update: (id: number, data: { name: string; color: number }) =>
    http.put<Category>(`/mistakes/categories/${id}`, data).then((r) => r.data),
  remove: (id: number) => http.delete(`/mistakes/categories/${id}`),
}

// ---------------- 对话 ----------------
export const chatApi = {
  sessions: () => http.get<ChatSession[]>('/chat/sessions').then((r) => r.data),
  createSession: (title = '新对话') =>
    http.post<ChatSession>('/chat/sessions', null, { params: { title } }).then((r) => r.data),
  messages: (sid: number) =>
    http.get<ChatMessage[]>(`/chat/sessions/${sid}/messages`).then((r) => r.data),
  send: (sid: number, content: string) =>
    http.post<ChatMessage[]>(`/chat/sessions/${sid}/messages`, { content }).then((r) => r.data),
  remove: (sid: number) => http.delete(`/chat/sessions/${sid}`),
  // 根据题干生成 AI 解析（推理较慢且不稳定，超时放宽到 180s）
  solve: (question: string) =>
    http.post<{ answer: string; available: boolean }>('/chat/solve', { question }, { timeout: 180000 }).then((r) => r.data),
}

// ---------------- 看板 ----------------
export const dashboardApi = {
  stats: () => http.get<DashboardStats>('/dashboard/stats').then((r) => r.data),
}

// ---------------- 设置 ----------------
export const settingsApi = {
  get: () => http.get<Settings>('/settings').then((r) => r.data),
  update: (data: Settings) => http.put<Settings>('/settings', data).then((r) => r.data),
}

// ---------------- 上传 OCR ----------------
export const uploadApi = {
  ocr: async (file: File) => {
    const form = new FormData()
    form.append('file', file)
    // OCR 走 AI 视觉识别，冷启动可能较慢，超时放宽到 120s
    const r = await http.post<{ available: boolean; text: string; message: string }>(
      '/upload/ocr',
      form,
      { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 120000 },
    )
    return r.data
  },
}

// ---------------- 帮助 ----------------
export const helpApi = {
  doc: () => http.get<HelpDoc>('/help').then((r) => r.data),
}
