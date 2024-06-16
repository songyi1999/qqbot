import re




def fix_question(question: str) -> str:
    """ 从用户输入的文本中移除 @ 符号和用户 ID，并保留问题描述。
    >>> fix_question('<@!123> This is a test')
    ' this IS A test'
    """
    user_id, *others = re.split('<@!(\d+)>', question)[1:]  # 获取用户 ID
    return ' '.join(others)