<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { Category, Mastery, Mistake } from '@/types'
import { categoriesApi, chatApi, mistakesApi, uploadApi } from '@/api'
import Icon from '@/components/Icon.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseInput from '@/components/BaseInput.vue'
import BaseModal from '@/components/BaseModal.vue'
import EmptyState from '@/components/EmptyState.vue'
import MistakeCard from '@/components/MistakeCard.vue'
import CategoryNav from '@/components/CategoryNav.vue'
import MathText from '@/components/MathText.vue'

const route = useRoute()

const CAT_COLORS: Record<number, string> = {
  1: '#0A84FF', 2: '#34C759', 3: '#FF9500', 4: '#AF52DE',
  5: '#FF2D55', 6: '#32ADE6', 7: '#FFCC00', 8: '#5856D6',
}

const categories = ref<Category[]>([])
const mistakes = ref<Mistake[]>([])
const loading = ref(false)
const loadError = ref('')
const selectedCategory = ref<number | null>(null)
const search = ref('')
const statusFilter = ref<string>('')

// 选择导出
const selectedIds = ref<Set<number>>(new Set())
const hasSelection = computed(() => selectedIds.value.size > 0)
const exportLabel = computed(() =>
  hasSelection.value ? `导出选中 (${selectedIds.value.size})` : '导出全部',
)
const allSelected = computed(() => mistakes.value.length > 0 && mistakes.value.every((m) => selectedIds.value.has(m.id)))

// 弹窗状态
const formOpen = ref(false)
const form = reactive({
  id: null as number | null,
  question: '', answer: '', source: '', subject: '', knowledge_point: '',
  category_id: null as number | null, mastery: 'unmastered' as Mastery,
})
const catOpen = ref(false)
const catName = ref('')
const catColorSel = ref(1)

const ocrOpen = ref(false)
const ocrFile = ref<File | null>(null)
const ocrLoading = ref(false)
const ocrText = ref('')
const ocrParsing = ref(false)
const ocrError = ref('')
const ocrInputKey = ref(0)

// 复习模式
const reviewOpen = ref(false)
const reviewList = ref<Mistake[]>([])
const reviewIdx = ref(0)
const reviewShowAns = ref(false)

const filteredCount = computed(() => mistakes.value.length)

function toggleSelect(id: number, v: boolean) {
  if (v) selectedIds.value.add(id)
  else selectedIds.value.delete(id)
}
function selectAll() {
  mistakes.value.forEach((m) => selectedIds.value.add(m.id))
}
function clearSelection() {
  selectedIds.value.clear()
}

async function loadCategories() {
  categories.value = await categoriesApi.list()
}
async function loadMistakes() {
  loading.value = true
  loadError.value = ''
  try {
    mistakes.value = await mistakesApi.list({
      category_id: selectedCategory.value ?? undefined,
      q: search.value || undefined,
      status: statusFilter.value || undefined,
    })
    // 过滤条件变化后，清除已失效的选择
    selectedIds.value.clear()
  } catch (e) {
    loadError.value = '加载失败，请检查网络后刷新重试'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadCategories()
  await loadMistakes()
  if (route.query.new) openCreate()
})

watch([selectedCategory, search, statusFilter], loadMistakes)

// 从侧边栏「新建错题」触发（query.new 为时间戳，每次都变化）
watch(
  () => route.query.new,
  (v) => {
    if (v) openCreate()
  },
)

// ---------------- 录入 / 编辑 ----------------
function openCreate() {
  Object.assign(form, {
    id: null, question: '', answer: '', source: '', subject: '', knowledge_point: '',
    category_id: categories.value[0]?.id ?? null, mastery: 'unmastered',
  })
  formOpen.value = true
}
function openEdit(m: Mistake) {
  Object.assign(form, {
    id: m.id, question: m.question, answer: m.answer, source: m.source,
    subject: m.subject, knowledge_point: m.knowledge_point,
    category_id: m.category_id, mastery: m.mastery,
  })
  formOpen.value = true
}
async function saveForm() {
  if (!form.question.trim()) {
    alert('请填写题目内容')
    return
  }
  const payload = {
    question: form.question, answer: form.answer, source: form.source,
    subject: form.subject, knowledge_point: form.knowledge_point,
    category_id: form.category_id, mastery: form.mastery,
  }
  if (form.id) await mistakesApi.update(form.id, payload)
  else await mistakesApi.create(payload)
  formOpen.value = false
  await loadCategories()
  await loadMistakes()
}

