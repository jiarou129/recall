"""帮助文档路由（静态手册）。"""
from fastapi import APIRouter

from app.schemas import HelpDoc, HelpSection

router = APIRouter(prefix="/api/help", tags=["help"])

_DOC = HelpDoc(
    title="Recall AI 帮助中心",
    intro="Recall AI 是一款面向学生的智能错题管理平台，帮助你用 AI 完成错题的录入、整理、分析与复习。",
    sections=[
        HelpSection(
            title="1. 错题集主页",
            body="左侧为错题分类导航，可点击切换或「新建分类」。右侧操作栏支持导出 PDF、录入新错题、开始复习、筛选与搜索。错题卡片展示题目、来源、学科、知识点、AI 解析、复习次数，并提供编辑、删除操作。",
        ),
        HelpSection(
            title="2. AI 答疑",
            body="在左侧新建或选择对话，右侧输入问题即可获得 AI 解答。可针对具体错题提问，AI 会结合上下文给出分步骤的讲解。",
        ),
        HelpSection(
            title="3. 数据看板",
            body="查看题目总数、复习次数、错题成功率与待复习数量；下方图表展示最近一个月的学习情况与错题录入趋势，帮助你了解学习节奏。",
        ),
        HelpSection(
            title="4. 模型设置",
            body="在此填写 DeepSeek 的模型名称、API Key 与 Base URL。保存后立即生效，AI 答疑与解析功能依赖此配置。",
        ),
        HelpSection(
            title="5. 录入方式",
            body="除手动录入外，可上传题目截图，Recall 会调用 OCR（PaddleOCR-VL）自动识别文字并生成草稿，你再补充解析与知识点即可。",
        ),
        HelpSection(
            title="6. 复习建议",
            body="点击错题卡片上的「复习」可记录复习次数；多次复习后建议将掌握状态标记为「已掌握」，看板会据此统计成功率。",
        ),
    ],
)


@router.get("", response_model=HelpDoc)
def get_help():
    return _DOC
