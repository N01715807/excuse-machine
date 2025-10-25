import os
import httpx
from typing import Optional, Dict, Any

class LLMClient:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://ollama-appECM:11434") #找 OLLAMA_URL，找不到就用默认值 http://ollama-appECM:11434
        self.model = os.getenv("OLLAMA_MODEL", "phi3:mini") #去找 OLLAMA_MODEL（模型名字），找不到就用默认值 phi3:mini；
        self.timeout = 60 #把网络请求的最大等待时间设为 60 秒

        self.default_options: Dict[str, Any] = {
            "temperature": 0.9, #放飞程度
            "top_p": 0.9, #采样控制
            "num_predict": 120, #输出长度为120个字
        }

    def generate(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> str: #发送 prompt 到 Ollama 模型并返回生成文本
        payload = {
            "model": self.model, #用哪个模型
            "prompt": prompt, #问的内容
            "stream": False, #一次性拿完结果
            "options": {**self.default_options, **(options or {}) #把默认参数和用户传入的参数合并如果传入 options，会覆盖默认设置
            },}

        try:
            with httpx.Client(timeout=self.timeout) as client: #打开一个 HTTP 客户端，会在退出时自动关闭连接
                res = client.post(f"{self.base_url}/api/generate", json=payload) #向 Ollama 服务器发一个 POST 请求，把前面准备的字典作为 JSON 数据发送
                res.raise_for_status() #如果 HTTP 状态码不是 200，就抛出异常
                data = res.json() #把服务器返回的数据解析为 Python 字典
                text = (data.get("response") or "").strip() #从响应中取出模型生成的文字
                return text
        except Exception as e:
            print(f"[LLMClient Error] {e}")
            return ""