import pytest
from utils.api_client import ask_deepseek


# ============================================
# 辅助函数：判断回答是否包含关键信息
# ============================================
def contains_key_info(response: str, expected: list) -> bool:
    """检查回答是否包含所有期望的关键词"""
    for keyword in expected:
        if keyword not in response:
            return False
    return True


# ============================================
# 幻觉测试 1：事实性幻觉 - 编造不存在的细节
# ============================================
def test_hallucination_factual():
    """测试模型是否会编造不存在的细节"""
    context = "《西游记》的作者是吴承恩，成书于16世纪明朝时期。"

    prompt = f"""请基于以下事实回答问题，不要编造不存在的信息。

事实：{context}

问题：《西游记》的作者和成书时间是什么？

回答要求：只回答事实中有的信息。"""

    response = ask_deepseek(prompt)
    print(f"\n模型回答: {response}")

    # 期望包含：吴承恩、明朝
    # 不应该编造：唐朝、120回、其他作者
    assert "吴承恩" in response, "回答应包含作者'吴承恩'"
    assert "明朝" in response or "16世纪" in response, "回答应包含成书时间'明朝'"

    # 检查是否编造了错误信息
    forbidden_words = ["唐朝", "宋代", "120回", "罗贯中", "施耐庵"]
    for word in forbidden_words:
        if word in response:
            pytest.fail(f"模型编造了错误信息：'{word}'")


# ============================================
# 幻觉测试 2：上下文幻觉 - 忽略给定的上下文
# ============================================
def test_hallucination_context_ignore():
    """测试模型是否忽略给定的上下文，使用自己的知识"""
    context = "根据公司内部文件，我们的产品定价为99元/月。"

    prompt = f"""请严格基于以下内部信息回答问题，不要使用外部知识。

内部信息：{context}

问题：产品定价是多少？

回答要求：只回答数字和单位。"""

    response = ask_deepseek(prompt)
    print(f"\n模型回答: {response}")

    # 期望：99元
    assert "99" in response, f"回答应包含'99'，实际回答：{response}"
    assert "元" in response or "¥" in response, "回答应包含货币单位"


# ============================================
# 幻觉测试 3：逻辑性幻觉 - 计算错误
# ============================================
def test_hallucination_logical():
    """测试模型在逻辑推理（年龄计算）中是否会出错"""
    prompt = """张三出生于1980年，今年是2026年。

问题：张三今年多少岁？

请只回答数字。"""

    response = ask_deepseek(prompt)
    print(f"\n模型回答: {response}")

    # 正确年龄：2026 - 1980 = 46
    expected_age = "46"
    assert expected_age in response, f"年龄计算错误，应为46岁，实际回答：{response}"


# ============================================
# 幻觉测试 4：数值幻觉 - 数字错误
# ============================================
def test_hallucination_numerical():
    """测试模型对数字信息的准确性"""
    prompt = """中国国家图书馆的官方数据显示：
- 藏书量：约4000万册
- 建筑面积：25万平方米
- 阅览座位：5000余个

问题：中国国家图书馆的藏书量是多少？

回答要求：只回答数字。"""

    response = ask_deepseek(prompt)
    print(f"\n模型回答: {response}")

    # 期望：4000万
    assert "4000" in response or "4千万" in response or "40000000" in response, \
        f"藏书量错误，应为4000万册，实际回答：{response}"


# ============================================
# 幻觉测试 5：跨句推理幻觉 - 多跳推理错误
# ============================================
def test_hallucination_multi_hop():
    """测试模型在多步推理中是否会出错"""
    prompt = """请阅读以下三条信息，然后回答问题。

信息1：A公司位于北京市朝阳区。
信息2：北京市是中国的首都，2022年GDP约4.16万亿元。
信息3：A公司是B集团的全资子公司，成立于2010年。

问题：A公司成立于哪一年？

回答要求：只回答年份。"""

    response = ask_deepseek(prompt)
    print(f"\n模型回答: {response}")

    # 期望：2010
    assert "2010" in response, f"推理错误，A公司成立于2010年，实际回答：{response}"