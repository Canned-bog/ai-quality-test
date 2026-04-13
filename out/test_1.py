import pytest
from deepeval import assert_test
from deepeval.metrics import HallucinationMetric
from deepeval.test_case import LLMTestCase
from deepeval.models import DeepSeekModel


def test_no_hallucination():
    # 配置 DeepSeek 模型
    model = DeepSeekModel(
        model="deepseek-chat",
        api_key="sk-b9397f787deb4685b61098f58cee9497",  # 替换成你的真实 API Key
        temperature=0
    )

    context = ["Python由Guido van Rossum于1991年创建。"]
    actual_output = "Python是由Guido van Rossum在1991年设计的编程语言。"

    test_case = LLMTestCase(
        input="Python是谁创造的？",
        actual_output=actual_output,
        context=context
    )

    # 创建幻觉检测指标，传入 DeepSeek 模型
    metric = HallucinationMetric(
        threshold=0.3,
        model=model  # 关键：使用 DeepSeek 替代默认的 GPT
    )

    # 断言测试
    assert_test(test_case, [metric])