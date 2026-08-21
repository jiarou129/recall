# ============================================================
# Recall AI · 云端部署镜像（多阶段构建）
#   阶段 1：构建前端（Vue3 + Vite + TypeScript）
#   阶段 2：Python 运行时 + 前端产物 + Chromium（PDF 公式渲染）
#
# 构建：docker build -t recall .
# 运行：docker run -p 8000:8000 -e DEEPSEEK_API_KEY=xxx -v recall-data:/app/data recall
# ============================================================

# ---------- 阶段 1：前端构建 ----------
FROM node:20-alpine AS frontend-build
WORKDIR /build/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund

COPY frontend/ .
RUN npm run build

# ---------- 阶段 2：后端运行时 ----------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Chromium（PDF 公式渲染，headless 打印）+ 中文字体
RUN apt-get update && apt-get install -y --no-install-recommends \
        chromium \
        fonts-noto-cjk \
        fonts-wqy-zenhei \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
# 前端构建产物 → 后端静态托管（http://host:8000/ 即前端页面）
COPY --from=frontend-build /build/frontend/dist /app/frontend/dist

# 数据目录（SQLite / ChromaDB），挂载持久卷防丢失
ENV SQLITE_PATH=/app/data/recall.db \
    CHROMA_PATH=/app/data/chroma
VOLUME ["/app/data"]

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
