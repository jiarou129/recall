<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { HelpDoc } from '@/types'
import { helpApi } from '@/api'
import Icon from '@/components/Icon.vue'

const doc = ref<HelpDoc | null>(null)
const loading = ref(true)
const error = ref('')

async function loadDoc() {
  loading.value = true
  error.value = ''
  try {
    doc.value = await helpApi.doc()
  } catch {
    error.value = '加载失败，请检查网络后刷新重试'
  } finally {
    loading.value = false
  }
}

onMounted(loadDoc)
</script>

<template>
  <div class="p-xl overflow-auto h-full">
    <div class="max-w-content mx-auto">
      <div v-if="loading" class="text-text3 text-caption py-2xl text-center">加载中…</div>

    <div v-else-if="error" class="text-center py-2xl">
      <p class="text-body text-error mb-md">{{ error }}</p>
      <button class="rounded-btn border border-border px-4 h-9 text-caption text-primary" @click="loadDoc">重试</button>
    </div>

      <template v-else-if="doc">
        <div class="ly-card p-2xl mb-md">
          <div class="flex items-center gap-3 mb-md">
            <div class="flex h-11 w-11 items-center justify-center rounded-btn bg-primary text-white">
              <Icon name="help" :size="22" />
            </div>
            <div>
              <h1 class="text-h1 text-text1">{{ doc.title }}</h1>
              <p class="text-body text-text2 mt-xs">{{ doc.intro }}</p>
            </div>
          </div>
        </div>

        <div class="space-y-md">
          <div v-for="(s, i) in doc.sections" :key="i" class="ly-card p-xl">
            <div class="flex items-start gap-3">
              <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-bg text-primary text-caption font-medium">{{ i + 1 }}</span>
              <div>
                <h3 class="text-h2 text-text1">{{ s.title }}</h3>
                <p class="text-body text-text2 mt-xs whitespace-pre-wrap">{{ s.body }}</p>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
