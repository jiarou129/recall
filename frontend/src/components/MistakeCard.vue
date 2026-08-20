<script setup lang="ts">
import { withDefaults } from 'vue'
import type { Mistake, Mastery } from '@/types'
import Icon from './Icon.vue'
import BaseTag from './BaseTag.vue'
import MathText from './MathText.vue'

const props = withDefaults(defineProps<{ mistake: Mistake; selected?: boolean }>(), { selected: false })
const emit = defineEmits<{
  (e: 'edit', m: Mistake): void
  (e: 'delete', m: Mistake): void
  (e: 'review', m: Mistake): void
  (e: 'update:selected', v: boolean): void
}>()

const CAT_COLORS: Record<number, string> = {
  1: '#0A84FF', 2: '#34C759', 3: '#FF9500', 4: '#AF52DE',
  5: '#FF2D55', 6: '#32ADE6', 7: '#FFCC00', 8: '#5856D6',
}
function catColor(n: number): string {
  return CAT_COLORS[n] || CAT_COLORS[1]
}

const MASTERY: Record<Mastery, { label: string; color: string }> = {
  unmastered: { label: '未掌握', color: '#FF3B30' },
  reviewing: { label: '复习中', color: '#FF9500' },
  mastered: { label: '已掌握', color: '#34C759' },
}
const m = MASTERY[props.mistake.mastery]
</script>

<template>
  <div class="ly-card p-xl">
    <!-- 头部：复选框 + 分类色点 + 学科/知识点 + 状态 -->
    <div class="flex items-start justify-between gap-md">
      <div class="flex flex-wrap items-center gap-sm">
        <button
          class="h-5 w-5 rounded-[4px] border flex items-center justify-center transition-colors"
          :class="selected ? 'bg-primary border-primary' : 'border-border bg-white hover:border-primary/50'"
          @click.stop="emit('update:selected', !selected)"
          :aria-label="selected ? '取消选择' : '选择'"
        >
          <Icon v-if="selected" name="check" :size="12" class="text-white" />
        </button>
        <span class="inline-flex h-2 w-2 rounded-full" :style="{ backgroundColor: catColor(mistake.category_color) }" />
        <BaseTag v-if="mistake.subject" :label="mistake.subject" :color="mistake.category_color" filled />
        <BaseTag v-if="mistake.knowledge_point" :label="mistake.knowledge_point" />
      </div>
      <span
        class="shrink-0 rounded-tag border px-2 py-0.5 text-caption"
        :style="{ color: m.color, borderColor: m.color }"
      >{{ m.label }}</span>
    </div>

    <!-- 题目区（蓝 #3B82F6） -->
    <div class="mt-md flex gap-3">
      <div class="w-[3px] shrink-0 rounded-full bg-question" />
      <div class="min-w-0">
        <p class="text-caption font-medium text-question">题目</p>
        <p class="mt-xs break-words text-body text-text1"><MathText :text="mistake.question" /></p>
      </div>
    </div>

    <!-- AI 解析区（绿 #10B981） -->
    <div v-if="mistake.answer" class="mt-md flex gap-3">
      <div class="w-[3px] shrink-0 rounded-full bg-answer" />
      <div class="min-w-0">
        <p class="text-caption font-medium text-answer">AI 解析</p>
        <p class="mt-xs break-words text-body text-text2"><MathText :text="mistake.answer" /></p>
      </div>
    </div>

    <!-- 元信息 -->
    <div class="mt-md flex flex-wrap items-center gap-md text-caption text-text3">
      <span v-if="mistake.source">来源：{{ mistake.source }}</span>
      <span class="inline-flex items-center gap-1">
        <Icon name="refresh" :size="14" /> 复习 {{ mistake.review_count }} 次
      </span>
    </div>

    <!-- 操作 -->
    <div class="mt-md flex items-center justify-end gap-sm border-t border-border pt-md">
      <button class="inline-flex items-center gap-1 rounded-btn px-3 h-8 text-caption text-primary hover:bg-bg" @click="emit('review', mistake)">
        <Icon name="refresh" :size="14" /> 复习
      </button>
      <button class="inline-flex items-center gap-1 rounded-btn px-3 h-8 text-caption text-text2 hover:bg-bg" @click="emit('edit', mistake)">
        <Icon name="edit" :size="14" /> 编辑
      </button>
      <button class="inline-flex items-center gap-1 rounded-btn px-3 h-8 text-caption text-error hover:bg-bg" @click="emit('delete', mistake)">
        <Icon name="trash" :size="14" /> 删除
      </button>
    </div>
  </div>
</template>
