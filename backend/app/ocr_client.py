"""PaddleOCR-VL 图片文字识别封装（可选依赖）。"""
import shutil


def ocr_available() -> bool:
    return shutil.which("paddleocr") is not None or _module_available()


def _module_available() -> bool:
    try:
        import paddleocr  # noqa: F401
        return True
    except Exception:
        return False


def ocr_image(image_path: str) -> str:
    """识别图片中的题目文字，返回拼接文本。"""
    if not _module_available():
        raise RuntimeError(
            "未检测到 PaddleOCR-VL。请先安装：pip install paddlepaddle paddleocr。"
        )
    from paddleocr import PaddleOCR

    ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    result = ocr.ocr(image_path, cls=True)
    lines: list[str] = []
    if result and isinstance(result, list):
        for block in result:
            if not block:
                continue
            for line in block:
                if isinstance(line, (list, tuple)) and len(line) >= 2:
                    text = line[1]
                    if isinstance(text, (list, tuple)):
                        text = text[0]
                    if text:
                        lines.append(str(text))
    return "\n".join(lines).strip()
