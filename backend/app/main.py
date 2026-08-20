"""Recall AI 后端入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