// ---------------- 分类 ----------------
async function createCategory() {
  if (!catName.value.trim()) return
  await categoriesApi.create({ name: catName.value, color: catColorSel.value })
  catName.value = ''
  catColorSel.value = 1
  catOpen.value = false
  await loadCategories()
}
async function deleteCategory(id: number) {
  if (!confirm('确定删除该分类？错题将变为未分类。')) return
  await categoriesApi.remove(id)
  if (selectedCategory.value === id) selectedCategory.value = null
  await loadCategories()
  await loadMistakes()
}

// ---------------- 删除 / 复习 ----------------
async function removeMistake(m: Mistake) {
  if (!confirm('确定删除这道错题？')) return
  await mistakesApi.remove(m.id)
  await loadMistakes()
}
async function reviewOne(m: Mistake) {
  await mistakesApi.review(m.id)
  await loadMistakes()
}

// ---------------- OCR ----------------
function openOcr() {
  ocrError.value = ''
  ocrFile.value = null
  ocrText.value = ''
  ocrParsing.value = false
  ocrInputKey.value++
  ocrOpen.value = true
}

function applyOcrToForm() {
  if (!ocrText.value) return
  openCreate() // 先重置表单并打开录入弹窗，否则 openCreate 的 Object.assign 会把 question 清空
  form.question = ocrText.value
  ocrOpen.value = false
}

// 识别后：AI 自动解析并一并填入
async function applyOcrWithAi() {
  if (!ocrText.value || ocrParsing.value) return
  ocrParsing.value = true
  ocrError.value = ''
  try {
    const res = await chatApi.solve(ocrText.value)
    if (!res.available) {
      ocrError.value = res.answer || 'AI 解析暂不可用，请先在「设置」页配置 AI 模型，或直接「仅填题干」。'
      return
    }
    openCreate()
    form.question = ocrText.value
    form.answer = res.answer
    ocrOpen.value = false
  } catch (e: any) {
    ocrError.value = `AI 解析失败：${e?.message || '未知错误'}。可直接「仅填题干」或稍后重试。`
  } finally {
    ocrParsing.value = false
  }
}

async function doOcr() {
  const file = ocrFile.value
  if (!file) return
  ocrLoading.value = true
  ocrError.value = ''
  ocrText.value = ''
  try {
    const res = await uploadApi.ocr(file)
    if (!res.available) {
      ocrError.value = res.message || '图片识别暂不可用，请先在「设置」页配置 AI 模型。'
      return
    }
    ocrText.value = res.text
    if (!res.text) {
      ocrError.value = '未识别到文字，请更换清晰的题目截图后重试。'
    }
  } catch (e: any) {
    ocrError.value = e?.code === 'ECONNABORTED'
      ? '识别超时（AI 响应较慢），请稍后重试，或换一张更小的图片。'
      : `识别失败：${e?.message || '未知错误'}，请检查网络后重试。`
  } finally {
    ocrLoading.value = false
  }
}

// ---------------- 开始复习 ----------------
function startReview() {
  const now = new Date().toISOString()
  const pool = mistakes.value.filter((m) => !m.snooze_until || m.snooze_until < now)
  if (!pool.length) {
    alert('太棒了，当前没有待复习的错题！')
    return
  }
  reviewList.value = pool
  reviewIdx.value = 0
  reviewShowAns.value = false
  reviewOpen.value = true
}
async function reviewMark(mastered: boolean) {
  const cur = reviewList.value[reviewIdx.value]
  if (cur) {
    await mistakesApi.update(cur.id, { mastery: mastered ? 'mastered' : 'reviewing' })
    await mistakesApi.review(cur.id)
  }
  await advanceReview()
}
async function reviewSnooze() {
  const cur = reviewList.value[reviewIdx.value]
  if (cur) {
    await mistakesApi.snooze(cur.id) // 后端随机 5-7 天
  }
  await advanceReview()
}
async function advanceReview() {
  if (reviewIdx.value < reviewList.value.length - 1) {
    reviewIdx.value++
    reviewShowAns.value = false
  } else {
    reviewOpen.value = false
    await loadCategories()
    await loadMistakes()
  }
}
</script>

