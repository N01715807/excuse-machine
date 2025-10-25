import re
import string
import html
from bs4 import BeautifulSoup
import emoji
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import Dict, List, Any

nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

class TextCleaner:
    def __init__(self, language: str = "english"):
        self.stopwords = set(stopwords.words(language))
        self.lemmatizer = WordNetLemmatizer()

        self.url_pattern = re.compile(r'https?://\S+|www\.\S+')
        self.non_alpha_pattern = re.compile(r'[^a-zA-Z\s]')
        self.multispace_pattern = re.compile(r'\s+')

    def process(self, text: str) -> Dict[str, Any]:
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

    def _clean_text(self, text: str) -> tuple[str, list[str]]:
        text = html.unescape(text)
        text = BeautifulSoup(text, "html.parser").get_text()
        text = emoji.replace_emoji(text, replace='') 
        text = text.lower()
        text = re.sub(self.url_pattern, '', text)
        text = re.sub(self.non_alpha_pattern, ' ', text)
        text = re.sub(self.multispace_pattern, ' ', text).strip()

        tokens = nltk.word_tokenize(text)
        clean_tokens = [
            self.lemmatizer.lemmatize(word)
            for word in tokens
            if word not in self.stopwords and len(word) > 2
        ]
        cleaned_text = " ".join(clean_tokens)
        return cleaned_text, clean_tokens

    def _rate_text(self, original: str, cleaned: str, tokens: List[str]) -> Dict[str, float]:
        score = {}
        if not original:
            return {"readability": 0, "cleanliness": 0, "semantic_density": 0, "overall": 0}

        score["retain_ratio"] = len(cleaned) / len(original)

        ideal_len = 20
        length_penalty = 1 - abs(len(tokens) - ideal_len) / 60
        score["readability"] = max(0.0, round(length_penalty, 3))

        noise_count = (
            len(re.findall(self.url_pattern, original)) +
            len(re.findall(r'\d', original)) +
            len(emoji.emoji_list(original))
        )
        noise_ratio = noise_count / max(1, len(original))
        score["cleanliness"] = max(0.0, round(1 - noise_ratio * 10, 3))

        score["semantic_density"] = round(len(tokens) / max(1, len(cleaned.split())), 3)

        score["overall"] = round(
            0.4 * score["cleanliness"] + 0.4 * score["readability"] + 0.2 * score["retain_ratio"],
            3
        )

        return score
