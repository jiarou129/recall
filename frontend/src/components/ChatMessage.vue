<script setup lang="ts">
import type { ChatMessage } from '@/types'
import Icon from './Icon.vue'
import MathText from './MathText.vue'

defineProps<{ message: ChatMessage }>()
</script>

<template>
  <div class="flex gap-3" :class="message.role === 'user' ? 'flex-row-reverse' : 'flex-row'">
    <!-- 头像 -->
    <div
      class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full"
      :class="message.role === 'user' ? 'bg-primary text-white' : 'bg-bg text-primary'"
    >
      <Icon :name="message.role === 'user' ? 'user' : 'bot'" :size="18" />
    </div>
    <!-- 气泡 -->
    <div
      class="max-w-[78%] rounded-card border px-xl py-md text-body break-words"
      :class="
        message.role === 'user'
          ? 'bg-primary text-white border-primary'
          : 'bg-card text-text1 border-border'
      "
    >
      <MathText :text="message.content" />
    </div>
  </div>
</template>
