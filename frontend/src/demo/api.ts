// 演示模式数据 & API 桩
// 当构建时设置 VITE_DEMO=true（npm run build -- --mode demo），前端不再请求后端，
// 改用此处内置的 mock 数据渲染所有页面，让「在线展示链接」的访客看到的是成品界面，而非报错页。
import type {
  Category,
  ChatMessage,
  ChatSession,
  DashboardStats,
  HelpDoc,
  Mistake,
  Settings,
} from '@/types'

const DEMO_NOTICE = '这是演示版（静态托管，无后端）。该功能需要本地运行完整版或云端部署后才可用。'

function delay<T>(data: T, ms = 280): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(data), ms))
}

// ---------------- 分类 ----------------
export const categories: Category[] = [
  { id: 1, name: '数学', color: 1, count: 2 },
  { id: 2, name: '英语', color: 2, count: 1 },
  { id: 3, name: '物理', color: 3, count: 1 },
  { id: 4, name: '化学', color: 4, count: 1 },
  { id: 5, name: '高数', color: 6, count: 1 },
  { id: 6, name: '其他', color: 8, count: 0 },
]

// ---------------- 错题 ----------------
export const mistakes: Mistake[] = [
  {
    id: 1,
    category_id: 1,
    category_name: '数学',
    category_color: 1,
    question:
      '已知椭圆 $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1\\,(a>b>0)$ 的离心率为 $e=\\dfrac{\\sqrt{2}}{2}$，且过点 $(2,\\sqrt{2})$，求椭圆的标准方程。',
    answer:
      '**【思路】** 由离心率 $e=\\dfrac{c}{a}=\\dfrac{\\sqrt{2}}{2}$ 得 $a^2=2b^2$；再将已知点代入即可解出 $a^2,b^2$。\n\n**【解答】**\n由 $e=\\dfrac{c}{a}=\\dfrac{\\sqrt{2}}{2}$ 得 $c^2=\\dfrac{1}{2}a^2$，故 $b^2=a^2-c^2=\\dfrac{1}{2}a^2$。\n设椭圆为 $\\dfrac{x^2}{a^2}+\\dfrac{2y^2}{a^2}=1$，代入 $(2,\\sqrt{2})$ 得 $\\dfrac{4}{a^2}+\\dfrac{4}{a^2}=1$，即 $a^2=8$，从而 $b^2=4$。\n\n**【答案】** $\\dfrac{x^2}{8}+\\dfrac{y^2}{4}=1$\n\n**【易错提醒】** 注意 $a>b>0$，别把 $a^2,b^2$ 写反；离心率公式 $e=\\dfrac{c}{a}$ 中 $c$ 是焦距的一半。',
    source: '模拟卷·选择填空',
    subject: '数学',
    knowledge_point: '椭圆方程与离心率',
    review_count: 3,
    mastery: 'reviewing',
    snooze_until: '',
    created_at: '2026-08-15 10:12',
    updated_at: '2026-08-19 09:30',
  },
  {
    id: 2,
    category_id: 4,
    category_name: '化学',
    category_color: 4,
    question:
      '对于反应 $2SO_2(g)+O_2(g)\\rightleftharpoons 2SO_3(g)\\quad \\Delta H<0$，写出其平衡常数表达式，并说明升高温度时平衡如何移动。',
    answer:
      '**【思路】** 平衡常数取生成物浓度幂之积除以反应物浓度幂之积，幂为化学计量数；升温使平衡向吸热方向移动。\n\n**【解答】**\n$$K_c=\\dfrac{c^2(SO_3)}{c^2(SO_2)\\cdot c(O_2)}$$\n该反应正反应放热（$\\Delta H<0$），升高温度平衡向逆反应（吸热）方向移动，$SO_3$ 产率下降。\n\n**【答案】** 表达式如上；升温平衡左移。\n\n**【易错提醒】** 纯固体/液体不写入 $K$；移动方向看"吸热"而不是"放热"。',
    source: '课堂例题',
    subject: '化学',
    knowledge_point: '化学平衡常数与勒夏特列原理',
    review_count: 2,
    mastery: 'reviewing',
    snooze_until: '',
    created_at: '2026-08-16 14:05',
    updated_at: '2026-08-19 09:31',
  },
  {
    id: 3,
    category_id: 2,
    category_name: '英语',
    category_color: 2,
    question:
      '改错：If I was you, I would take the job offer immediately.（虚拟语气）',
    answer:
      '**【思路】** 与现在事实相反的虚拟语气，be 动词一律用 were，不用 was。\n\n**【解答】** 应为：If I **were** you, I would take the job offer immediately.\n\n**【答案】** was → were\n\n**【易错提醒】** 虚拟条件句中无论主语是第几人称，be 都用 were（口语中极非正式才用 was）。',
    source: '语法练习',
    subject: '英语',
    knowledge_point: '虚拟语气',
    review_count: 1,
    mastery: 'unmastered',
    snooze_until: '',
    created_at: '2026-08-17 20:40',
    updated_at: '2026-08-19 09:32',
  },
  {
    id: 4,
    category_id: 3,
    category_name: '物理',
    category_color: 3,
    question:
      '质量为 $m$ 的物体沿倾角为 $\\theta$ 的光滑斜面由静止下滑，求下滑距离 $s$ 时的速度 $v$。',
    answer:
      '**【思路】** 沿斜面方向的加速度为 $a=g\\sin\\theta$，用运动学公式 $v^2=2as$ 即可。\n\n**【解答】**\n$$a=g\\sin\\theta, \\quad v^2=2as=2g\\sin\\theta\\cdot s$$\n$$v=\\sqrt{2gs\\sin\\theta}$$\n\n**【答案】** $v=\\sqrt{2gs\\sin\\theta}$\n\n**【易错提醒】** 加速度不是 $g$ 而是沿斜面的 $g\\sin\\theta$；不要漏掉 $\\sin\\theta$。',
    source: '课后习题',
    subject: '物理',
    knowledge_point: '牛顿第二定律与斜面运动',
    review_count: 4,
    mastery: 'mastered',
    snooze_until: '',
    created_at: '2026-08-14 16:20',
    updated_at: '2026-08-19 09:33',
  },
  {
    id: 5,
    category_id: 5,
    category_name: '高数',
    category_color: 6,
    question: '求极限 $\\lim_{x\\to 0}\\dfrac{\\int_0^x (e^{t^2}-1)\\,dt}{x^2\\sin 2x}$。',
    answer:
      '**【思路】** 分子分母均趋于 0，用洛必达法则；注意 $\\sin 2x\\sim 2x$。\n\n**【解答】**\n$$\\lim_{x\\to 0}\\dfrac{e^{x^2}-1}{2x\\sin 2x+2x^2\\cos 2x}\\sim\\lim_{x\\to 0}\\dfrac{x^2}{2x\\cdot 2x}=\\dfrac{1}{4}$$\n\n**【答案】** $\\dfrac{1}{4}$\n\n**【易错提醒】** 洛必达后分母要用乘积求导；等价无穷小 $\\sin 2x\\sim 2x$ 可简化计算。',
    source: '考研真题',
    subject: '高数',
    knowledge_point: '洛必达法则与等价无穷小',
    review_count: 5,
    mastery: 'mastered',
    snooze_until: '',
    created_at: '2026-08-13 21:10',
    updated_at: '2026-08-19 09:34',
  },
  {
    id: 6,
    category_id: 1,
    category_name: '数学',
    category_color: 1,
    question:
      '已知向量 $\\vec{a}=(1,2)$，$\\vec{b}=(3,-1)$，求 $\\vec{a}\\cdot\\vec{b}$ 与 $|\\vec{a}+\\vec{b}|$。',
    answer:
      '**【思路】** 数量积按对应分量相乘求和；先求 $\\vec{a}+\\vec{b}$ 再取模。\n\n**【解答】**\n$\\vec{a}\\cdot\\vec{b}=1\\times 3+2\\times(-1)=1$；\n$\\vec{a}+\\vec{b}=(4,1)$，故 $|\\vec{a}+\\vec{b}|=\\sqrt{4^2+1^2}=\\sqrt{17}$。\n\n**【答案】** $\\vec{a}\\cdot\\vec{b}=1$，$|\\vec{a}+\\vec{b}|=\\sqrt{17}$\n\n**【易错提醒】** 数量积结果是标量不是向量；模长别忘了开平方。',
    source: '周测',
    subject: '数学',
    knowledge_point: '平面向量运算',
    review_count: 2,
    mastery: 'reviewing',
    snooze_until: '',
    created_at: '2026-08-18 11:55',
    updated_at: '2026-08-19 09:35',
  },
]

