@echo off
chcp 65001 >nul
REM Recall AI 错题本 · Windows 一键启动
REM 前提：backend/.venv 已创建、依赖已安装、backend/.env 已配置

cd /d "%~dp0"
echo [Recall] 启动后端服务...
cd backend
start "Recall Backend" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
cd ..

timeout /t 4 /nobreak >nul
echo [Recall] 打开浏览器...
start http://localhost:8000/
echo [Recall] 已启动，访问 http://localhost:8000/
pause