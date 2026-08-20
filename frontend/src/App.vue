<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppSidebar from '@/components/AppSidebar.vue'
import Icon from '@/components/Icon.vue'

const route = useRoute()
const router = useRouter()
const mobileOpen = ref(false)
const title = computed(() => (route.meta.title as string) || 'Recall AI')

function onNew() {
  mobileOpen.value = false
  // 用时间戳保证 query.new 每次都变化，从而能反复触发 HomeView 的监听打开弹窗
  router.push({ path: '/', query: { new: Date.now().toString() } })
}
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-bg">
    <!-- 桌面/平板侧栏 -->
    <aside class="hidden md:flex md:w-[72px] lg:w-60 shrink-0">
      <AppSidebar @new="onNew" />
    </aside>

    <!-- 移动端抽屉 -->
    <Teleport to="body">
      <div v-if="mobileOpen" class="fixed inset-0 z-40 md:hidden">
        <div class="absolute inset-0 bg-black/30" @click="mobileOpen = false" />
        <div class="absolute left-0 top-0 h-full w-64 max-w-[80%]">
          <AppSidebar expanded @new="onNew" @close="mobileOpen = false" />
        </div>
      </div>
    </Teleport>

    <!-- 主区 -->
    <div class="flex flex-1 flex-col min-w-0">
      <!-- 顶栏（移动端显示菜单） -->
      <header class="flex h-16 shrink-0 items-center gap-md border-b border-border bg-card px-xl">
        <button class="md:hidden text-text2" @click="mobileOpen = true">
          <Icon name="menu" :size="22" />
        </button>
        <h1 class="text-h2 text-text1">{{ title }}</h1>
      </header>

      <main class="flex-1 overflow-auto">
        <router-view />
      </main>
    </div>
  </div>
</template>
