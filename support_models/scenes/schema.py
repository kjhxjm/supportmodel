from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Scenario:
    """
    预设的测试任务场景，用于为大模型提供 one-shot 示例。
    """

    id: str
    model_name: str
    name: str
    example_input: str
    reasoning_chain: str
    prompt: Optional[str] = None  # 该场景的专项要求提示词，用于细化蓝图生成要求
    # 当用户任务描述与 example_input 相似度 > 0.9 时，可直接返回该标准输出而不调用大模型
    example_output: Optional[Dict[str, Any]] = None