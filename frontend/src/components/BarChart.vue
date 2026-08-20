<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    data: { label: string; count: number }[]
    color?: string
    height?: number
  }>(),
  { color: '#007AFF', height: 200 },
)

const W = 640
const PAD = 28
const max = computed(() => Math.max(1, ...props.data.map((d) => d.count)))
const slot = computed(() => (W - PAD * 2) / Math.max(1, props.data.length))
const bars = computed(() =>
  props.data.map((d, i) => {
    const h = (d.count / max.value) * (props.height - PAD * 2)
    return {
      x: PAD + i * slot.value + slot.value * 0.2,
      w: slot.value * 0.6,
      y: props.height - PAD - h,
      h,
      label: d.label.slice(5), // MM-DD
      count: d.count,
    }
  }),
)
const showLabel = computed(() => props.data.length <= 14)
</script>

<template>
  <svg :viewBox="`0 0 ${W} ${height}`" class="w-full" preserveAspectRatio="none" style="height: auto">
    <!-- 基线 -->
    <line :x1="PAD" :y1="height - PAD" :x2="W - PAD" :y2="height - PAD" stroke="#E5E5EA" stroke-width="1" />
    <!-- 网格线 -->
    <line :x1="PAD" :y1="PAD" :x2="W - PAD" :y2="PAD" stroke="#F5F5F7" stroke-width="1" />
    <line :x1="PAD" :y1="(height) / 2" :x2="W - PAD" :y2="(height) / 2" stroke="#F5F5F7" stroke-width="1" />
    <!-- 柱 -->
    <g v-for="(b, i) in bars" :key="i">
      <rect :x="b.x" :y="b.y" :width="b.w" :height="Math.max(0, b.h)" :fill="color" rx="3">
        <title>{{ b.label }} · {{ b.count }}</title>
      </rect>
      <text
        v-if="showLabel"
        :x="b.x + b.w / 2"
        :y="height - PAD + 14"
        text-anchor="middle"
        font-size="10"
        fill="#AEAEB2"
      >
        {{ b.label }}
      </text>
    </g>
  </svg>
</template>
