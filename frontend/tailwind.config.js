/** @type {import('tailwindcss').Config} */
// Recall AI · 设计令牌（来自 ly-design 设计系统，极简蓝调 Apple 变体）
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#007AFF',
        bg: '#F5F5F7',
        card: '#FFFFFF',
        border: '#E5E5EA',
        text1: '#1D1D1F',
        text2: '#6E6E73',
        text3: '#AEAEB2',
        success: '#34C759',
        warning: '#FF9500',
        error: '#FF3B30',
        question: '#3B82F6',
        answer: '#10B981',
        // 错题本 8 色（科目标签）
        cat: {
          1: '#0A84FF',
          2: '#34C759',
          3: '#FF9500',
          4: '#AF52DE',
          5: '#FF2D55',
          6: '#32ADE6',
          7: '#FFCC00',
          8: '#5856D6',
        },
      },
      fontFamily: {
        sans: [
          'PingFang SC',
          '钉钉进步体',
          'SF Pro Text',
          'SF Pro Display',
          '-apple-system',
          'BlinkMacSystemFont',
          'Helvetica Neue',
          'Microsoft YaHei',
          'sans-serif',
        ],
      },
      fontSize: {
        h1: ['28px', { lineHeight: '36px', fontWeight: '600' }],
        h2: ['20px', { lineHeight: '28px', fontWeight: '600' }],
        body: ['14px', { lineHeight: '20px' }],
        caption: ['12px', { lineHeight: '16px' }],
      },
      spacing: {
        xs: '4px',
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '24px',
        '2xl': '32px',
      },
      borderRadius: {
        btn: '8px',
        card: '12px',
        tag: '6px',
      },
      maxWidth: {
        content: '1200px',
      },
    },
  },
  plugins: [],
  // 全局禁用阴影，符合 ly-design「无阴影」原则
  corePlugins: {
    boxShadow: false,
  },
}
