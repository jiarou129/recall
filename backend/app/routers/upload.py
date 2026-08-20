"""图片上传与 OCR 识别路由（优先 AI 视觉识别，可降级到 PaddleOCR-VL）。"""
import tempfile
import os

from fastapi import APIRouter, File, UploadFile

from app import llm_client, ocr_client

router = APIRouter(prefix="/api/upload", tags=["upload"])


def _clean_ocr(text: str) -> str:
    # 过滤纯提示性垃圾，保留用户可能输入的内容
    t = text.strip()
    noise = [
        "未安装 PaddleOCR-VL",
        "localhost:",
        "请执行 pip install",
        "无法识别",
    ]
    if any(n in t for n in noise) and len(t) < 80:
        return ""
    return t


@router.post("/ocr")
async def upload_ocr(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "img.jpg")[1] or ".jpg"
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)
    try:
        content = await file.read()
        with os.fdopen(fd, "wb") as f:
            f.write(content)

        # 优先使用 AI 视觉识别（无需本地 Paddle 依赖）
        if llm_client.is_configured():
            try:
                text = llm_client.vision_ocr(tmp_path)
                text = _clean_ocr(text)
                if text:
                    return {"available": True, "text": text, "message": "AI 识别完成"}
                return {
                    "available": False,
                    "text": "",
                    "message": "未检测到题目，请上传包含题目的截图。",
                }
            except Exception as e:
                # AI 识别失败时，若本地 Paddle 可用则降级
                if ocr_client.ocr_available():
                    text = ocr_client.ocr_image(tmp_path)
                    return {"available": True, "text": text, "message": "本地 OCR 识别完成"}
                return {"available": False, "text": "", "message": f"AI 识别失败：{e}"}

        # 无 AI 配置时，回退到本地 PaddleOCR-VL
        if ocr_client.ocr_available():
            text = ocr_client.ocr_image(tmp_path)
            return {"available": True, "text": text, "message": "本地 OCR 识别完成"}

        return {
            "available": False,
            "text": "",
            "message": "未配置 AI 模型，且未安装 PaddleOCR-VL。请先在「设置」页配置 SiliconFlow / DeepSeek API Key，或执行 pip install paddlepaddle paddleocr 后重试。",
        }
    except RuntimeError as e:
        return {"available": False, "text": "", "message": str(e)}
    except Exception as e:
        return {"available": False, "text": "", "message": f"OCR 失败：{e}"}
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
