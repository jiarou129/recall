"""错题与分类路由。"""
import random
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.database import get_conn
from app.schemas import (
    CategoryCreate,
    CategoryOut,
    MistakeCreate,
    MistakeOut,
    MistakeUpdate,
)
from app import chroma_client
from app import pdf_export

router = APIRouter(prefix="/api/mistakes", tags=["mistakes"])


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _row_to_out(row) -> dict:
    return {
        "id": row["id"],
        "category_id": row["category_id"],
        "category_name": row["category_name"],
        "category_color": row["category_color"] or 1,
        "question": row["question"],
        "answer": row["answer"],
        "source": row["source"],
        "subject": row["subject"],
        "knowledge_point": row["knowledge_point"],
        "review_count": row["review_count"],
        "mastery": row["mastery"],
        "snooze_until": row["snooze_until"] or "",
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


_MISTAKE_SELECT = """
    SELECT m.*, c.name AS category_name, c.color AS category_color
    FROM mistakes m
    LEFT JOIN categories c ON m.category_id = c.id
"""


# ---------------- 分类 ----------------
@router.get("/categories", response_model=list[CategoryOut])
def list_categories():
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT c.*, (SELECT COUNT(*) FROM mistakes m WHERE m.category_id=c.id) AS count "
            "FROM categories c ORDER BY c.id"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate):
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO categories (name, color) VALUES (?, ?)",
            (payload.name, payload.color),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM categories WHERE id=?", (cur.lastrowid,)).fetchone()
        return dict(row, count=0)
    finally:
        conn.close()


@router.put("/categories/{cid}", response_model=CategoryOut)
def update_category(cid: int, payload: CategoryCreate):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE categories SET name=?, color=? WHERE id=?",
            (payload.name, payload.color, cid),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM categories WHERE id=?", (cid,)).fetchone()
        if not row:
            raise HTTPException(404, "分类不存在")
        count = conn.execute("SELECT COUNT(*) AS c FROM mistakes WHERE category_id=?", (cid,)).fetchone()["c"]
        return dict(row, count=count)
    finally:
        conn.close()


@router.delete("/categories/{cid}", status_code=204)
def delete_category(cid: int):
    conn = get_conn()
    try:
        row = conn.execute("SELECT id FROM categories WHERE id=?", (cid,)).fetchone()
        if not row:
            raise HTTPException(404, "分类不存在")
        conn.execute("DELETE FROM categories WHERE id=?", (cid,))
        conn.commit()
    finally:
        conn.close()


# ---------------- 错题 ----------------
@router.get("", response_model=list[MistakeOut])
def list_mistakes(
    category_id: Optional[int] = None,
    subject: Optional[str] = None,
    status: Optional[str] = None,
    q: Optional[str] = None,
):
    sql = [_MISTAKE_SELECT]
    wheres, params = [], []
    if category_id is not None:
        wheres.append("m.category_id = ?")
        params.append(category_id)
    if subject:
        wheres.append("m.subject = ?")
        params.append(subject)
    if status:
        wheres.append("m.mastery = ?")
        params.append(status)
    if q:
        wheres.append("(m.question LIKE ? OR m.answer LIKE ? OR m.knowledge_point LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
    if wheres:
        sql.append("WHERE " + " AND ".join(wheres))
    sql.append("ORDER BY m.updated_at DESC")
    conn = get_conn()
    try:
        rows = conn.execute(" ".join(sql), params).fetchall()
        return [_row_to_out(r) for r in rows]
    finally:
        conn.close()


@router.post("", response_model=MistakeOut, status_code=201)
def create_mistake(payload: MistakeCreate):
    now = _now()
    conn = get_conn()
    try:
        cur = conn.execute(
            """INSERT INTO mistakes
               (category_id, question, answer, source, subject, knowledge_point, review_count, mastery, snooze_until, created_at, updated_at)
               VALUES (?,?,?,?,?,?,0,?,'',?,?)""",
            (payload.category_id, payload.question, payload.answer, payload.source,
             payload.subject, payload.knowledge_point, payload.mastery, now, now),
        )
        mid = cur.lastrowid
        conn.commit()
        row = conn.execute(_MISTAKE_SELECT + " WHERE m.id=?", (mid,)).fetchone()
        out = _row_to_out(row)
    finally:
        conn.close()
    # 写入向量库
    chroma_client.upsert_mistake(mid, f"{payload.question}\n{payload.answer}", {
        "subject": payload.subject, "knowledge_point": payload.knowledge_point})
    return out


# ---------------- 导出 PDF ----------------
@router.get("/export")
def export_pdf(ids: Optional[str] = Query(None)):
    conn = get_conn()
    try:
        if ids:
            id_list = [int(x) for x in ids.split(",") if x.strip().isdigit()]
            placeholders = ",".join("?" * len(id_list))
            rows = conn.execute(_MISTAKE_SELECT + f" WHERE m.id IN ({placeholders})", id_list).fetchall()
        else:
            rows = conn.execute(_MISTAKE_SELECT + " ORDER BY m.updated_at DESC").fetchall()
        data = [_row_to_out(r) for r in rows]
    finally:
        conn.close()
    pdf_bytes = pdf_export.export_mistakes_pdf(data)
    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=recall-mistakes.pdf"},
    )


