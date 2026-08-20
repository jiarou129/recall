<script setup lang="ts">
withDefaults(
  defineProps<{
    modelValue: string
    label?: string
    placeholder?: string
    error?: string
    type?: string
    multiline?: boolean
  }>(),
  { label: '', placeholder: '', error: '', type: 'text', multiline: false },
)
const emit = defineEmits<{ (e: 'update:modelValue', v: string): void }>()
</script>

<template>
  <label v-if="label" class="block text-caption text-text2 mb-xs">{{ label }}</label>
  <textarea
    v-if="multiline"
    :value="modelValue"
    :placeholder="placeholder"
    rows="4"
    class="ly-input resize-y"
    :class="error ? '!border-error' : ''"
    @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
  />
  <input
    v-else
    :type="type"
    :value="modelValue"
    :placeholder="placeholder"
    class="ly-input"
    :class="error ? '!border-error' : ''"
    @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
  />
  <p v-if="error" class="mt-xs text-caption text-error">{{ error }}</p>
</template>
