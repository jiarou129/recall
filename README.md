# Recall AI · 智能错题本

> 拍照 / 截图 / 文本 / 对话，四种方式录入错题；AI 自动识别题目、生成解析、按 SM-2 算法规划复习，帮你把错题真正变成分数。

Recall 是一款面向学生（中学 / 大学 / 考研）的 AI 错题管理平台。它把"录入—解析—复习—统计"整合成一条顺畅的学习闭环，让整理错题这件事从负担变成习惯。

---

## 📌 项目简介

传统错题本靠手抄，费时且难以坚持。Recall 用 AI 把这件事自动化：

- **录入**：上传题目截图，AI 视觉模型直接识别图中的题目文字（含 LaTeX 公式）；也支持手动录入、AI 对话一键入本。
- **解析**：一键让 AI 生成完整解题步骤（思路 / 解答 / 答案 / 易错提醒），数学公式用 KaTeX 渲染成可读样式。
- **复习**：基于 SM-2 记忆算法生成每日 / 周度 / 考前复习计划，AI 生成变体题并自动批改评分。
- **洞察**：数据看板展示学习趋势与知识图谱，支持 PDF / Markdown 导出。

技术定位：**本地优先**（SQLite 本地存储，数据不出本机），前后端分离，AI 能力通过 OpenAI 兼容接口接入（DeepSeek / SiliconFlow 等）。

---

## ✨ 特性列表

| 分类 | 特性 |
|---|---|
| **错题录入** | 图片 OCR 识别（AI 视觉，降级本地 PaddleOCR-VL）、文本录入、AI 对话一键入本 |
| **AI 解析** | 自动生成【思路】【解答】【答案】【易错提醒】，支持 LaTeX 公式渲染 |
| **错题管理** | 分类、学科、知识点、来源标签；编辑 / 删除 / 多选批量操作 |
| **一键复习** | SM-2 记忆引擎驱动，逐题作答 + AI 批改评分 |
| **复习计划** | 按遗忘曲线生成每日 / 周度 / 考前复习清单 |
| **数据看板** | 学习趋势、掌握度、知识图谱可视化 |
| **导出** | 错题集 PDF / Markdown 一键导出 |
| **AI 对话** | 流式问答，可直接把对话结论加入错题本 |
| **帮助中心** | 内置使用说明与常见问题 |
| **公式渲染** | KaTeX 支持 `$...$` `$$...$$` `\(...\)` `\[...\]` 四种 LaTeX 定界符 |
| **本地优先** | SQLite + ChromaDB 本地存储，无需上云 |

---

## 📚 项目文档

| 文档 | 面向 | 内容 |
|---|---|---|
| [`README.md`](./README.md) | 使用者 | 安装、配置、使用、贡献指引 |
| [`docs/PRD.md`](./docs/PRD.md) | 产品/决策 | 产品背景、用户画像、功能流程、需求规格 |
| [`docs/DEVELOPMENT.md`](./docs/DEVELOPMENT.md) | 开发者 | 架构、API 契约、数据模型、关键模块设计、扩展指南 |
| [`docs/TEST_REPORT.md`](./docs/TEST_REPORT.md) | 测试/质量 | 功能/非功能测试用例、真实质量门禁结果、缺陷与结论 |

---

## 🚀 安装步骤

> 环境要求：Node.js 18+（前端）、Python 3.12+（后端，推荐 3.13）。

### 1. 克隆 / 进入项目

```bash
cd recall
```

### 2. 启动后端（FastAPI）

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
# Windows 激活：
.venv\Scripts\activate
# macOS / Linux 激活：
# source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置大模型（复制示例并填入你的 API Key）
cp .env.example .env
# 用编辑器打开 .env，填入 DEEPSEEK_API_KEY 等

# 启动服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

后端启动后访问 `http://localhost:8000/api/health` 应返回 `{"status":"ok","product":"Recall AI"}`。

### 3. 启动前端（Vue 3 + Vite）

```bash
cd frontend

npm install

npm run dev
```

前端默认运行在 `http://localhost:5173`，开发模式下已配置 `/api` 代理到 `http://localhost:8000`，无需额外跨域配置。

## 📦 打包版运行（无需 npm run dev）

如果你拿到的是**已包含 `frontend/dist/` 的压缩包**，只需启动后端即可同时访问前端页面：

```bash
cd recall

# 前提：backend/.venv 已创建、依赖已安装、backend/.env 已配置

# Windows 直接双击
start.bat

# macOS / Linux
chmod +x start.sh
./start.sh
```

