<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import Icon from './Icon.vue'

defineProps<{ expanded?: boolean }>()
const emit = defineEmits<{ (e: 'new'): void; (e: 'close'): void }>()

const router = useRouter()
const route = useRoute()

const items = [
  { to: '/', label: '错题集', icon: 'book' },
  { to: '/chat', label: 'AI 答疑', icon: 'chat' },
  { to: '/dashboard', label: '数据看板', icon: 'chart' },
  { to: '/settings', label: '模型设置', icon: 'settings' },
  { to: '/help', label: '帮助中心', icon: 'help' },
]

function isActive(to: string) {
  return to === '/' ? route.path === '/' : route.path.startsWith(to)
}
</script>

<template>
  <div class="flex h-full flex-col bg-card border-r border-border">
    <!-- Logo -->
    <div class="flex items-center gap-2 px-xl h-16 border-b border-border">
      <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-btn bg-primary text-white">
        <Icon name="brain" :size="20" />
      </div>
      <span class="text-h2 text-text1 font-semibold" :class="expanded ? 'inline' : 'hidden lg:inline'">Recall AI</span>
    </div>

    <!-- 新建错题 -->
    <div class="p-md">
      <button
        class="flex w-full items-center justify-center gap-1.5 rounded-btn bg-primary px-4 h-10 text-body text-white font-medium hover:opacity-90"
        :class="expanded ? 'justify-center' : 'lg:justify-center justify-start'"
        @click="emit('new')"
      >
        <Icon name="plus" :size="16" />
        <span :class="expanded ? 'inline' : 'hidden lg:inline'">新建错题</span>
      </button>
    </div>

    <!-- 导航 -->
    <nav class="flex-1 px-md space-y-1">
      <a
        v-for="item in items"
        :key="item.to"
        class="flex items-center gap-3 rounded-btn px-3 h-10 cursor-pointer transition-colors"
        :class="[
          isActive(item.to) ? 'bg-bg text-primary font-medium' : 'text-text2 hover:bg-bg',
          expanded ? 'justify-start' : 'lg:justify-start justify-center',
        ]"
        @click="router.push(item.to); emit('close')"
      >
        <Icon :name="item.icon" :size="20" />
        <span class="text-body" :class="expanded ? 'inline' : 'hidden lg:inline'">{{ item.label }}</span>
      </a>
    </nav>

    <div class="p-md border-t border-border text-caption text-text3" :class="expanded ? 'block' : 'hidden lg:block'">
      v1.0 · 智能错题本
    </div>
  </div>
</template>
