"""将错题导出为 PDF。

主方案：生成带 KaTeX 的 HTML，调用系统 Edge/Chrome 无头打印为 PDF。
Fallback：浏览器不可用时退回 reportlab 纯文本导出（公式显示源码，保证可用性）。
"""
import html
import io
import logging
import os
import pathlib
import shutil
import subprocess
import tempfile

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)


def _register_chinese_font() -> str:
    """注册中文字体。

    优先级：项目自带 -> Windows 微软雅黑（支持完整 Unicode，含上标/平方根等数学符号）
    -> Windows 黑体（基础 CJK） -> Linux 常见中文字体。
    .ttc 字体需通过 subfontIndex 指定子字体。
    """
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates: list[tuple[str, int | None]] = [
        (os.path.join(project_dir, "app", "assets", "fonts", "NotoSansCJKsc-Regular.otf"), None),
        (os.path.join(project_dir, "app", "assets", "fonts", "msyh.ttc"), 0),
        (r"C:\Windows\Fonts\msyh.ttc", 0),
        (r"C:\Windows\Fonts\msyhbd.ttc", 0),
        ("/c/Windows/Fonts/msyh.ttc", 0),
        ("/c/Windows/Fonts/msyhbd.ttc", 0),
        (r"C:\Windows\Fonts\simhei.ttf", None),
        ("/c/Windows/Fonts/simhei.ttf", None),
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


def _find_browser() -> str | None:
    """探测可用的 Chromium 内核浏览器（Edge/Chrome），用于 headless PDF 打印。

    同时覆盖 Windows（本机）与 Linux（云端 Docker：apt 安装 chromium）路径。
    """
    candidates = [
        # Windows
        r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",
        r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe",
        r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
        r"%LocalAppData%\Google\Chrome\Application\chrome.exe",
        # Linux（Debian/Ubuntu 的 chromium 包）
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/opt/google/chrome/chrome",
    ]
    for pattern in candidates:
        path = os.path.expandvars(pattern)
        if os.path.exists(path):
            return path
    return None


def _katex_base_uri() -> str:
    """优先使用前端 node_modules 里的 KaTeX；找不到则回退 CDN。"""
    local_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "..", "frontend", "node_modules", "katex", "dist"
        )
    )
    if os.path.exists(os.path.join(local_dir, "katex.min.css")):
        return pathlib.Path(local_dir).as_uri()
    logger.warning("本地 KaTeX 未找到，PDF 公式渲染将使用 CDN（离线环境可能失败）")
    return "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist"


def _text_to_html_paragraphs(text: str | None) -> str:
    """把纯文本按行拆成 <p>，并对特殊字符做 HTML 转义。"""
    if not text:
        return "<p>（无）</p>"
    lines = text.splitlines()
    parts: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            parts.append('<p style="margin:4px 0;">&nbsp;</p>')
        else:
            parts.append(f"<p>{html.escape(stripped)}</p>")
    return "\n".join(parts)


def _build_html(mistakes: list[dict]) -> str:
    """生成包含 KaTeX auto-render 的 HTML。"""
    katex_uri = _katex_base_uri()
    sections: list[str] = []
    for idx, m in enumerate(mistakes, 1):
        subject = html.escape(m.get("subject") or "未分类")
        source = html.escape(m.get("source") or "—")
        kp = html.escape(m.get("knowledge_point") or "—")
        review_count = m.get("review_count", 0)
        sections.append(
            f"""
            <section class="mistake">
                <h2>错题 {idx} · {subject}</h2>
                <div class="question"><h3>题目</h3>{_text_to_html_paragraphs(m.get("question"))}</div>
                <div class="answer"><h3>解析</h3>{_text_to_html_paragraphs(m.get("answer"))}</div>
                <div class="meta">来源：{source}　|　知识点：{kp}　|　复习次数：{review_count}</div>
            </section>
            """
        )

    mistakes_html = "\n".join(sections)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>Recall AI · 智能错题本</title>
<link rel="stylesheet" href="{katex_uri}/katex.min.css">
<style>
  @page {{ size: A4; margin: 18mm; }}
  body {{
    font-family: "Microsoft YaHei", "PingFang SC", -apple-system, sans-serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #1D1D1F;
    padding: 0;
    margin: 0;
  }}
  h1 {{
    font-size: 18pt;
    color: #007AFF;
    margin: 0 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #E5E5EA;
  }}
  h2 {{
    font-size: 13pt;
    color: #007AFF;
    margin: 18px 0 8px 0;
  }}
  h3 {{
    font-size: 10pt;
    color: #6E6E73;
    margin: 10px 0 4px 0;
    font-weight: 600;
  }}
  .mistake {{
    page-break-inside: avoid;
    margin-bottom: 12px;
  }}
  .question p, .answer p {{
    margin: 4px 0;
    text-align: justify;
  }}
  .answer {{
    color: #10B981;
  }}
  .meta {{
    font-size: 9pt;
    color: #6E6E73;
    margin-top: 6px;
  }}
  .katex {{
    font-size: 1.05em;
  }}
</style>
</head>
<body>
<h1>Recall AI · 智能错题本</h1>
{mistakes_html}
<script src="{katex_uri}/katex.min.js"></script>
<script src="{katex_uri}/contrib/auto-render.min.js"></script>
<script>
  document.addEventListener("DOMContentLoaded", function() {{
    renderMathInElement(document.body, {{
      delimiters: [
        {{left: "$$", right: "$$", display: true}},
        {{left: "$", right: "$", display: false}},
        {{left: "\\[", right: "\\]", display: true}},
        {{left: "\\(", right: "\\)", display: false}}
      ],
      throwOnError: false
    }});
  }});
</script>
</body>
</html>"""


def _export_with_browser(browser_path: str, mistakes: list[dict]) -> bytes:
    """用浏览器 headless 打印生成 PDF。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        html_path = os.path.join(tmpdir, "export.html")
        pdf_path = os.path.join(tmpdir, "export.pdf")
        html_content = _build_html(mistakes)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        cmd = [
            browser_path,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=5000",
            f"--print-to-pdf={pdf_path}",
            pathlib.Path(html_path).as_uri(),
        ]
        logger.info("调用浏览器生成 PDF: %s", browser_path)
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=45)

        if not os.path.exists(pdf_path):
            raise RuntimeError("浏览器未生成 PDF 文件")
        with open(pdf_path, "rb") as f:
            return f.read()


def _export_with_reportlab(mistakes: list[dict]) -> bytes:
    """浏览器不可用时回退到 reportlab 文本导出。"""
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


def export_mistakes_pdf(mistakes: list[dict]) -> bytes:
    """mistakes: list of dict（与 MistakeOut 字段一致）。返回 PDF 字节。"""
    browser = _find_browser()
    if browser:
        try:
            return _export_with_browser(browser, mistakes)
        except Exception as e:
            logger.warning("浏览器 PDF 生成失败，回退到 reportlab: %s", e)
    else:
        logger.warning("未找到 Edge/Chrome，PDF 将不包含公式渲染")
    return _export_with_reportlab(mistakes)


def _esc(text: str | None) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
