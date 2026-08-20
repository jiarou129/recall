<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { settingsApi } from '@/api'
import Icon from '@/components/Icon.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseInput from '@/components/BaseInput.vue'

const form = reactive({ model_name: 'deepseek-chat', api_key: '', base_url: 'https://api.deepseek.com' })
const saved = ref(false)
const loading = ref(true)
const saving = ref(false)

onMounted(async () => {
  try {
    const s = await settingsApi.get()
    Object.assign(form, s)
  } finally {
    loading.value = false
  }
})

async function save() {
  saving.value = true
  try {
    await settingsApi.update({ ...form })
    saved.value = true
    setTimeout(() => (saved.value = false), 2500)
  } catch {
    alert('保存失败，请检查网络后重试')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="p-xl overflow-auto h-full">
    <div class="max-w-content mx-auto">
      <div class="ly-card p-xl mb-md">
        <div class="flex items-center gap-2 mb-md">
          <Icon name="settings" :size="20" class="text-primary" />
          <h2 class="text-h2 text-text1">模型设置</h2>
        </div>
        <p class="text-body text-text2 mb-xl">
          Recall AI 的答疑与解析能力依赖大模型 API。请填写 DeepSeek 的模型信息，保存后立即生效。
        </p>

        <div v-if="loading" class="text-text3 text-caption">加载中…</div>
        <div v-else class="space-y-md max-w-xl">
          <BaseInput v-model="form.model_name" label="模型名称" placeholder="如 deepseek-chat" />
          <BaseInput v-model="form.api_key" label="API Key" type="password" placeholder="sk-..." />
          <BaseInput v-model="form.base_url" label="Base URL" placeholder="https://api.deepseek.com" />

          <div class="flex items-center gap-md pt-md">
            <BaseButton :disabled="saving" @click="save"><Icon name="check" :size="16" /> {{ saving ? '保存中…' : '保存设置' }}</BaseButton>
            <span v-if="saved" class="inline-flex items-center gap-1 text-caption text-success">
              <Icon name="check" :size="14" /> 已保存
            </span>
          </div>
        </div>
      </div>

      <div class="ly-card p-xl">
        <h3 class="text-h2 text-text1 mb-md">说明</h3>
        <ul class="space-y-sm text-body text-text2 list-disc pl-xl">
          <li>当前默认对接 <b>DeepSeek</b>（OpenAI 兼容接口）。</li>
          <li>未填写 API Key 时，AI 答疑会返回演示回复，不影响其他功能。</li>
          <li>如需更换为其它 OpenAI 兼容模型，修改模型名称与 Base URL 即可。</li>
        </ul>
      </div>
    </div>
  </div>
</template>
