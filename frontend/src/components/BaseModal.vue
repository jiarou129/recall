<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
const props = defineProps<{ modelValue: boolean; title?: string }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void }>()
function close() {
  emit('update:modelValue', false)
}
function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.modelValue) close()
}
onMounted(() => document.addEventListener('keydown', onKey))
onUnmounted(() => document.removeEventListener('keydown', onKey))
</script>

<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4"
      @click.self="close"
    >
      <div class="w-full max-w-lg rounded-card border border-border bg-card">
        <div class="flex items-center justify-between border-b border-border px-xl py-md">
          <h3 class="text-h2 text-text1">{{ title }}</h3>
          <button class="text-text3 hover:text-text1" @click="close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M6 6l12 12M18 6 6 18"/></svg>
          </button>
        </div>
        <div class="px-xl py-lg max-h-[70vh] overflow-auto">
          <slot />
        </div>
        <div v-if="$slots.footer" class="flex justify-end gap-md border-t border-border px-xl py-md">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Teleport>
</template>
