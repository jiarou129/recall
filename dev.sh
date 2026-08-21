#!/usr/bin/env bash
# ============================================================
#  Recall AI · 开发模式一键启动（前端 + 后端）
#  同时启动：后端 FastAPI(8000) + 前端 Vite(5173, /api 代理到 8000)
#  适合：自己开发调试（改前端代码热更新）
#  如需"只跑一个后端就能用页面"，请用 start.sh（打包模式）
# ============================================================
set -e
cd "$(dirname "$0")"
ROOT="$(pwd)"

echo "============================================================"
echo "  Recall AI · 开发模式（前端 + 后端）"
echo "  后端 : http://localhost:8000  (API)"
echo "  前端 : http://localhost:5173  (页面)"
echo "============================================================"

# ---------- 环境检测 ----------
if command -v python3 >/dev/null 2>&1; then PY=python3; elif command -v python >/dev/null 2>&1; then PY=python; else
  echo "[错误] 未检测到 Python 3：https://www.python.org/downloads/"; exit 1; fi
if ! command -v node >/dev/null 2>&1; then
  echo "[错误] 未检测到 Node.js：https://nodejs.org/"; exit 1; fi
echo "[0/4] 环境检测通过（Python + Node）"

# ---------- 后端环境 ----------
cd "$ROOT/backend"
[ -f ".venv/bin/python" ] || { echo "[1/4] 创建 Python 虚拟环境..."; "$PY" -m venv .venv; }
if ! .venv/bin/python -c "import fastapi,uvicorn,chromadb,reportlab,httpx" >/dev/null 2>&1; then
  echo "[2/4] 安装后端依赖（约 2-5 分钟）..."
  .venv/bin/python -m pip install -r requirements.txt
fi
[ -f ".env" ] || { cp .env.example .env; echo "[3/4] 已生成 backend/.env，请填入 DEEPSEEK_API_KEY（不填也能启动，但 AI/OCR 不可用）"; }

# ---------- 前端依赖 ----------
cd "$ROOT/frontend"
if [ ! -d "node_modules" ]; then
  echo "[4/4] 安装前端依赖（约 1-3 分钟）..."
  npm install
fi
echo "环境就绪。"

# ---------- 启动后端 ----------
cd "$ROOT/backend"
.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACK_PID=$!

# ---------- 启动前端 ----------
cd "$ROOT/frontend"
npm run dev &
FRONT_PID=$!

# ---------- 打开浏览器 ----------
sleep 8
if command -v xdg-open >/dev/null 2>&1; then xdg-open "http://localhost:5173/" >/dev/null 2>&1 || true; fi
if command -v open >/dev/null 2>&1; then open "http://localhost:5173/" >/dev/null 2>&1 || true; fi

echo "[Recall] 开发模式已启动"
echo "  前端 : http://localhost:5173/"
echo "  后端 : http://localhost:8000/api/health"
echo "  停止 : Ctrl+C"

wait "$BACK_PID" "$FRONT_PID"
