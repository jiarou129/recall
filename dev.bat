@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Recall AI - 开发模式(前端 + 后端)
cd /d "%~dp0"

REM ============================================================
REM  Recall AI · 开发模式一键启动（前端 + 后端）
REM  同时启动：后端 FastAPI(8000) + 前端 Vite(5173, /api 代理到 8000)
REM  适合：自己开发调试（改前端代码热更新）
REM  如需"只跑一个后端就能用页面"，请用 start.bat（打包模式）
REM ============================================================

echo ============================================================
echo    Recall AI · 开发模式（前端 + 后端）
echo    后端 : http://localhost:8000  (API)
echo    前端 : http://localhost:5173  (页面, 自动打开)
echo ============================================================
echo.

REM ---------- 0. 环境自检 ----------
set "PY="
where python >nul 2>&1 && set "PY=python"
if not defined PY where py >nul 2>&1 && set "PY=py -3"
if not defined PY (
  echo [错误] 未检测到 Python，请先安装 Python 3.10+：https://www.python.org/downloads/
  pause
  exit /b 1
)
where node >nul 2>&1
if errorlevel 1 (
  echo [错误] 未检测到 Node.js，前端无法启动：https://nodejs.org/
  pause
  exit /b 1
)
echo [0/4] 环境检测通过（Python + Node）

REM ---------- 1. 后端虚拟环境与依赖 ----------
cd /d "%~dp0\backend"
if not exist ".venv\Scripts\python.exe" (
  echo [1/4] 首次运行：创建 Python 虚拟环境...
  %PY% -m venv .venv
  if errorlevel 1 ( echo [错误] 创建虚拟环境失败 & pause & exit /b 1 )
)
".venv\Scripts\python.exe" -c "import fastapi,uvicorn,chromadb,reportlab,httpx" >nul 2>&1
if errorlevel 1 (
  echo [2/4] 首次运行：安装后端依赖（约 2-5 分钟，请勿关闭窗口）...
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 ( echo [错误] 后端依赖安装失败 & pause & exit /b 1 )
)
if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo [3/4] 已生成 backend\.env，请填入 DEEPSEEK_API_KEY（不填也能启动，但 AI/OCR 不可用）
)

REM ---------- 2. 前端依赖 ----------
cd /d "%~dp0\frontend"
if not exist "node_modules" (
  echo [4/4] 首次运行：安装前端依赖（约 1-3 分钟）...
  call npm install
  if errorlevel 1 ( echo [错误] 前端依赖安装失败 & pause & exit /b 1 )
)
echo 环境就绪。

REM ---------- 3. 端口占用检测 ----------
netstat -ano 2>nul | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
  echo [提示] 8000 端口已被占用，可能已有后端在运行。
  echo        建议先关闭旧进程，否则新后端无法启动。
)
netstat -ano 2>nul | findstr ":5173" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
  echo [提示] 5173 端口已被占用，可能已有前端在运行。
  echo        建议先关闭旧进程，否则新前端无法启动。
)

REM ---------- 4. 启动后端（新窗口） ----------
cd /d "%~dp0\backend"
start "Recall Backend" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

REM ---------- 5. 启动前端（新窗口） ----------
cd /d "%~dp0\frontend"
start "Recall Frontend" cmd /k "npm run dev"

REM ---------- 6. 打开浏览器 ----------
echo 等待服务启动...
timeout /t 8 /nobreak >nul
echo [Recall] 打开浏览器：http://localhost:5173/
start "" "http://localhost:5173/"

echo.
echo [Recall] 开发模式已启动！
echo    - 前端页面：http://localhost:5173/
echo    - 后端 API ：http://localhost:8000/api/health
echo    - 停止方式：关闭 "Recall Backend" 和 "Recall Frontend" 两个窗口
echo    - 改前端代码会自动热更新，无需重启
echo.
pause
