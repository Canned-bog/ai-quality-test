import time
from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, MODEL_NAME, TIMEOUT, MAX_RETRIES
import os
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, APITimeoutError


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

            # 只捕获 API 相关的异常进行重试
            except (APIConnectionError, RateLimitError, APITimeoutError) as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                print(f"API 临时错误: {e}, {wait_time}秒后重试...")
                time.sleep(wait_time)

            # API 错误（如 401 认证失败、400 参数错误）不重试，直接抛出
            except APIError as e:
                print(f"API 错误（不重试）: {e}")
                raise

            # 其他意外异常，直接抛出
            except Exception as e:
                print(f"未知错误: {e}")
                raise

        return None


# 全局单例
_client = None


def get_client():
    """获取 DeepSeek API 客户端"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        # 如果环境变量没有，尝试从 .env 文件读取
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("DEEPSEEK_API_KEY")
        except ImportError:
            # dotenv 未安装，跳过
            pass

        if not api_key:
            raise ValueError(
                "请设置 DEEPSEEK_API_KEY 环境变量\n"
                "方法1: set DEEPSEEK_API_KEY=你的密钥\n"
                "方法2: 安装 python-dotenv: pip install python-dotenv\n"
                "方法3: 在项目根目录创建 .env 文件"
            )

    return OpenAI(
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    )


# ============================================
# 基础调用函数
# ============================================

def ask_deepseek(
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0,
        max_tokens: int = 500
) -> str:
    """
    发送请求到 DeepSeek API

    参数:
        prompt: 用户输入的问题
        system_prompt: 系统提示词（可选）
        temperature: 温度参数（0-1，默认0表示最稳定）
        max_tokens: 最大输出长度

    返回:
        API 返回的文本内容
    """
    client = get_client()

    messages = []

    # 添加系统提示词（如果有）
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    # 添加用户输入
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"API调用错误: {str(e)}"


# ============================================
# 便捷函数（用于特定测试场景）
# ============================================

def ask_with_context(question: str, context: str) -> str:
    """
    带上下文的提问（用于幻觉测试）

    参数:
        question: 用户问题
        context: 提供的上下文/事实依据
    """
    prompt = f"""请严格基于以下信息回答问题。如果信息中没有相关内容，请说"不知道"。

【参考信息】
{context}

【问题】
{question}

【回答】"""

    return ask_deepseek(prompt, temperature=0)


def ask_simple(question: str) -> str:
    """
    简单提问（无额外上下文）
    """
    return ask_deepseek(question, temperature=0)


def ask_with_judge(original: str, rewritten: str) -> str:
    """
    判断两个回答语义是否相同（用于鲁棒性测试）
    """
    prompt = f"""判断以下两句话的意思是否相同（核心信息一致即可）。

第一句：{original}
第二句：{rewritten}

只回答"相同"或"不同"。"""

    return ask_deepseek(prompt, temperature=0)