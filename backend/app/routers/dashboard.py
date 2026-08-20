"""数据看板统计路由。"""
from datetime import datetime, timedelta

from fastapi import APIRouter

from app.database import get_conn
from app.schemas import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def stats():
    conn = get_conn()
    try:
        total = conn.execute("SELECT COUNT(*) AS c FROM mistakes").fetchone()["c"]
        reviews = conn.execute("SELECT COALESCE(SUM(review_count),0) AS s FROM mistakes").fetchone()["s"]
        pending = conn.execute(
            "SELECT COUNT(*) AS c FROM mistakes WHERE mastery != 'mastered'"
        ).fetchone()["c"]
        mastered = conn.execute(
            "SELECT COUNT(*) AS c FROM mistakes WHERE mastery = 'mastered'"
        ).fetchone()["c"]
        success_rate = round(mastered / total * 100, 1) if total else 0.0

        # 最近 30 天（含今天）
        today = datetime.now().date()
        study_series, entry_series = [], []
        for i in range(29, -1, -1):
            d = today - timedelta(days=i)
            ds = d.isoformat()
            rc = conn.execute(
                "SELECT COALESCE(SUM(review_count),0) AS s FROM mistakes WHERE DATE(updated_at)=?",
                (ds,),
            ).fetchone()["s"]
            ec = conn.execute(
                "SELECT COUNT(*) AS c FROM mistakes WHERE DATE(created_at)=?", (ds,)
            ).fetchone()["c"]
            study_series.append({"date": ds, "count": rc})
            entry_series.append({"date": ds, "count": ec})

        by_subject = [
            {"subject": r["subject"] or "未分类", "count": r["c"]}
            for r in conn.execute(
                "SELECT subject, COUNT(*) AS c FROM mistakes GROUP BY subject ORDER BY c DESC"
            ).fetchall()
        ]
        return DashboardStats(
            total_questions=total,
            total_reviews=reviews,
            success_rate=success_rate,
            pending_review=pending,
            study_series=study_series,
            entry_series=entry_series,
            by_subject=by_subject,
        )
    finally:
        conn.close()