然后浏览器访问 `http://localhost:8000/`。

原理：`frontend/dist/` 构建完成后，FastAPI 会自动把它托管在 `/`；所有 API 仍走 `/api/*`。因此一个端口 `8000` 就能同时 serving 前端和后端，部署/演示更简单。

### 生产构建（可选）

```bash
cd frontend
npm run build      # 产物输出到 dist/
npm run preview    # 本地预览构建结果
```

构建产物在 `frontend/dist/`，后端启动后会自动托管。

---

## 💡 代码示例

### 健康检查

```bash
curl http://localhost:8000/api/health
# => {"status":"ok","product":"Recall AI"}
```

### 图片 OCR 识别（Python）

```python
import requests

with open("math_problem.png", "rb") as f:
    resp = requests.post(
        "http://localhost:8000/api/upload/ocr",
        files={"file": f},
    ).json()

if resp["available"]:
    print("识别结果：", resp["text"])   # 含 LaTeX 公式的题目文本
else:
    print("失败原因：", resp["message"])
```

### 让 AI 解析一道题（JavaScript / TypeScript）

```ts
import axios from 'axios'

// 前端通过 /api 代理访问后端
const res = await axios.post('/api/chat/solve', {
  question: '求极限 $\\lim_{x \\to 0} \\frac{\\int_0^x (e^{t^2}-1)dt}{x^2 \\sin 2x}$',
})

if (res.data.available) {
  console.log('AI 解析：', res.data.answer)
  // => 【思路】...【解答】...【答案】...【易错提醒】...
}
```

### 获取错题列表（前端 API 封装示例）

```ts
import { mistakesApi } from '@/api'

// 按分类 + 关键词筛选
const list = await mistakesApi.list({
  category_id: 1,
  q: '椭圆',
  status: 'pending',   // 待复习 / 已掌握 等
})
list.forEach((m) => console.log(m.question, m.subject))
```

---

## ⚙️ 配置说明

后端通过根目录 `backend/.env` 读取配置（参考 `backend/.env.example`）：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `DEEPSEEK_API_KEY` | 空 | 大模型 API Key（DeepSeek / SiliconFlow 等 OpenAI 兼容服务） |
| `DEEPSEEK_MODEL` | `deepseek-chat` | 用于对话、解析、视觉 OCR 的模型名（如 `deepseek-ai/DeepSeek-V3.2`、`Qwen/Qwen3-VL-8B-Instruct`） |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | 模型服务地址（SiliconFlow 用户填 `https://api.siliconflow.cn/v1`） |
| `SQLITE_PATH` | `./data/recall.db` | SQLite 数据库文件路径 |
| `CHROMA_PATH` | `./data/chroma` | ChromaDB 向量库路径 |
| `PORT` | `8000` | 后端监听端口 |

**OCR 说明**：优先使用 `DEEPSEEK_MODEL` 配置的视觉模型做题目识别（`vision_ocr`）；若未配置 API Key，自动降级到本地 `PaddleOCR-VL`（需另行 `pip install paddlepaddle paddleocr`）。两者都不可用时，上传接口会返回友好的"未配置"提示，不影响其他功能。

**前端配置**：代理规则在 `frontend/vite.config.ts` 中，已将 `/api` 代理到 `http://localhost:8000`。

---

## 🤝 贡献指引

欢迎提交 Issue 与 Pull Request！

1. **Fork** 本仓库并创建特性分支：`git checkout -b feat/your-feature`
2. **本地验证**：
   - 后端：`pip install -r requirements.txt` 后正常启动 `uvicorn`
   - 前端：`npm install` + `npm run dev`，并运行类型检查 `npm run typecheck`（要求零错误）
3. **提交规范**：Commit Message 建议遵循 `type(scope): description`，如 `feat(ocr): 支持截图批量识别`、`fix(ui): 修复卡片等高空白`
4. **PR 描述**请说明：改动动机、涉及模块、自测结果
5. 提交前请确保不泄露个人 `.env`、API Key 与本地数据库文件

> 本项目处于早期活跃开发阶段，重大结构变更请先在 Issue 中讨论。

---

## 📄 许可证信息

本项目采用 **MIT License**。详见仓库根目录 [`LICENSE`](./LICENSE) 文件。

---

<p align="center">用 Recall，把每一道错题都变成下一次的得分。</p>
