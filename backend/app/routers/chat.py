"""AI 答疑（对话）路由，调用 DeepSeek。"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.database import get_conn
from app.schemas import ChatMessageOut, ChatSessionOut, ChatSend
from app import llm_client

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


@router.get("/sessions", response_model=list[ChatSessionOut])
def list_sessions():
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM chat_sessions ORDER BY updated_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.post("/sessions", response_model=ChatSessionOut, status_code=201)
def create_session(title: str = "新对话"):
    now = _now()
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO chat_sessions (title, created_at, updated_at) VALUES (?,?,?)",
            (title, now, now),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM chat_sessions WHERE id=?", (cur.lastrowid,)).fetchone()
        return dict(row)
    finally:
        conn.close()


@router.get("/sessions/{sid}/messages", response_model=list[ChatMessageOut])
def list_messages(sid: int):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM chat_messages WHERE session_id=? ORDER BY id ASC", (sid,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.post("/sessions/{sid}/messages", response_model=list[ChatMessageOut])
def send_message(sid: int, payload: ChatSend):
    if not payload.content.strip():
        raise HTTPException(400, "消息内容不能为空")
    now = _now()
    conn = get_conn()
    try:
        # 校验会话存在
        sess = conn.execute("SELECT * FROM chat_sessions WHERE id=?", (sid,)).fetchone()
        if not sess:
            raise HTTPException(404, "会话不存在")
        # 保存用户消息
        conn.execute(
            "INSERT INTO chat_messages (session_id, role, content, created_at) VALUES (?,?,?,?)",
            (sid, "user", payload.content, now),
        )
        # 拉取历史构建上下文
        hist = conn.execute(
            "SELECT role, content FROM chat_messages WHERE session_id=? ORDER BY id ASC", (sid,)
        ).fetchall()
        # 过滤系统错误/降级占位回复（以"（"开头），避免失败文本污染上下文导致后续请求持续异常
        messages = [
            {"role": r["role"], "content": r["content"]}
            for r in hist
            if not (r["role"] == "assistant" and r["content"].startswith("（"))
        ]

        # 调用大模型（未配置 key 时返回友好占位）
        if not llm_client.is_configured():
            reply = (
                "（当前未配置大模型 API Key，请在「模型设置」页填入 DeepSeek API Key 后即可获得真实回答。）\n\n"
                "这是一条演示回复：" + payload.content
            )
        else:
            try:
                reply = llm_client.chat(messages)
            except Exception as e:
                reply = f"（调用大模型失败：{e}）"

        conn.execute(
            "INSERT INTO chat_messages (session_id, role, content, created_at) VALUES (?,?,?,?)",
            (sid, "assistant", reply, _now()),
        )
        # 更新会话标题（首条）与更新时间
        if sess["title"] == "新对话":
            title = payload.content[:20]
            conn.execute("UPDATE chat_sessions SET title=?, updated_at=? WHERE id=?",
                         (title, _now(), sid))
        else:
            conn.execute("UPDATE chat_sessions SET updated_at=? WHERE id=?", (_now(), sid))
        conn.commit()
        rows = conn.execute(
            "SELECT * FROM chat_messages WHERE session_id=? ORDER BY id ASC", (sid,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.delete("/sessions/{sid}", status_code=204)
def delete_session(sid: int):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM chat_sessions WHERE id=?", (sid,))
        conn.commit()
    finally:
        conn.close()


class SolveRequest(BaseModel):
    question: str


class SolveResponse(BaseModel):
    answer: str
    available: bool


@router.post("/solve", response_model=SolveResponse)
def solve_question(payload: SolveRequest):
    """根据题干生成 AI 解析（供 OCR 识别后一键填入「解析」栏）。"""
    q = payload.question.strip()
    if not q:
        raise HTTPException(400, "题目内容不能为空")
    if not llm_client.is_configured():
        return SolveResponse(available=False, answer="")
    try:
        answer = llm_client.solve_question(q)
    except Exception as e:
        return SolveResponse(available=False, answer=f"（AI 解析失败：{e}）")
    return SolveResponse(available=True, answer=answer)