// ---------------- 对话 ----------------
const chatSession: ChatSession = { id: 1, title: '关于椭圆离心率的疑问', created_at: '2026-08-19 09:00', updated_at: '2026-08-19 09:20' }
const chatMessages: ChatMessage[] = [
  { id: 1, session_id: 1, role: 'user', content: '椭圆的离心率和焦距是什么关系？', created_at: '2026-08-19 09:01' },
  { id: 2, session_id: 1, role: 'assistant', content: '离心率 $e=\\dfrac{c}{a}$，其中 $c$ 是焦距的一半（半焦距），$a$ 是长半轴。三者满足 $c^2=a^2-b^2$。所以 $e$ 越大椭圆越扁。', created_at: '2026-08-19 09:02' },
]

// ---------------- 看板 ----------------
export const dashboardStats: DashboardStats = {
  total_questions: 6,
  total_reviews: 23,
  success_rate: 0.78,
  pending_review: 2,
  study_series: [
    { date: '08-13', count: 3 },
    { date: '08-14', count: 5 },
    { date: '08-15', count: 4 },
    { date: '08-16', count: 2 },
    { date: '08-17', count: 4 },
    { date: '08-18', count: 3 },
    { date: '08-19', count: 2 },
  ],
  entry_series: [
    { date: '08-13', count: 1 },
    { date: '08-14', count: 1 },
    { date: '08-15', count: 1 },
    { date: '08-16', count: 1 },
    { date: '08-17', count: 1 },
    { date: '08-18', count: 1 },
    { date: '08-19', count: 0 },
  ],
  by_subject: [
    { subject: '数学', count: 2 },
    { subject: '英语', count: 1 },
    { subject: '物理', count: 1 },
    { subject: '化学', count: 1 },
    { subject: '高数', count: 1 },
  ],
}

