<script setup lang="ts">
import Icon from './Icon.vue'
withDefaults(defineProps<{ title: string; value: string | number; icon: string; accent?: string; sub?: string }>(), {
  accent: '#007AFF',
  sub: '',
})
</script>

<template>
  <div class="ly-card p-lg flex items-center gap-md">
    <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-btn" :style="{ backgroundColor: accent + '1A', color: accent }">
      <Icon :name="icon" :size="22" />
    </div>
    <div class="min-w-0">
      <p class="text-caption text-text2">{{ title }}</p>
      <p class="text-h1 text-text1 leading-tight">{{ value }}</p>
      <p v-if="sub" class="text-caption text-text3">{{ sub }}</p>
    </div>
  </div>
</template>
