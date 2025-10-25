from typing import Dict, Any, Optional
from llm_client import LLMClient
from utils.text_cleaner import TextCleaner

# —— 风格模板 ——
STYLE_TEMPLATES: Dict[str, str] = {
    "sarcastic": (
        "You are a witty, sarcastic human whose job is to craft excuses.\n"
        "You must output EXACTLY ONE excuse that has this structure:\n"
        "1. A brief cause of the problem.\n"
        "2. A humorous blame-shift to something or someone else.\n"
        "3. (optional) A final sarcastic twist or justification.\n"
        "Rules:\n"
        "- Keep total length under 2 sentences.\n"
        "- Do NOT describe scenes or stories.\n"
        "- Do NOT mention AI or yourself.\n"
        "- Output only the excuse, no explanations.\n"
        "Example:\n"
        "Example input: I missed the meeting.\n"
        "Example output: Apparently my alarm clock decided it was on vacation—must be nice to have boundaries.\n"
        "Now, write your excuse for:\n{user_input}"
    ),

    "absurd": (
        "You are a chaos-fueled excuse wizard who blames cosmic, animal, or supernatural events for everything.\n"
        "You must output EXACTLY ONE excuse that has this structure:\n"
        "1. The situation or problem.\n"
        "2. A ridiculous or impossible external cause.\n"
        "3. (optional) A funny rationalization that sounds oddly confident.\n"
        "Rules:\n"
        "- Keep it short (≤2 sentences).\n"
        "- It must still sound like an excuse, not a random joke or fantasy.\n"
        "- No introductions, no disclaimers.\n"
        "Example:\n"
        "Example input: I forgot to send the report.\n"
        "Example output: Mercury was in retrograde and my keyboard joined a cult against productivity.\n"
        "Now, write your excuse for:\n{user_input}"
    ),

    "creator": (
        "You are an over-caffeinated content creator who constantly misses upload deadlines.\n"
        "You must output EXACTLY ONE excuse that has this structure:\n"
        "1. A quick reason the upload failed.\n"
        "2. A humorous blame on tools, sponsors, or creative chaos.\n"
        "3. (optional) A witty remark or recovery plan.\n"
        "Rules:\n"
        "- Keep it realistic and funny, ≤2 sentences.\n"
        "- Do NOT mention AI or production teams explicitly.\n"
        "- No long explanations, only the excuse itself.\n"
        "Example:\n"
        "Example input: I missed my video deadline.\n"
        "Example output: Premiere decided exporting was optional today, so the upload’s meditating in 4K limbo.\n"
        "Now, write your excuse for:\n{user_input}"
    ),

    "british_dry": (
        "Adopt a British dry humour tone—understated, tidy, and mildly self-deprecating.\n"
        "You must output EXACTLY ONE excuse that has this structure:\n"
        "1. A short statement of the issue.\n"
        "2. A subtle external reason or ironic observation.\n"
        "3. (optional) A wry twist or polite apology.\n"
        "Rules:\n"
        "- ≤2 sentences, crisp and dry.\n"
        "- Avoid dramatic exaggeration or slang.\n"
        "- Output only the excuse.\n"
        "Example:\n"
        "Example input: I missed the call.\n"
        "Example output: My Wi-Fi fancied a tea break just as the call began—how terribly British of it.\n"
        "Now, write your excuse for:\n{user_input}"
    ),

    "wholesome": (
        "You are kind, supportive, and constructive.\n"
        "You must output EXACTLY ONE excuse that has this structure:\n"
        "1. A gentle explanation for the mistake.\n"
        "2. A soft external reason that doesn’t blame anyone harshly.\n"
        "3. A quick positive action or fix.\n"
        "Rules:\n"
        "- ≤2 sentences, calm and compassionate.\n"
        "- No sarcasm, no self-hate.\n"
        "- Output only the excuse.\n"
        "Example:\n"
        "Example input: I missed the deadline.\n"
        "Example output: I lost track of time helping a friend, but I’ll finish the task right after lunch.\n"
        "Now, write your excuse for:\n{user_input}"
    ),
}

# —— 这里定义每种风格的 生成参数 ——
STYLE_PARAMS: Dict[str, Dict[str, Any]] = {
    "sarcastic":   {"temperature": 0.6,  "top_p": 0.8,  "top_k": 40, "repeat_penalty": 1.1, "num_predict": 60, "seed": 42},
    "absurd":      {"temperature": 0.85, "top_p": 0.9,  "top_k": 50, "repeat_penalty": 1.05,"num_predict": 80, "seed": 42},
    "creator":     {"temperature": 0.65, "top_p": 0.85, "top_k": 40, "repeat_penalty": 1.1, "num_predict": 70, "seed": 42},
    "british_dry": {"temperature": 0.55, "top_p": 0.8,  "top_k": 40, "repeat_penalty": 1.1, "num_predict": 50, "seed": 42},
    "wholesome":   {"temperature": 0.6,  "top_p": 0.8,  "top_k": 40, "repeat_penalty": 1.1, "num_predict": 60, "seed": 42},
}

DEFAULT_STYLE = "sarcastic" #默认风格，当用户没指定风格、或者输入的风格不存在，就用这个。
BAD_TAIL_MARKERS = ("Please note", "Disclaimer", "As an AI")  # 简单尾巴清理标记


def _cleanup_tail(text: str) -> str: #清理生成文本里那种“AI道德声明”小工具函数
    if not text:
        return text
    for marker in BAD_TAIL_MARKERS: #遍历刚才定义的那三个关键词。
        if marker in text: #如果文本里包含其中一个
            text = text.split(marker, 1)[0].rstrip() #从 marker 第一次出现的位置切开，保留前半部分。
    return text.strip() #最后再清理首尾空格，返回干净的文本


def run(user_input: str, style: str = DEFAULT_STYLE) -> Dict[str, Any]: #user_input: 用户输入的句子（比如 “我错过会议”）style: 用户指定的风格（默认用上面的 sarcastic）返回值：一个字典（Dict[str, Any]），包含结果详情。
    cleaner = TextCleaner() #创建一个“文本清洗器”的对象
    clean_result = cleaner.process(user_input) #把用户输入的原始文本（user_input）交给清洗器处理
    cleaned_text = clean_result["cleaned"] #从刚才清洗结果里取出“干净后的文本”

    print("🧹 Text Clean Score:", clean_result["scores"]) # 查看清洗评分

    style_safe = style.strip().lower() #把传进来的风格字符串清洗一下
    fallback_style = None

    # 组 prompt
    template = STYLE_TEMPLATES[style_safe] #从 STYLE_TEMPLATES 中取出对应的模板内容
    prompt = template.format(user_input=cleaned_text) #用 .format() 把 {user_input} 替换成实际的输入。

    # 选采样参数
    options = STYLE_PARAMS.get(style_safe, {}) #从 STYLE_PARAMS 中找该风格对应的生成参数。没找到就返回空字典（表示用默认的）。

    # 调模型
    client = LLMClient() #创建一个模型客户端对象
    result_text = client.generate(prompt, options=options) #把 prompt 和参数发给模型
    result_text = _cleanup_tail(result_text) #去掉免责声明、空格、多余废话

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

