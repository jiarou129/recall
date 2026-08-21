#!/usr/bin/env bash
# ============================================================
#  Recall AI 错题本 · Linux/macOS 一键启动（全自动引导版）
#  首次运行自动：检查环境 -> 建虚拟环境 -> 装依赖 -> 生成 .env
#                -> 构建前端（如缺 dist）-> 启动服务 -> 打开浏览器
# ============================================================
set -e
cd "$(dirname "$0")"
ROOT="$(pwd)"

echo "============================================================"
echo "  Recall AI 错题本 · 一键启动"
echo "============================================================"

# ---------- 1. 检查 Python ----------
if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "[错误] 未检测到 Python 3，请先安装：https://www.python.org/downloads/"
  exit 1
fi
echo "[1/5] Python: $PY"

# ---------- 2. 虚拟环境 ----------
cd "$ROOT/backend"
if [ ! -f ".venv/bin/python" ]; then
  echo "[2/5] 首次运行：创建 Python 虚拟环境..."
  "$PY" -m venv .venv
else
  echo "[2/5] 虚拟环境已就绪"
fi

# ---------- 3. 安装后端依赖 ----------
if ! .venv/bin/python -c "import fastapi,uvicorn,chromadb,reportlab,httpx" >/dev/null 2>&1; then
  echo "[3/5] 首次运行：安装后端依赖（约 2-5 分钟）..."
  .venv/bin/python -m pip install -r requirements.txt
else
  echo "[3/5] 后端依赖已就绪"
fi

# ---------- 4. 配置文件 ----------
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "[4/5] 已生成 backend/.env"
  echo "      请编辑填入 DEEPSEEK_API_KEY（不填也能启动，但 AI 功能会提示未配置）"
else
  echo "[4/5] 配置文件已就绪"
fi

# ---------- 5. 前端构建 ----------
cd "$ROOT"
if [ ! -f "frontend/dist/index.html" ]; then
  echo "[5/5] 未找到前端构建产物，准备构建（需要 Node.js 18+）..."
  if ! command -v node >/dev/null 2>&1; then
    echo "[错误] 未检测到 Node.js，无法构建前端。"
    echo "      方案 A：安装 Node.js https://nodejs.org/ 后重新运行"
    echo "      方案 B：改用「完整版（含构建产物）」压缩包（已内置 frontend/dist）"
    exit 1
  fi
  cd frontend
  echo "      安装前端依赖（约 1-3 分钟）..."
  npm install
  echo "      构建前端..."
  npm run build
  cd "$ROOT"
  echo "[5/5] 前端构建完成"
else
  echo "[5/5] 前端构建产物已就绪"
fi

echo "============================================================"
echo "  环境就绪，正在启动服务：http://localhost:8000/"
echo "============================================================"

# ---------- 启动后端（托管前端页面 + API） ----------
cd "$ROOT/backend"
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
UVPID=$!

# ---------- 等待并打开浏览器 ----------
sleep 6
if command -v xdg-open >/dev/null 2>&1; then xdg-open "http://localhost:8000/" >/dev/null 2>&1 || true; fi
if command -v open >/dev/null 2>&1; then open "http://localhost:8000/" >/dev/null 2>&1 || true; fi

echo "[Recall] 服务已启动：http://localhost:8000/   （Ctrl+C 停止）"
wait "$UVPID"
