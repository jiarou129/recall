"""Recall AI 后端入口。"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import init_db, seed_if_empty
from app.routers import mistakes, chat, dashboard, settings, upload, help as help_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_if_empty()
    yield


app = FastAPI(title="Recall AI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mistakes.router)
app.include_router(chat.router)
app.include_router(dashboard.router)
app.include_router(settings.router)
app.include_router(upload.router)
app.include_router(help_router.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "product": "Recall AI"}


# 生产/打包模式：如果 frontend/dist 存在，则由后端直接托管静态资源
# 这样解压后只启动后端，访问 http://localhost:8000/ 即可看到页面
_DIST_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
)
if os.path.isdir(_DIST_DIR):

    @app.exception_handler(StarletteHTTPException)
    async def _spa_fallback_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404 and not request.url.path.startswith("/api/"):
            index_path = os.path.join(_DIST_DIR, "index.html")
            if os.path.exists(index_path):
                return FileResponse(index_path)
        raise exc

    app.mount("/", StaticFiles(directory=_DIST_DIR, html=True), name="static")
