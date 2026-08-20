<script setup lang="ts">
import { computed } from 'vue'

const CAT_COLORS: Record<number, string> = {
  1: '#0A84FF', 2: '#34C759', 3: '#FF9500', 4: '#AF52DE',
  5: '#FF2D55', 6: '#32ADE6', 7: '#FFCC00', 8: '#5856D6',
}

const props = withDefaults(
  defineProps<{ label: string; color?: number | string; filled?: boolean }>(),
  { color: 1, filled: false },
)

const hex = computed(() => {
  if (typeof props.color === 'string') return props.color
  return CAT_COLORS[props.color] || CAT_COLORS[1]
})
const style = computed(() =>
  props.filled
    ? { backgroundColor: hex.value, color: '#fff', borderColor: hex.value }
    : { color: hex.value, borderColor: hex.value, backgroundColor: 'transparent' },
)
</script>

<template>
  <span
    class="inline-flex items-center rounded-tag border px-2 py-0.5 text-caption leading-4"
    :style="style"
  >
    {{ label }}
  </span>
</template>
