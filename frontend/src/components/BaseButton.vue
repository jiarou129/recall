<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    variant?: 'primary' | 'secondary' | 'text'
    size?: 'sm' | 'md' | 'lg'
    disabled?: boolean
    block?: boolean
    type?: 'button' | 'submit'
  }>(),
  { variant: 'primary', size: 'md', disabled: false, block: false, type: 'button' },
)

const cls = computed(() => {
  const base =
    'inline-flex items-center justify-center gap-1.5 rounded-btn font-medium transition-colors select-none disabled:opacity-40 disabled:cursor-not-allowed'
  const sizes: Record<string, string> = {
    sm: 'h-8 px-3 text-caption',
    md: 'h-10 px-4 text-body',
    lg: 'h-11 px-5 text-body',
  }
  const variants: Record<string, string> = {
    primary: 'bg-primary text-white hover:opacity-90',
    secondary: 'bg-card border border-border text-primary hover:bg-bg',
    text: 'bg-transparent text-primary hover:bg-bg',
  }
  return [base, sizes[props.size], variants[props.variant], props.block ? 'w-full' : '']
})
</script>

<template>
  <button :type="type" :disabled="disabled" :class="cls">
    <slot />
  </button>
</template>
