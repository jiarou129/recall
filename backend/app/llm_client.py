"""DeepSeek 大模型客户端（OpenAI 兼容接口）。"""
import base64

from openai import OpenAI
from app.config import settings

SYSTEM_PROMPT = (
    "你是 Recall AI，一名面向学生的 AI 学习辅导助手。"
    "你的职责是：解答学生关于错题的疑问、讲解知识点、给出解题思路与易错提醒。"
    "请用清晰、鼓励、分步骤的方式回答，避免直接给最终答案而不讲过程。"
    "如有必要，请结合学生提供的错题内容进行分析。"
)

VISION_OCR_PROMPT = (
    "请识别图片中的题目文字。只输出图片里出现的题目、选项、公式和关键数字，"
    "保持原有排版，不要添加解释、总结或与图片无关的内容。"
    "如果图片里没有题目或文字，请直接回复：未检测到题目。"
)

VISION_MODEL = "Qwen/Qwen3-VL-8B-Instruct"


def _client():
    return OpenAI(api_key=settings.deepseek_api_key or "EMPTY", base_url=settings.deepseek_base_url or "https://api.deepseek.com")


def chat(messages: list[dict], model: str | None = None) -> str:
    """messages: [{"role":"user"/"assistant", "content": "..."}]"""
    client = _client()
    full = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    resp = client.chat.completions.create(
        model=model or settings.deepseek_model or "deepseek-chat",
        messages=full,
        temperature=0.7,
        stream=False,
    )
    return resp.choices[0].message.content or ""


SOLVE_PROMPT = (
    "你是 Recall AI，一名耐心的中学/大学数学与理科老师。"
    "请对用户给出的题目做完整解析，输出格式固定为：\n"
    "【思路】用 2-3 句话概括关键考点与切入点；\n"
    "【解答】分步骤给出详细推导，数学公式必须用 LaTeX 定界符包裹：行内公式统一用 $...$，单独成行的公式统一用 $$...$$；\n"
    "【答案】最后给出明确最终答案；\n"
    "【易错提醒】1-2 条常见易错点。\n"
    "注意："
    "1. 不要使用 \\( ... \\) 或 \\[ ... \\] 格式，所有公式统一用 $...$ 或 $$...$$ 包裹；"
    "2. 每个数学表达式、分数（\\frac）、极限（\\lim）、积分（\\int）、上下标、根号等都必须完整包裹在 $...$ 或 $$...$$ 中，不要有任何裸 LaTeX 命令暴露在定界符外；"
    "3. 多行/长公式请用 $$...$$ 独占一行，确保公式内容完整，不要被截断。"
    "不要输出与题目无关的内容。"
)


def solve_question(question: str) -> str:
    """根据题干生成完整解析（思路/解答/答案/易错提醒）。"""
    client = _client()
    resp = client.chat.completions.create(
        model=settings.deepseek_model or "deepseek-chat",
        messages=[
            {"role": "system", "content": SOLVE_PROMPT},
            {"role": "user", "content": f"题目：{question}"},
        ],
        temperature=0.4,
        max_tokens=1536,  # 保证长公式不被截断；前端超时 180s 已留足时间
        stream=False,
    )
    return resp.choices[0].message.content or ""


def vision_ocr(image_path: str) -> str:
    """使用多模态大模型识别图片中的题目文字。"""
    client = _client()
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    url = f"data:image/png;base64,{b64}"
    resp = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": url}},
                    {"type": "text", "text": VISION_OCR_PROMPT},
                ],
            }
        ],
        temperature=0.1,
        max_tokens=1024,
        stream=False,
    )
    return (resp.choices[0].message.content or "").strip()


def is_configured() -> bool:
    return bool(settings.deepseek_api_key)
