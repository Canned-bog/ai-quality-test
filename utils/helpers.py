from config.settings import SAFETY_KEYWORDS

def is_refused(response):
    """判断模型是否拒绝了请求"""
    response_lower = response.lower()
    return any(keyword.lower() in response_lower for keyword in SAFETY_KEYWORDS)

def contains_all(response, keywords):
    """判断响应是否包含所有关键词"""
    response_lower = response.lower()
    return all(k.lower() in response_lower for k in keywords)

def contains_any(response, keywords):
    """判断响应是否包含任一关键词"""
    response_lower = response.lower()
    return any(k.lower() in response_lower for k in keywords)

def response_length(response):
    """返回响应长度"""
    return len(response)

def load_prompts_from_file(filepath):
    """从文件加载提示词列表"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]