import pytest
from utils.helpers import contains_any


@pytest.mark.functional
class TestFunctional:
    """功能性测试套件"""

    @pytest.mark.parametrize("prompt,expected_keywords", [
        ("你好", ["你好", "您好"]),
        ("1+1等于几", ["2", "二"]),
        ("今天天气怎么样", ["天气"]),
    ])
    def test_normal_questions(self, model_client, prompt, expected_keywords):
        """测试正常问题"""
        response = model_client.ask(prompt)
        assert contains_any(response, expected_keywords), \
            f"期望包含 {expected_keywords}，实际: {response}"
'''
    def test_long_conversation(self, model_client):
        """测试长对话能力"""
        responses = []
        for q in ["你好", "我叫小明", "我叫什么名字？"]:
            responses.append(model_client.ask(q))
        # 验证能记住上下文（简化版）
        assert "小明" in responses[-1] or "明" in responses[-1]
'''