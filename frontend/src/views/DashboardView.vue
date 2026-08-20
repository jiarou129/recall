<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { DashboardStats } from '@/types'
import { dashboardApi } from '@/api'
import Icon from '@/components/Icon.vue'
import StatCard from '@/components/StatCard.vue'
import BarChart from '@/components/BarChart.vue'

const stats = ref<DashboardStats | null>(null)
const loading = ref(true)
const error = ref('')

async function loadStats() {
  loading.value = true
  error.value = ''
  try {
    stats.value = await dashboardApi.stats()
  } catch {
    error.value = '加载失败，请检查网络后刷新重试'
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<template>
  <div class="p-xl overflow-auto h-full">
    <p class="text-caption text-text3 mb-xl">最近 30 天学习概览</p>

    <div v-if="loading" class="text-center text-text3 py-2xl">加载中…</div>

    <div v-else-if="error" class="text-center py-2xl">
      <p class="text-body text-error mb-md">{{ error }}</p>
      <button class="rounded-btn border border-border px-4 h-9 text-caption text-primary" @click="loadStats">重试</button>
    </div>

    <template v-else-if="stats">
      <!-- 指标卡 -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-md mb-xl">
        <StatCard title="题目总数" :value="stats.total_questions" icon="book" accent="#007AFF" sub="累计录入错题" />
        <StatCard title="复习次数" :value="stats.total_reviews" icon="refresh" accent="#34C759" sub="累计复习动作" />
        <StatCard title="错题成功率" :value="stats.success_rate + '%'" icon="target" accent="#0A84FF" sub="已掌握占比" />
        <StatCard title="待复习" :value="stats.pending_review" icon="clock" accent="#FF9500" sub="未掌握 + 复习中" />
      </div>

      <!-- 图表 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-md">
        <div class="ly-card p-xl">
          <div class="flex items-center gap-2 mb-md">
            <Icon name="refresh" :size="18" class="text-primary" />
            <h3 class="text-h2 text-text1">最近一个月学习情况</h3>
          </div>
          <p class="text-caption text-text3 mb-md">按天统计复习次数</p>
          <BarChart :data="stats.study_series.map((d) => ({ label: d.date, count: d.count }))" color="#007AFF" :height="200" />
        </div>

        <div class="ly-card p-xl">
          <div class="flex items-center gap-2 mb-md">
            <Icon name="doc" :size="18" class="text-answer" />
            <h3 class="text-h2 text-text1">最近一个月错题录入</h3>
          </div>
          <p class="text-caption text-text3 mb-md">按天统计新增错题</p>
          <BarChart :data="stats.entry_series.map((d) => ({ label: d.date, count: d.count }))" color="#10B981" :height="200" />
        </div>
      </div>

      <!-- 学科分布 -->
      <div class="ly-card p-xl mt-md" v-if="stats.by_subject.length">
        <div class="flex items-center gap-2 mb-md">
          <Icon name="chart" :size="18" class="text-warning" />
          <h3 class="text-h2 text-text1">学科分布</h3>
        </div>
        <div class="flex flex-wrap gap-md">
          <div
            v-for="s in stats.by_subject"
            :key="s.subject"
            class="flex items-center gap-sm rounded-tag border border-border px-md py-sm text-body text-text2"
          >
            <span>{{ s.subject }}</span>
            <span class="text-primary font-medium">{{ s.count }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
