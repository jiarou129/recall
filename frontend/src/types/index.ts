// 与后端 schemas 对应的前端类型
export type Mastery = 'unmastered' | 'reviewing' | 'mastered'

export interface Category {
  id: number
  name: string
  color: number // 1-8
  count: number
}

export interface Mistake {
  id: number
  category_id: number | null
  category_name: string | null
  category_color: number
  question: string
  answer: string
  source: string
  subject: string
  knowledge_point: string
  review_count: number
  mastery: Mastery
  snooze_until: string
  created_at: string
  updated_at: string
}

export interface ChatSession {
  id: number
  title: string
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: number
  session_id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface Settings {
  model_name: string
  api_key: string
  base_url: string
}

export interface DashboardStats {
  total_questions: number
  total_reviews: number
  success_rate: number
  pending_review: number
  study_series: { date: string; count: number }[]
  entry_series: { date: string; count: number }[]
  by_subject: { subject: string; count: number }[]
}

export interface HelpDoc {
  title: string
  intro: string
  sections: { title: string; body: string }[]
}
