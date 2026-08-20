"""模型设置路由。"""
from fastapi import APIRouter, HTTPException

from app.config import settings
from app.database import get_conn
from app.schemas import SettingsOut, SettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["settings"])

# 掩码标记：GET 时返回，前端回填；PUT 时识别以保留原 Key
_MASK = "********"


@router.get("", response_model=SettingsOut)
def get_settings():
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT model_name, api_key, base_url FROM settings WHERE id=1"
        ).fetchone()
        returned_key = _MASK if (row["api_key"] or "").strip() else ""
        return SettingsOut(
            model_name=row["model_name"], api_key=returned_key, base_url=row["base_url"]
        )
    finally:
        conn.close()


@router.put("", response_model=SettingsOut)
def update_settings(payload: SettingsUpdate):
    conn = get_conn()
    try:
        old = conn.execute("SELECT api_key FROM settings WHERE id=1").fetchone()
        old_key = (old["api_key"] or "") if old else ""
        incoming = payload.api_key or ""
        # 包含掩码 -> 保留原 Key；空串 -> 清除 Key；其它 -> 更新 Key
        keep_key = _MASK in incoming
        new_key = old_key if keep_key else incoming
        if keep_key:
            conn.execute(
                "UPDATE settings SET model_name=?, base_url=? WHERE id=1",
                (payload.model_name, payload.base_url),
            )
        else:
            conn.execute(
                "UPDATE settings SET model_name=?, api_key=?, base_url=? WHERE id=1",
                (payload.model_name, incoming, payload.base_url),
            )
        conn.commit()
    finally:
        conn.close()
    # 同步到运行期配置，使 llm_client 立即生效
    settings.deepseek_model = payload.model_name
    settings.deepseek_api_key = new_key
    settings.deepseek_base_url = payload.base_url
    returned_key = _MASK if new_key else ""
    return SettingsOut(
        model_name=payload.model_name, api_key=returned_key, base_url=payload.base_url
    )
