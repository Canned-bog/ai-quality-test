import pytest
import os
from openai import OpenAI

# ========== DeepSeek API 配置 ==========
DEEPSEEK_API_KEY =os.getenv("DEEPSEEK_API_KEY")  # 替换成你的真实 Key

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)


def ask_deepseek(prompt: str) -> str:
    """发送请求到 DeepSeek API 并返回响应内容"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # 温度设为0，保证输出稳定
            max_tokens=50  # 限制输出长度
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"


# ========== 鲁棒性测试 ==========

@pytest.mark.parametrize("original,rewritten", [
    ("今天天气怎么样", "今日天气如何"),
    ("如何学好Python", "Python学习的方法有哪些"),
])
def test_paraphrase_robustness(original, rewritten):
    """测试改写后的输入是否得到语义一致的输出"""
    ans1 = ask_deepseek(original)
    ans2 = ask_deepseek(rewritten)

    # 用 DeepSeek 判断两句话语义是否相同
    judge_prompt = f"""判断下面两句话的意思是否相同（核心信息一致即可）。
只回答"相同"或"不同"。

第一句：{ans1}
第二句：{ans2}"""

    result = ask_deepseek(judge_prompt)
    assert "相同" in result, f"语义不一致：\n原问句回答：{ans1}\n改写问句回答：{ans2}\n判断结果：{result}"
def test_irrelevant_noise():
    """测试无关噪声输入是否影响正确答案"""
    clean = "法国的首都是哪里？"
    noisy = "你好啊，请问法国的首都是哪里？谢谢！"

    ans_clean = ask_deepseek(clean)
    ans_noisy = ask_deepseek(noisy)

    assert "巴黎" in ans_clean, f"干净输入未返回'巴黎'，返回：{ans_clean}"
    assert "巴黎" in ans_noisy, f"带噪声输入未返回'巴黎'，返回：{ans_noisy}"