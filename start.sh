#!/usr/bin/env bash
# Recall AI 错题本 · Linux/macOS 一键启动
# 前提：backend/.venv 已创建、依赖已安装、backend/.env 已配置

set -e
cd "$(dirname "$0")"

echo "[Recall] 启动后端服务..."
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
UVPID=$!
cd ..

sleep 4
echo "[Recall] 打开浏览器..."
if command -v xdg-open >/dev/null 2>&1; then xdg-open http://localhost:8000/; fi
if command -v open >/dev/null 2>&1; then open http://localhost:8000/; fi
echo "[Recall] 已启动，访问 http://localhost:8000/"

wait "$UVPID"