// ---------------- 设置 ----------------
export const settings: Settings = {
  model_name: 'deepseek-ai/DeepSeek-V3.2',
  api_key: '********',
  base_url: 'https://api.siliconflow.cn/v1',
}

// ---------------- 帮助 ----------------
export const helpDoc: HelpDoc = {
  title: 'Recall AI · 使用帮助',
  intro: 'Recall 帮你把错题自动整理成可复习的知识库：录入、AI 解析、按计划复习、数据洞察。',
  sections: [
    { title: '如何录入错题', body: '支持图片识别、文本录入、AI 对话一键入本三种方式。图片识别由视觉模型完成，可识别含公式的题目。' },
    { title: 'AI 解析怎么用', body: '在错题详情或新建时点击「AI 解析」，系统会生成【思路】【解答】【答案】【易错提醒】四段内容，数学公式以 KaTeX 渲染。' },
    { title: '复习计划', body: '基于 SM-2 记忆算法，根据遗忘曲线生成每日 / 周度复习清单，逐题作答后由 AI 批改。' },
    { title: '关于本演示版', body: '你当前浏览的是演示版（静态托管，无后端）。录入、AI 解析、OCR、导出等功能需在完整版或云端部署中运行。' },
  ],
}

// ---------------- demo 版 api 对象 ----------------
export const demoApi = {
  mistakes: {
    list: () => delay(mistakes),
    get: (id: number) => delay(mistakes.find((m) => m.id === id) ?? mistakes[0]),
    create: (data: Partial<Mistake>) => delay({ ...mistakes[0], ...data, id: 99 } as Mistake),
    update: (id: number, data: Partial<Mistake>) => delay({ ...mistakes[0], ...data, id }),
    remove: () => delay(undefined),
    review: (id: number) => delay(mistakes.find((m) => m.id === id) ?? mistakes[0]),
    semantic: () => delay([]),
    exportPdf: () => {
      alert(DEMO_NOTICE)
      return Promise.resolve()
    },
    snooze: (id: number) => delay(mistakes.find((m) => m.id === id) ?? mistakes[0]),
  },
  categories: {
    list: () => delay(categories),
    create: (data: { name: string; color: number }) => delay({ ...data, id: 99, count: 0 }),
    update: (id: number, data: { name: string; color: number }) => delay({ ...data, id }),
    remove: () => delay(undefined),
  },
  chat: {
    sessions: () => delay([chatSession]),
    createSession: (title = '新对话') => delay({ ...chatSession, title, id: 99 }),
    messages: () => delay(chatMessages),
    send: () => delay([...chatMessages, { id: 3, session_id: 1, role: 'assistant' as const, content: DEMO_NOTICE, created_at: '' }]),
    remove: () => delay(undefined),
    solve: () =>
      delay({ available: false, answer: DEMO_NOTICE }),
  },
  dashboard: {
    stats: () => delay(dashboardStats),
  },
  settings: {
    get: () => delay(settings),
    update: () => {
      alert(DEMO_NOTICE)
      return delay(settings)
    },
  },
  upload: {
    ocr: () => {
      alert(DEMO_NOTICE)
      return Promise.reject(new Error('demo-unsupported'))
    },
  },
  help: {
    doc: () => delay(helpDoc),
  },
}
