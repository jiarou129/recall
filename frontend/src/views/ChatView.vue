<script setup lang="ts">
import { onMounted, ref, nextTick, watch } from 'vue'
import type { ChatMessage, ChatSession } from '@/types'
import { chatApi } from '@/api'
import Icon from '@/components/Icon.vue'
import BaseButton from '@/components/BaseButton.vue'
import ChatMessageComp from '@/components/ChatMessage.vue'
import EmptyState from '@/components/EmptyState.vue'

const sessions = ref<ChatSession[]>([])
const activeId = ref<number | null>(null)
const messages = ref<ChatMessage[]>([])
const input = ref('')
const sending = ref(false)
const scrollEl = ref<HTMLElement | null>(null)

const SUGGESTIONS = [
  '帮我讲解这道题的解题思路',
  '为什么我这里会算错？',
  '总结一下这个知识点的易错点',
  '给我出一道类似的练习题',
]

async function loadSessions() {
  sessions.value = await chatApi.sessions()
  if (!activeId.value && sessions.value.length) {
    await selectSession(sessions.value[0].id)
  }
}
async function selectSession(id: number) {
  activeId.value = id
  messages.value = await chatApi.messages(id)
  await scrollBottom()
}
async function newSession() {
  const s = await chatApi.createSession()
  sessions.value = [s, ...sessions.value]
  await selectSession(s.id)
}
async function removeSession(id: number) {
  if (!confirm('删除该对话？')) return
  await chatApi.remove(id)
  sessions.value = sessions.value.filter((s) => s.id !== id)
  if (activeId.value === id) {
    activeId.value = null
    messages.value = []
    if (sessions.value.length) await selectSession(sessions.value[0].id)
  }
}
async function send() {
  const text = input.value.trim()
  if (!text || sending.value) return
  let sid = activeId.value
  if (!sid) {
    await newSession()
    sid = activeId.value
  }
  if (!sid) return
  input.value = ''
  sending.value = true
  try {
    messages.value = await chatApi.send(sid, text)
    await scrollBottom()
  } finally {
    sending.value = false
  }
}
async function scrollBottom() {
  await nextTick()
  if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight
}

onMounted(loadSessions)
watch(messages, scrollBottom)
</script>

<template>
  <div class="flex h-full">
    <!-- 会话列表 -->
    <aside class="hidden md:flex w-64 shrink-0 flex-col border-r border-border bg-card">
      <div class="p-md border-b border-border">
        <BaseButton block @click="newSession"><Icon name="plus" :size="16" /> 新建对话</BaseButton>
      </div>
      <div class="flex-1 overflow-auto p-md space-y-1">
        <div
          v-for="s in sessions"
          :key="s.id"
          class="group flex items-center gap-2 rounded-btn px-3 h-10 cursor-pointer transition-colors"
          :class="activeId === s.id ? 'bg-bg text-primary font-medium' : 'text-text2 hover:bg-bg'"
          @click="selectSession(s.id)"
        >
          <Icon name="chat" :size="16" />
          <span class="flex-1 truncate text-body">{{ s.title }}</span>
          <button class="opacity-0 group-hover:opacity-100 text-text3 hover:text-error" @click.stop="removeSession(s.id)">
            <Icon name="trash" :size="14" />
          </button>
        </div>
        <p v-if="!sessions.length" class="text-caption text-text3 px-3 py-md">暂无对话</p>
      </div>
    </aside>

    <!-- 聊天区 -->
    <div class="flex flex-1 min-w-0 flex-col">
      <!-- 移动端会话切换 -->
      <div class="md:hidden p-md border-b border-border">
        <div class="flex gap-md items-center">
          <select v-if="sessions.length" :value="activeId ?? ''" class="ly-input" @change="selectSession(Number(($event.target as HTMLSelectElement).value))">
            <option v-for="s in sessions" :key="s.id" :value="s.id">{{ s.title }}</option>
          </select>
          <BaseButton size="sm" @click="newSession"><Icon name="plus" :size="14" /> 新对话</BaseButton>
        </div>
      </div>

      <div ref="scrollEl" class="flex-1 overflow-auto p-xl space-y-lg">
        <!-- 欢迎 -->
        <EmptyState
          v-if="!messages.length"
          icon="sparkles"
          title="我是 Recall AI 学习助手"
          desc="针对你的错题提问，我会分步骤讲解思路与易错点。"
        >
          <template #action>
            <div class="mt-md grid grid-cols-1 sm:grid-cols-2 gap-sm max-w-md">
              <button
                v-for="s in SUGGESTIONS" :key="s"
                class="rounded-btn border border-border bg-card px-md py-sm text-caption text-text2 hover:border-primary hover:text-primary text-left"
                @click="input = s; send()"
              >{{ s }}</button>
            </div>
          </template>
        </EmptyState>

        <ChatMessageComp v-for="m in messages" :key="m.id" :message="m" />
        <div v-if="sending" class="flex gap-3">
          <div class="flex h-8 w-8 items-center justify-center rounded-full bg-bg text-primary"><Icon name="bot" :size="18" /></div>
          <div class="rounded-card border border-border bg-card px-xl py-md text-text3 text-body">正在思考…</div>
        </div>
      </div>

      <!-- 输入栏 -->
      <div class="border-t border-border bg-card p-md">
        <div class="flex items-end gap-md max-w-content mx-auto">
          <textarea
            v-model="input"
            rows="1"
            placeholder="输入你的问题，回车发送（Shift+回车换行）"
            class="ly-input resize-none"
            @keydown.enter.exact.prevent="send"
          />
          <BaseButton :disabled="!input.trim() || sending" @click="send">
            <Icon name="send" :size="16" /> 发送
          </BaseButton>
        </div>
      </div>
    </div>
  </div>
</template>
