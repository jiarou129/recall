<script setup lang="ts">
import type { Category } from '@/types'
import Icon from './Icon.vue'

const CAT_COLORS: Record<number, string> = {
  1: '#0A84FF', 2: '#34C759', 3: '#FF9500', 4: '#AF52DE',
  5: '#FF2D55', 6: '#32ADE6', 7: '#FFCC00', 8: '#5856D6',
}

defineProps<{ categories: Category[]; selectedId: number | null }>()
const emit = defineEmits<{
  (e: 'select', id: number | null): void
  (e: 'create'): void
  (e: 'delete', id: number): void
}>()

function color(n: number) {
  return CAT_COLORS[n] || CAT_COLORS[1]
}
</script>

<template>
  <div class="flex flex-col">
    <p class="px-md pb-xs text-caption text-text3">错题分类</p>
    <button
      class="flex items-center gap-2 rounded-btn px-3 h-9 text-body transition-colors"
      :class="selectedId === null ? 'bg-bg text-primary font-medium' : 'text-text2 hover:bg-bg'"
      @click="emit('select', null)"
    >
      <Icon name="list" :size="16" />
      <span class="flex-1 text-left">全部错题</span>
    </button>

    <div
      v-for="c in categories"
      :key="c.id"
      class="group flex items-center gap-2 rounded-btn px-3 h-9 text-body transition-colors"
      :class="selectedId === c.id ? 'bg-bg text-primary font-medium' : 'text-text2 hover:bg-bg'"
    >
      <button class="flex flex-1 items-center gap-2 min-w-0" @click="emit('select', c.id)">
        <span class="h-2.5 w-2.5 shrink-0 rounded-full" :style="{ backgroundColor: color(c.color) }" />
        <span class="truncate">{{ c.name }}</span>
        <span class="ml-auto text-caption text-text3">{{ c.count }}</span>
      </button>
      <button class="opacity-0 group-hover:opacity-100 text-text3 hover:text-error" @click="emit('delete', c.id)">
        <Icon name="close" :size="14" />
      </button>
    </div>

    <button class="mt-xs flex items-center gap-2 rounded-btn px-3 h-9 text-caption text-primary hover:bg-bg" @click="emit('create')">
      <Icon name="plus" :size="16" /> 新建分类
    </button>
  </div>
</template>