<template>
  <div class="flex h-full">
    <!-- 分类导航（桌面左栏） -->
    <aside class="hidden lg:block w-56 shrink-0 border-r border-border bg-card p-md overflow-auto">
      <CategoryNav
        :categories="categories"
        :selected-id="selectedCategory"
        @select="selectedCategory = $event"
        @create="catOpen = true"
        @delete="deleteCategory"
      />
    </aside>

    <!-- 主内容 -->
    <div class="flex-1 min-w-0 p-xl overflow-auto">
      <!-- 移动端分类横向 -->
      <div class="lg:hidden flex gap-2 overflow-x-auto pb-md mb-md border-b border-border">
        <button
          class="shrink-0 rounded-tag border px-3 h-8 text-caption"
          :class="selectedCategory === null ? 'bg-bg text-primary border-primary' : 'text-text2 border-border'"
          @click="selectedCategory = null"
        >全部</button>
        <button
          v-for="c in categories" :key="c.id"
          class="shrink-0 rounded-tag border px-3 h-8 text-caption flex items-center gap-1"
          :class="selectedCategory === c.id ? 'bg-bg text-primary border-primary' : 'text-text2 border-border'"
          @click="selectedCategory = c.id"
        >
          <span class="h-2 w-2 rounded-full" :style="{ backgroundColor: CAT_COLORS[c.color] }" />{{ c.name }}
        </button>
        <button class="shrink-0 rounded-tag border border-dashed border-border px-3 h-8 text-caption text-primary" @click="catOpen = true">+ 分类</button>
      </div>

      <!-- 操作栏 -->
      <div class="flex flex-wrap items-center gap-md mb-xl">
        <BaseButton @click="openCreate"><Icon name="plus" :size="16" /> 新建错题</BaseButton>
        <BaseButton variant="secondary" @click="openOcr"><Icon name="upload" :size="16" /> 图片识别</BaseButton>
        <BaseButton variant="secondary" @click="mistakesApi.exportPdf(hasSelection ? Array.from(selectedIds) : undefined)">
          <Icon name="download" :size="16" /> {{ exportLabel }}
        </BaseButton>
        <BaseButton variant="secondary" @click="startReview"><Icon name="refresh" :size="16" /> 开始复习</BaseButton>

        <div v-if="mistakes.length" class="hidden sm:flex items-center gap-sm border-l border-border pl-md">
          <button
            class="text-caption text-text2 hover:text-primary"
            @click="allSelected ? clearSelection() : selectAll()"
          >{{ allSelected ? '取消全选' : '全选' }}</button>
          <button v-if="hasSelection" class="text-caption text-text3 hover:text-text1" @click="clearSelection">清空</button>
        </div>

        <div class="relative flex-1 min-w-[200px]">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-text3"><Icon name="search" :size="16" /></span>
          <input v-model="search" placeholder="搜索题目 / 解析 / 知识点" class="ly-input pl-9" />
        </div>

        <select v-model="statusFilter" class="ly-input !w-auto">
          <option value="">全部状态</option>
          <option value="unmastered">未掌握</option>
          <option value="reviewing">复习中</option>
          <option value="mastered">已掌握</option>
        </select>
      </div>

      <p class="text-caption text-text3 mb-md">共 {{ filteredCount }} 道错题</p>

      <!-- 列表 -->
      <div v-if="loading" class="text-center text-text3 py-2xl">加载中…</div>
      <div v-else-if="loadError" class="text-center py-2xl">
        <p class="text-body text-error mb-md">{{ loadError }}</p>
        <BaseButton variant="secondary" @click="loadMistakes">重试</BaseButton>
      </div>
      <EmptyState
        v-else-if="!mistakes.length"
        icon="book"
        title="还没有错题"
        desc="点击「录入」手动添加，或上传题目截图让 AI 自动识别。"
      >
        <template #action>
          <div class="mt-md flex gap-md">
            <BaseButton @click="openCreate"><Icon name="plus" :size="16" /> 录入错题</BaseButton>
            <BaseButton variant="secondary" @click="openOcr"><Icon name="upload" :size="16" /> 图片识别</BaseButton>
          </div>
        </template>
      </EmptyState>

      <div v-else class="grid grid-cols-1 xl:grid-cols-2 items-start gap-md">
        <MistakeCard
          v-for="m in mistakes"
          :key="m.id"
          :mistake="m"
          :selected="selectedIds.has(m.id)"
          @update:selected="toggleSelect(m.id, $event)"
          @edit="openEdit"
          @delete="removeMistake"
          @review="reviewOne"
        />
      </div>

      <!-- 底部轻量提示，填充空白同时不补无关错题 -->
      <div v-if="mistakes.length" class="mt-2xl flex flex-col items-center justify-center py-10 text-center">
        <div class="flex h-10 w-10 items-center justify-center rounded-full bg-bg">
          <Icon name="book" :size="20" />
        </div>
        <p class="mt-3 text-caption text-text3">共 {{ mistakes.length }} 道错题 · 继续积累，进步看得见</p>
        <button class="mt-2 text-caption text-primary hover:underline" @click="openCreate">继续录入</button>
      </div>
    </div>
  </div>

  <!-- 录入/编辑弹窗 -->
  <BaseModal v-model="formOpen" :title="form.id ? '编辑错题' : '录入错题'">
    <div class="space-y-md">
      <BaseInput v-model="form.question" label="题目内容" placeholder="支持 LaTeX：用 $...$ 包裹公式，如 $\\frac{a}{b}$" multiline />
      <details v-if="form.question" class="text-caption">
        <summary class="text-text3 cursor-pointer">预览渲染效果</summary>
        <div class="mt-2 rounded-6px border border-border bg-bg px-3 py-2 text-text1">
          <MathText :text="form.question" />
        </div>
      </details>
      <BaseInput v-model="form.answer" label="AI 解析" placeholder="解题步骤 / 易错提醒（可选，支持 LaTeX）" multiline />
      <details v-if="form.answer" class="text-caption">
        <summary class="text-text3 cursor-pointer">预览渲染效果</summary>
        <div class="mt-2 rounded-6px border border-border bg-bg px-3 py-2 text-text2">
          <MathText :text="form.answer" />
        </div>
      </details>
      <div class="grid grid-cols-2 gap-md">
        <BaseInput v-model="form.subject" label="学科" placeholder="如 数学" />
        <BaseInput v-model="form.knowledge_point" label="知识点" placeholder="如 三角函数" />
      </div>
      <BaseInput v-model="form.source" label="来源" placeholder="如 期中试卷 / 作业" />
      <div>
        <label class="block text-caption text-text2 mb-xs">分类</label>
        <select v-model="form.category_id" class="ly-input">
          <option :value="null">未分类</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div>
        <label class="block text-caption text-text2 mb-xs">掌握状态</label>
        <select v-model="form.mastery" class="ly-input">
          <option value="unmastered">未掌握</option>
          <option value="reviewing">复习中</option>
          <option value="mastered">已掌握</option>
        </select>
      </div>
    </div>
    <template #footer>
      <BaseButton variant="text" @click="formOpen = false">取消</BaseButton>
      <BaseButton :disabled="!form.question.trim()" @click="saveForm"><Icon name="check" :size="16" /> 保存</BaseButton>
    </template>
  </BaseModal>

  <!-- 新建分类 -->
  <BaseModal v-model="catOpen" title="新建分类">
    <div class="space-y-md">
      <BaseInput v-model="catName" label="分类名称" placeholder="如 高数" />
      <div>
        <label class="block text-caption text-text2 mb-xs">标签颜色</label>
        <div class="flex gap-sm">
          <button
            v-for="n in 8" :key="n"
            class="h-8 w-8 rounded-btn border-2"
            :style="{ borderColor: catColorSel === n ? '#1D1D1F' : 'transparent', backgroundColor: CAT_COLORS[n] }"
            @click="catColorSel = n"
          />
        </div>
      </div>
    </div>
    <template #footer>
      <BaseButton variant="text" @click="catOpen = false">取消</BaseButton>
      <BaseButton @click="createCategory"><Icon name="check" :size="16" /> 创建</BaseButton>
    </template>
  </BaseModal>

  <!-- OCR 上传 -->
  <BaseModal v-model="ocrOpen" title="图片识别（AI 视觉）">
    <div class="space-y-md">
      <input :key="ocrInputKey" type="file" accept="image/*" class="ly-input" @change="ocrError = ''; ocrText = ''; ocrFile = ($event.target as HTMLInputElement).files?.[0] || null" />
      <p class="text-caption text-text3">上传题目截图，Recall 会调用 AI 视觉模型自动识别图中的题目文字（含数学公式）。</p>
      <div v-if="ocrFile" class="text-caption text-text2">已选择：{{ ocrFile.name }}（{{ (ocrFile.size / 1024).toFixed(0) }} KB）</div>
      <div v-if="ocrError" class="rounded-8px border border-error/30 bg-error/5 px-3 py-2 text-caption text-error">{{ ocrError }}</div>
      <div v-if="ocrText" class="rounded-8px border border-success/30 bg-success/5 px-3 py-3">
        <p class="text-caption text-text2 mb-2">识别结果（选择下方操作）：</p>
        <div class="text-body text-text1 border border-border rounded-6px bg-white px-3 py-2">
          <MathText :text="ocrText" />
        </div>
        <details class="mt-2">
          <summary class="text-caption text-text3 cursor-pointer">查看原始文本（可手动编辑后再填入）</summary>
          <textarea v-model="ocrText" class="ly-input mt-2 w-full font-mono text-caption" rows="4" />
        </details>
      </div>
    </div>
    <template #footer>
      <BaseButton variant="text" @click="ocrOpen = false">取消</BaseButton>
      <template v-if="ocrText">
        <BaseButton variant="secondary" :disabled="ocrParsing" @click="applyOcrWithAi">
          <Icon name="sparkles" :size="16" /> {{ ocrParsing ? 'AI 解析中…（约 30-60 秒）' : 'AI 解析并填入' }}
        </BaseButton>
        <BaseButton variant="secondary" :disabled="ocrParsing" @click="applyOcrToForm"><Icon name="check" :size="16" /> 仅填题干</BaseButton>
      </template>
      <BaseButton v-else :disabled="!ocrFile || ocrLoading" @click="doOcr">
        <Icon name="sparkles" :size="16" /> {{ ocrLoading ? '识别中…（约 10 秒）' : '开始识别' }}
      </BaseButton>
    </template>
  </BaseModal>

  <!-- 复习模式 -->
  <BaseModal v-model="reviewOpen" :title="`复习中（${reviewIdx + 1}/${reviewList.length}）`">
    <div v-if="reviewList[reviewIdx]" class="space-y-md">
      <div class="flex gap-3">
        <div class="w-[3px] rounded-full bg-question" />
        <p class="text-text1"><MathText :text="reviewList[reviewIdx].question" /></p>
      </div>
      <div v-if="reviewShowAns" class="flex gap-3">
        <div class="w-[3px] rounded-full bg-answer" />
        <p class="text-text2"><MathText :text="reviewList[reviewIdx].answer || '（暂无解析）'" /></p>
      </div>
      <BaseButton v-else variant="secondary" block @click="reviewShowAns = true">显示解析</BaseButton>
    </div>
    <template #footer>
      <div class="w-full flex flex-col sm:flex-row gap-sm">
        <BaseButton variant="secondary" block @click="reviewMark(false)">还不会</BaseButton>
        <BaseButton variant="secondary" block @click="reviewSnooze">不再复习此题</BaseButton>
        <BaseButton block @click="reviewMark(true)"><Icon name="check" :size="16" /> 已掌握</BaseButton>
      </div>
    </template>
  </BaseModal>
</template>
