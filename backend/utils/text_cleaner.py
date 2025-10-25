import re
import string
import html
from bs4 import BeautifulSoup
import emoji
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import Dict, List, Any

# === 初始化资源（第一次运行时自动下载） ===
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

class TextCleaner:
    """AI文本清洗与可读性评分器"""
    def __init__(self, language: str = "english"):
        self.stopwords = set(stopwords.words(language))
        self.lemmatizer = WordNetLemmatizer()

        # 正则模板
        self.url_pattern = re.compile(r'https?://\S+|www\.\S+')
        self.non_alpha_pattern = re.compile(r'[^a-zA-Z\s]')
        self.multispace_pattern = re.compile(r'\s+')

    # === 核心API ===
    def process(self, text: str) -> Dict[str, Any]:
        """主入口：清洗 + 打分 + 返回结构化结果"""
        original = text
        cleaned, tokens = self._clean_text(text)
        scores = self._rate_text(original, cleaned, tokens)

        return {
            "original": original,
            "cleaned": cleaned,
            "tokens": tokens,
            "token_count": len(tokens),
            "scores": scores,
        }

    # === 清洗流程 ===
    def _clean_text(self, text: str) -> tuple[str, list[str]]:
        text = html.unescape(text)  # 解码HTML实体
        text = BeautifulSoup(text, "html.parser").get_text()  # 去HTML标签
        text = emoji.replace_emoji(text, replace='')  # 去emoji
        text = text.lower()
        text = re.sub(self.url_pattern, '', text)
        text = re.sub(self.non_alpha_pattern, ' ', text)
        text = re.sub(self.multispace_pattern, ' ', text).strip()

        # 分词 + 停用词过滤 + 词形还原
        tokens = nltk.word_tokenize(text)
        clean_tokens = [
            self.lemmatizer.lemmatize(word)
            for word in tokens
            if word not in self.stopwords and len(word) > 2
        ]
        cleaned_text = " ".join(clean_tokens)
        return cleaned_text, clean_tokens

    # === 打分逻辑 ===
    def _rate_text(self, original: str, cleaned: str, tokens: List[str]) -> Dict[str, float]:
        score = {}
        if not original:
            return {"readability": 0, "cleanliness": 0, "semantic_density": 0, "overall": 0}

        # 保留率
        score["retain_ratio"] = len(cleaned) / len(original)

        # 可读性（理想长度 10~30 词）
        ideal_len = 20
        length_penalty = 1 - abs(len(tokens) - ideal_len) / 60
        score["readability"] = max(0.0, round(length_penalty, 3))

        # 噪声比（URL、emoji、数字等）
        noise_count = (
            len(re.findall(self.url_pattern, original)) +
            len(re.findall(r'\d', original)) +
            len(emoji.emoji_list(original))
        )
        noise_ratio = noise_count / max(1, len(original))
        score["cleanliness"] = max(0.0, round(1 - noise_ratio * 10, 3))

        # 语义密度（词数 / 文本长度）
        score["semantic_density"] = round(len(tokens) / max(1, len(cleaned.split())), 3)

        # 综合分
        score["overall"] = round(
            0.4 * score["cleanliness"] + 0.4 * score["readability"] + 0.2 * score["retain_ratio"],
            3
        )

        return score