@router.get("/{mid}", response_model=MistakeOut)
def get_mistake(mid: int):
    conn = get_conn()
    try:
        row = conn.execute(_MISTAKE_SELECT + " WHERE m.id=?", (mid,)).fetchone()
        if not row:
            raise HTTPException(404, "错题不存在")
        return _row_to_out(row)
    finally:
        conn.close()


@router.put("/{mid}", response_model=MistakeOut)
def update_mistake(mid: int, payload: MistakeUpdate):
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM mistakes WHERE id=?", (mid,)).fetchone()
        if not row:
            raise HTTPException(404, "错题不存在")
        data = dict(row)
        for k, v in payload.model_dump(exclude_unset=True).items():
            if v is not None:
                data[k] = v
        conn.execute(
            """UPDATE mistakes SET category_id=?, question=?, answer=?, source=?, subject=?,
               knowledge_point=?, mastery=?, snooze_until=?, updated_at=? WHERE id=?""",
            (data["category_id"], data["question"], data["answer"], data["source"],
             data["subject"], data["knowledge_point"], data["mastery"], data.get("snooze_until", row["snooze_until"] or ""), _now(), mid),
        )
        conn.commit()
        new_row = conn.execute(_MISTAKE_SELECT + " WHERE m.id=?", (mid,)).fetchone()
        out = _row_to_out(new_row)
    finally:
        conn.close()
    chroma_client.upsert_mistake(mid, f"{out['question']}\n{out['answer']}",
                                 {"subject": out["subject"], "knowledge_point": out["knowledge_point"]})
    return out


@router.delete("/{mid}", status_code=204)
def delete_mistake(mid: int):
    conn = get_conn()
    try:
        row = conn.execute("SELECT id FROM mistakes WHERE id=?", (mid,)).fetchone()
        if not row:
            raise HTTPException(404, "错题不存在")
        conn.execute("DELETE FROM mistakes WHERE id=?", (mid,))
        conn.commit()
    finally:
        conn.close()
    chroma_client.delete_mistake(mid)


@router.post("/{mid}/review", response_model=MistakeOut)
def review_mistake(mid: int):
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM mistakes WHERE id=?", (mid,)).fetchone()
        if not row:
            raise HTTPException(404, "错题不存在")
        new_count = row["review_count"] + 1
        # 复习过一次即进入「复习中」
        mastery = "reviewing" if row["mastery"] == "unmastered" else row["mastery"]
        conn.execute(
            "UPDATE mistakes SET review_count=?, mastery=?, updated_at=? WHERE id=?",
            (new_count, mastery, _now(), mid),
        )
        conn.commit()
        new_row = conn.execute(_MISTAKE_SELECT + " WHERE m.id=?", (mid,)).fetchone()
        out = _row_to_out(new_row)
    finally:
        conn.close()
    return out


class SnoozeBody(BaseModel):
    days: Optional[int] = None  # 不传则后端随机 5-7 天


@router.post("/{mid}/snooze", response_model=MistakeOut)
def snooze_mistake(mid: int, body: Optional[SnoozeBody] = None):
    days = body.days if body and body.days else random.randint(5, 7)
    until = (datetime.now() + timedelta(days=days)).isoformat(timespec="seconds")
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM mistakes WHERE id=?", (mid,)).fetchone()
        if not row:
            raise HTTPException(404, "错题不存在")
        conn.execute(
            "UPDATE mistakes SET snooze_until=?, updated_at=? WHERE id=?",
            (until, _now(), mid),
        )
        conn.commit()
        new_row = conn.execute(_MISTAKE_SELECT + " WHERE m.id=?", (mid,)).fetchone()
        out = _row_to_out(new_row)
    finally:
        conn.close()
    return out


# ---------------- 语义检索 ----------------
class SemanticQuery(BaseModel):
    q: str
    n: int = 5


@router.post("/semantic", response_model=list[MistakeOut])
def semantic_search(body: SemanticQuery):
    ids = chroma_client.query_similar(body.q, body.n)
    if not ids:
        return []
    conn = get_conn()
    try:
        placeholders = ",".join("?" * len(ids))
        rows = conn.execute(
            _MISTAKE_SELECT + f" WHERE m.id IN ({placeholders})", ids
        ).fetchall()
        out_map = {r["id"]: _row_to_out(r) for r in rows}
        return [out_map[i] for i in ids if i in out_map]
    finally:
        conn.close()
