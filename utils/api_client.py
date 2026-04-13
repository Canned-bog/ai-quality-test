import time
from openai import OpenAI
from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME, TIMEOUT, MAX_RETRIES


class ModelClient:
    """大模型API客户端封装"""

    def __init__(self):
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            timeout=TIMEOUT
        )
        self.model = MODEL_NAME

    def ask(self, prompt, temperature=0.7, max_retries=MAX_RETRIES):
        """发送请求，支持自动重试"""
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature
                )
                return response.choices[0].message.content
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # 指数退避
        return None

    def ask_batch(self, prompts, delay=0.5):
        """批量发送请求（避免限流）"""
        results = []
        for prompt in prompts:
            results.append(self.ask(prompt))
            time.sleep(delay)
        return results


# 全局单例
_client = None


def get_client():
    global _client
    if _client is None:
        _client = ModelClient()
    return _client