@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title Recall AI 错题本 - 一键启动
cd /d "%~dp0"

REM ============================================================
REM  Recall AI 错题本 · Windows 一键启动（全自动引导版）
REM  首次运行自动：检查环境 -> 建虚拟环境 -> 装依赖 -> 生成 .env
REM                -> 构建前端（如缺 dist）-> 启动服务 -> 打开浏览器
REM  支持参数：start.bat --check  仅做环境自检，不启动服务
REM ============================================================

set "CHECK="
if /i "%~1"=="--check" set "CHECK=1"

echo ============================================================
echo    Recall AI 错题本 · 一键启动
echo    首次运行会自动配置环境，请耐心等待
echo ============================================================
echo.

REM ---------- 1. 检查 Python ----------
set "PY="
where python >nul 2>&1 && set "PY=python"
if not defined PY where py >nul 2>&1 && set "PY=py -3"
if not defined PY (
  echo [错误] 未检测到 Python，请先安装 Python 3.10+：
  echo         https://www.python.org/downloads/
  echo         安装时务必勾选 "Add Python to PATH"
  pause
  exit /b 1
)
echo [1/5] Python：%PY%

REM ---------- 2. 后端虚拟环境 ----------
cd /d "%~dp0\backend"
if not exist ".venv\Scripts\python.exe" (
  echo [2/5] 首次运行：创建 Python 虚拟环境...
  %PY% -m venv .venv
  if errorlevel 1 (
    echo [错误] 创建虚拟环境失败
    pause
    exit /b 1
  )
) else (
  echo [2/5] 虚拟环境已就绪
)

REM ---------- 3. 安装后端依赖 ----------
".venv\Scripts\python.exe" -c "import fastapi,uvicorn,chromadb,reportlab,httpx" >nul 2>&1
if errorlevel 1 (
  echo [3/5] 首次运行：安装后端依赖（约 2-5 分钟，请勿关闭窗口）...
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络后重试
    pause
    exit /b 1
  )
) else (
  echo [3/5] 后端依赖已就绪
)

REM ---------- 4. 配置文件 ----------
if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo [4/5] 已生成 backend\.env
  echo        用记事本打开填入 DEEPSEEK_API_KEY（不填也能启动，但 AI 功能会提示未配置）
) else (
  echo [4/5] 配置文件已就绪
)
cd /d "%~dp0"

REM ---------- 5. 前端构建 ----------
if not exist "frontend\dist\index.html" (
  echo [5/5] 未找到前端构建产物，准备构建（需要 Node.js 18+）...
  where node >nul 2>&1
  if errorlevel 1 (
    echo [错误] 未检测到 Node.js，无法构建前端。
    echo        方案 A：安装 Node.js https://nodejs.org/ 后重新运行
    echo        方案 B：改用"完整版（含构建产物）"压缩包（已内置 frontend\dist）
    pause
    exit /b 1
  )
  cd /d "%~dp0\frontend"
  echo        安装前端依赖（约 1-3 分钟）...
  call npm install
  if errorlevel 1 (
    echo [错误] 前端依赖安装失败
    pause
    exit /b 1
  )
  echo        构建前端...
  call npm run build
  if errorlevel 1 (
    echo [错误] 前端构建失败
    pause
    exit /b 1
  )
  cd /d "%~dp0"
  echo [5/5] 前端构建完成
) else (
  echo [5/5] 前端构建产物已就绪
)

if defined CHECK (
  echo.
  echo [自检] 环境就绪，未启动服务。
  echo         正常启动请运行 start.bat
  exit /b 0
)

echo.
echo ============================================================
echo    环境就绪，正在启动服务...
echo ============================================================

REM ---------- 端口占用检测 ----------
netstat -ano 2>nul | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
  echo [提示] 检测到 8000 端口已被占用，可能服务已在运行。
  echo        可直接打开 http://localhost:8000/ 查看，或关闭占用程序后重启。
)

REM ---------- 启动后端（新窗口：托管前端页面 + API） ----------
cd /d "%~dp0\backend"
start "Recall Backend" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
cd /d "%~dp0"

REM ---------- 等待并打开浏览器 ----------
echo 等待后端启动...
timeout /t 6 /nobreak >nul
echo [Recall] 打开浏览器：http://localhost:8000/
start "" "http://localhost:8000/"

echo.
echo [Recall] 服务已启动！
echo    - 页面：http://localhost:8000/
echo    - 后端日志：在 "Recall Backend" 窗口查看
echo    - 停止：关闭 "Recall Backend" 窗口
echo.
pause
