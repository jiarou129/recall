<script setup lang="ts">
/**
 * 数学文本渲染：支持混合排版（含 LaTeX 公式）。
 * 把字符串里的 LaTeX 段（$...$ / $$...$$ / \( ... \) / \[ ... \]）用 KaTeX 渲染，其余保留为纯文本。
 */
import { computed } from 'vue'
import katex from 'katex'

const props = withDefaults(
  defineProps<{ text: string; block?: boolean; muted?: boolean }>(),
  { block: false, muted: false },
)

interface Segment {
  type: 'text' | 'math'
  value: string
  display: boolean
}

const segments = computed<Segment[]>(() => {
  const s = props.text || ''
  const segs: Segment[] = []
  // 同时匹配 $$...$$（块级）、\[...\]（块级）、\(...\)（行内）、$...$（行内）
  const re = /\$\$([\s\S]+?)\$\$|\\\[(?:\s*([\s\S]+?)\s*)\\\]|\\\(([\s\S]+?)\\\)|\$([^$\n]+?)\$/g
  let last = 0
  let m: RegExpExecArray | null
  while ((m = re.exec(s)) !== null) {
    if (m.index > last) segs.push({ type: 'text', value: s.slice(last, m.index), display: false })
    // 去掉公式首尾空白/换行，避免 KaTeX 解析多余空行
    const raw = m[1] !== undefined ? m[1] : m[2] !== undefined ? m[2] : m[3] !== undefined ? m[3] : m[4]
    const value = raw.trim()
    const display = m[1] !== undefined || m[2] !== undefined
    segs.push({ type: 'math', value, display })
    last = m.index + m[0].length
  }
  if (last < s.length) segs.push({ type: 'text', value: s.slice(last), display: false })
  return segs
})

function render(seg: Segment): string {
  if (seg.type === 'text') return seg.value
  try {
    return katex.renderToString(seg.value, { throwOnError: false, displayMode: seg.display })
  } catch (e) {
    // 渲染失败时保留原始源码，用户至少能看到内容；外层样式会标灰提示
    return `<span class="math-fallback" title="公式渲染失败，显示源码">${seg.value.replace(/</g, '&lt;')}</span>`
  }
}
</script>

<template>
  <span class="math-text" :class="muted ? 'text-text2' : ''">
    <template v-for="(seg, i) in segments" :key="i">
      <span v-if="seg.type === 'text'" class="whitespace-pre-wrap">{{ seg.value }}</span>
      <span v-else v-html="render(seg)" class="katex-inline" :class="seg.display ? 'katex-block' : ''" />
    </template>
  </span>
</template>

<style scoped>
.math-text { line-height: 1.7; color: inherit; }
.katex-inline { display: inline-block; }
.katex-block {
  display: block;
  margin: 6px 0;
  overflow-x: auto;
  overflow-y: hidden;
  max-width: 100%;
}
.math-fallback {
  display: inline;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  background: rgba(174, 174, 178, 0.15);
  border-radius: 4px;
  padding: 0 4px;
  color: inherit;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>