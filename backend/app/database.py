"""SQLite 连接与初始化（使用标准库 sqlite3，零额外依赖）。"""
import os
import sqlite3
from pathlib import Path

from app.config import settings


def _db_path() -> str:
    path = settings.sqlite_path
    parent = Path(path).parent
    parent.mkdir(parents=True, exist_ok=True)
    return path


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    """对已存在的表追加新列（不破坏已有数据）。"""
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(mistakes)").fetchall()]
    if "snooze_until" not in cols:
        conn.execute("ALTER TABLE mistakes ADD COLUMN snooze_until TEXT NOT NULL DEFAULT ''")
        conn.commit()


def init_db() -> None:
    conn = get_conn()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                color INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS mistakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL DEFAULT '',
                source TEXT NOT NULL DEFAULT '',
                subject TEXT NOT NULL DEFAULT '',
                knowledge_point TEXT NOT NULL DEFAULT '',
                review_count INTEGER NOT NULL DEFAULT 0,
                mastery TEXT NOT NULL DEFAULT 'unmastered',
                snooze_until TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL DEFAULT '新对话',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                model_name TEXT NOT NULL DEFAULT 'deepseek-chat',
                api_key TEXT NOT NULL DEFAULT '',
                base_url TEXT NOT NULL DEFAULT 'https://api.deepseek.com'
            );
            """
        )
        _migrate(conn)
        conn.commit()
    finally:
        conn.close()


def seed_if_empty() -> None:
    """首次启动写入默认分类与设置。"""
    from datetime import datetime

    now = datetime.now().isoformat(timespec="seconds")
    conn = get_conn()
    try:
        cur = conn.execute("SELECT COUNT(*) AS c FROM categories")
        if cur.fetchone()["c"] == 0:
            defaults = [("数学", 1), ("英语", 2), ("物理", 4), ("化学", 6), ("其他", 8)]
            conn.executemany(
                "INSERT INTO categories (name, color) VALUES (?, ?)", defaults
            )
        cur = conn.execute("SELECT COUNT(*) AS c FROM settings")
        if cur.fetchone()["c"] == 0:
            conn.execute(
                "INSERT INTO settings (id, model_name, api_key, base_url) VALUES (1, ?, ?, ?)",
                (settings.deepseek_model, settings.deepseek_api_key, settings.deepseek_base_url),
            )
        conn.commit()
    finally:
        conn.close()
