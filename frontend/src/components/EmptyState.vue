<script setup lang="ts">
import Icon from './Icon.vue'
defineProps<{ icon?: string; title: string; desc?: string }>()
</script>

<template>
  <div class="flex flex-col items-center justify-center rounded-card border border-border bg-card py-2xl px-xl text-center">
    <div class="flex h-12 w-12 items-center justify-center rounded-full bg-bg text-text3">
      <Icon :name="icon || 'book'" :size="24" />
    </div>
    <p class="mt-md text-body text-text1 font-medium">{{ title }}</p>
    <p v-if="desc" class="mt-xs text-caption text-text2">{{ desc }}</p>
    <slot name="action" />
  </div>
</template>
