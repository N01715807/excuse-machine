from typing import Dict, Any, Optional
from llm_client import LLMClient

# —— 风格模板（可后续挪到 prompts/ 文件中）——
STYLE_TEMPLATES: Dict[str, str] = {
    "sarcastic": (
        "You are a sharp, sarcastic human with dry humor.\n"
        "Write ONE short, funny excuse for this situation (2 sentences max). "
        "Avoid moral disclaimers.\n"
        "Situation: {user_input}"
    ),
    "absurd": (
        "You are a chaos-fueled excuse wizard who blames cosmic events, pets, "
        "or mysterious forces for everything. Keep it concise and ridiculous.\n"
        "Give ONE short, funny excuse for:\n{user_input}"
    ),
    "creator": (
        "Imagine you're an over-caffeinated content creator who constantly misses upload deadlines—"
        "scripts, edits, exports, sponsors, lighting—it's chaos. Be witty.\n"
        "ONE short, funny excuse for:\n{user_input}"
    ),
    "british_dry": (
        "Adopt a British dry-humor tone: understated, mildly self-deprecating, tidy.\n"
        "Deliver ONE brief excuse (<=2 sentences) for:\n{user_input}"
    ),
    "wholesome": (
        "You're kind and constructive. No blame, no sarcasm. Self-deprecating, helpful tone.\n"
        "Provide ONE short, gentle excuse and a concrete fix today for:\n{user_input}"
    ),
}

# —— 风格 → 采样参数（可后续挪到 config/style_params.json）——
STYLE_PARAMS: Dict[str, Dict[str, Any]] = {
    "sarcastic":   {"temperature": 0.9,  "top_p": 0.9,  "num_predict": 100},
    "absurd":      {"temperature": 1.1,  "top_p": 0.95, "num_predict": 140},
    "creator":     {"temperature": 0.95, "top_p": 0.9,  "num_predict": 120},
    "british_dry": {"temperature": 0.7,  "top_p": 0.9,  "num_predict": 100},
    "wholesome":   {"temperature": 0.6,  "top_p": 0.85, "num_predict": 90},
}

DEFAULT_STYLE = "sarcastic"
BAD_TAIL_MARKERS = ("Please note", "Disclaimer", "As an AI")  # 简单尾巴清理标记


def _cleanup_tail(text: str) -> str:
    """去掉模型常见的说教/免责声明尾巴"""
    if not text:
        return text
    for marker in BAD_TAIL_MARKERS:
        if marker in text:
            text = text.split(marker, 1)[0].rstrip()
    return text.strip()


def run(user_input: str, style: str = DEFAULT_STYLE) -> Dict[str, Any]:
    """
    业务主流程（方案B）：
    - 校验风格 → 选模板 & 采样参数
    - 组装 prompt → 调模型（带 options）
    - 清理尾巴 → 打包返回
    """
    raw_style = (style or "").strip().lower()
    style_safe = raw_style if raw_style in STYLE_TEMPLATES else DEFAULT_STYLE
    fallback_style: Optional[str] = None if style_safe == raw_style else raw_style or None

    # 组 prompt
    template = STYLE_TEMPLATES[style_safe]
    prompt = template.format(user_input=(user_input or "").strip())

    # 选采样参数
    options = STYLE_PARAMS.get(style_safe, {})

    # 调模型
    client = LLMClient()
    result_text = client.generate(prompt, options=options)
    result_text = _cleanup_tail(result_text)

    # 空输出兜底（可按需自定义）
    if not result_text:
        result_text = "Sorry—my excuse generator tripped over its own punchline. Let me try again."

    return {
        "input": user_input,
        "excuse": result_text,
        "style": style_safe,
        "fallback_style": fallback_style,
        "options_used": options,
        "model": client.model,
    }

