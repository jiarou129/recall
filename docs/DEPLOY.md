# ☁️ 完整云端部署指南

让 Recall 跑在云上：**对方打开一个网址就能真正用**（录题、AI 解析、复习、数据全部在线，无需安装任何东西）。

> 适用：想把应用真正部署给他人使用的场景。与 `docs/` 里其他文档的差异：
> `README.md` 讲本地运行，`DEVELOPMENT.md` 讲技术实现，本指南讲**上云**。

---

## 一、总体架构（云端）

```
访客浏览器
   │  https://<你的服务>.onrender.com
   ▼
Render 云实例（Docker 镜像）
   ├── FastAPI 后端（uvicorn :8000）
   ├── 前端 dist（由后端托管在 /）      ← 一个端口同时 serving 前后端
   ├── SQLite + ChromaDB（挂载持久卷 /app/data，重启不丢）
   └── Chromium（headless，用于 PDF 公式渲染）
          │
          ▼
   SiliconFlow / DeepSeek API（AI 解析 / 视觉 OCR）
```

## 二、准备清单（一次性）

| 项 | 说明 |
|---|---|
| GitHub 仓库 | 已有：`jiarou129/recall`（本仓库已含 `Dockerfile`、`render.yaml`） |
| Render 账号 | 免费注册 [render.com](https://render.com)（支持 GitHub 登录） |
| 大模型 API Key | 你的 `DEEPSEEK_API_KEY`（SiliconFlow / DeepSeek），部署时填入平台环境变量 |

## 三、部署步骤（Render，推荐）

1. **注册并登录** [render.com](https://render.com)（用 GitHub 账号直接登录，免费）。
2. 右上角 **New + → Blueprint**，选择 `jiarou129/recall` 仓库。
3. Render 读取 `render.yaml`，自动创建名为 `recall` 的 Web Service（Docker 运行时）。
4. 首次部署时，在 **Environment** 里填写 `DEEPSEEK_API_KEY`（其余变量已在 `render.yaml` 预设）。
   > 也可以在 `render.yaml` 的 `envVars` 中把 `sync: false` 改为 `sync: true` 并直接写入值，但**不要把 Key 提交到仓库**。
5. 点击 **Apply / Deploy**，等待镜像构建（首次约 3–8 分钟）。
6. 部署完成后，服务会分配一个公网地址，形如 `https://recall-xxxx.onrender.com`。
   - 打开该地址 = 打开前端页面；
   - `https://recall-xxxx.onrender.com/api/health` 应返回 `{"status":"ok","product":"Recall AI"}`。

## 四、环境变量清单

| 变量 | 必填 | 说明 |
|---|---|---|
| `DEEPSEEK_API_KEY` | ✅ | 大模型 API Key（SiliconFlow / DeepSeek），**绝不入库** |
| `DEEPSEEK_MODEL` | 否 | 默认 `deepseek-ai/DeepSeek-V3.2`（对话/解析/视觉 OCR） |
| `DEEPSEEK_BASE_URL` | 否 | 默认 `https://api.siliconflow.cn/v1` |
| `PORT` | 否 | 默认 `8000`，平台会自动注入 |
| `SQLITE_PATH` | 否 | 默认 `/app/data/recall.db`（持久卷内） |
| `CHROMA_PATH` | 否 | 默认 `/app/data/chroma`（持久卷内） |

## 五、数据持久化

- 后端把数据库与向量库放在 `/app/data/`，Docker 镜像声明了 `VOLUME`，Render 的 `disk` 配置把它挂到持久磁盘。
- **默认数据是全新的空库**（云上与你的本地 `backend/data/` 互不相通）。
- 想把本地的错题带到云端：停服 → 用 Render 的 Shell/磁盘功能上传本地 `recall.db` 到 `/app/data/` → 重启。
- 想下载云端数据：同样通过 Render 磁盘或服务日志导出。

## 六、多人共用说明（重要，请先想清楚）

当前架构是**单租户**：所有访问者共用同一个数据库和同一个 API Key。

- 访客 A 录入的错题，访客 B 也能看到/修改；
- 所有人的 AI 请求都消耗**你的** API Key 额度；
- 若要多人隔离，需要再加登录/账号体系（后续迭代项）。

适合：小团队共用、给朋友/同学共用、作品展示。不适合：对外公开的大规模免费服务。

## 七、其他平台（通用 Docker）

只要平台支持 Docker 容器即可，本仓库的 `Dockerfile` 通用：

- **Railway**：`railway init` → 关联仓库 → 设置环境变量 → 添加 Volume 挂载 `/app/data`。
- **腾讯云 CloudBase（云托管）**：上传镜像或关联 Git → 环境变量同上 → 挂载 `/app/data`。
- **自己的 VPS**：`docker build -t recall . && docker run -d -p 8000:8000 -e DEEPSEEK_API_KEY=xxx -v recall-data:/app/data recall`。

## 八、常见问题

| 问题 | 处理 |
|---|---|
| 部署后 `/api/health` 返回 404 | 等服务构建完成、状态变 Live 再试 |
| 页面能开但 AI 解析报"未配置" | 检查环境变量 `DEEPSEEK_API_KEY` 是否已填且服务已重启 |
| 重启后数据丢失 | 确认持久卷挂载正常（`/app/data`）；免费实例睡眠唤醒一般不会丢数据 |
| PDF 导出公式仍是源码 | 确认镜像内含 chromium（本 Dockerfile 已装）；可用 `_find_browser` 日志排查 |
| 免费实例冷启动慢 | Render 免费层闲置会休眠，首次访问需等 30–60 秒唤醒（属正常） |

## 九、安全提示

- `DEEPSEEK_API_KEY` 只放平台环境变量，**绝不写进代码/仓库**（`.gitignore` 已拦截 `.env`）。
- 若想对外公开且限制用量：在反向代理（如 Cloudflare）加限流，或后续接入登录体系。
- 定期从云端备份 `recall.db`。
