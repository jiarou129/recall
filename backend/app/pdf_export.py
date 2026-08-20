"""使用 ReportLab 将错题导出为 PDF。"""
import io
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def _register_chinese_font() -> str:
    """注册中文字体。

    优先级：项目自带 -> Windows 微软雅黑（支持完整 Unicode，含上标/平方根等数学符号）
    -> Windows 黑体（基础 CJK） -> Linux 常见中文字体。
    .ttc 字体需通过 subfontIndex 指定子字体。
    """
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # (path, subfontIndex or None)
    candidates: list[tuple[str, int | None]] = [
        # 项目自带（部署时推荐把字体放这里）
        (os.path.join(project_dir, "app", "assets", "fonts", "NotoSansCJKsc-Regular.otf"), None),
        (os.path.join(project_dir, "app", "assets", "fonts", "msyh.ttc"), 0),
        # Windows 微软雅黑（Unicode 覆盖最全，含 x²/√ 等数学符号）
        (r"C:\Windows\Fonts\msyh.ttc", 0),
        (r"C:\Windows\Fonts\msyhbd.ttc", 0),
        ("/c/Windows/Fonts/msyh.ttc", 0),
        ("/c/Windows/Fonts/msyhbd.ttc", 0),
        # Windows 黑体（基础 CJK，但数学/上下标字符不全）
        (r"C:\Windows\Fonts\simhei.ttf", None),
        ("/c/Windows/Fonts/simhei.ttf", None),
        # Linux 常见中文字体
        ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 0),
        ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 0),
        ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 0),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", None),
    ]
    for path, sub_idx in candidates:
        if os.path.exists(path):
            try:
                name = f"CNFont-{os.path.basename(path)}-{sub_idx if sub_idx is not None else '0'}"
                kwargs: dict = {"subfontIndex": sub_idx} if sub_idx is not None else {}
                pdfmetrics.registerFont(TTFont(name, path, **kwargs))
                return name
            except Exception:
                continue
    return "Helvetica"


CN_FONT = _register_chinese_font()


def export_mistakes_pdf(mistakes: list[dict]) -> bytes:
    """mistakes: list of dict（与 MistakeOut 字段一致）。返回 PDF 字节。"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title="Recall AI 错题本",
    )
    styles = getSampleStyleSheet()
    h_style = ParagraphStyle(
        "H", parent=styles["Heading2"], fontName=CN_FONT,
        textColor=colors.HexColor("#007AFF")
    )
    h3_style = ParagraphStyle(
        "H3", parent=styles["Heading3"], fontName=CN_FONT
    )
    q_style = ParagraphStyle(
        "Q", parent=styles["Normal"], fontName=CN_FONT,
        fontSize=11, leading=16
    )
    a_style = ParagraphStyle(
        "A", parent=styles["Normal"], fontName=CN_FONT,
        fontSize=10, leading=15, textColor=colors.HexColor("#10B981")
    )
    meta_style = ParagraphStyle(
        "M", parent=styles["Normal"], fontName=CN_FONT,
        fontSize=9, textColor=colors.HexColor("#6E6E73")
    )

    story = [Paragraph("Recall AI · 智能错题本", h_style), Spacer(1, 8 * mm)]

    for idx, m in enumerate(mistakes, 1):
        story.append(Paragraph(f"错题 {idx} · {_esc(m.get('subject')) or '未分类'}", h3_style))
        story.append(Paragraph(f"<b>题目：</b>{_esc(m.get('question', ''))}", q_style))
        story.append(Paragraph(f"<b>解析：</b>{_esc(m.get('answer', ''))}", a_style))
        meta = f"来源：{_esc(m.get('source')) or '—'}　|　知识点：{_esc(m.get('knowledge_point')) or '—'}　|　复习次数：{m.get('review_count', 0)}"
        story.append(Paragraph(meta, meta_style))
        story.append(Spacer(1, 6 * mm))

    doc.build(story)
    return buffer.getvalue()


def _esc(text: str | None) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
