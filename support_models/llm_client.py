import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI

from .scenarios import Scenario, find_best_scenario


_client: Optional[OpenAI] = None


def _get_client() -> OpenAI:
    """
    懒加载 OpenAI/GLM 客户端，避免在未配置环境变量时过早报错。
    """
    global _client
    if _client is None:
        base_url = os.environ.get("GLM_BASE_URL")
        api_key = os.environ.get("GLM_API_KEY")
        if not base_url or not api_key:
            raise RuntimeError(
                "GLM_BASE_URL 或 GLM_API_KEY 未配置，无法调用大模型生成蓝图。"
            )
        _client = OpenAI(base_url=base_url, api_key=api_key)
    return _client


@dataclass
class BlueprintResult:
    """
    大模型生成的蓝图结果封装。
    """

    blueprint: Dict[str, Any]
    scenario: Optional[Scenario]
    raw_content: str


def _build_prompt(
    model_name: str, task_description: str, scenario: Optional[Scenario]
) -> List[Dict[str, Any]]:
    """
    构造用于大模型生成蓝图的对话消息。

    这里遵循现有 README/base.py 中定义的 BLUEPRINT 结构：
    - default_focus: str
    - behavior_tree: dict
    - node_insights: dict
    """
    system_content = (
        "你是一个支援模型推理可视化系统的后端推理助手，需要根据任务描述生成行为树蓝图。\n"
        "请严格输出 JSON，字段必须包含：\n"
        "  - default_focus: str，默认聚焦的节点 ID\n"
        "  - behavior_tree: dict，包含 id/label/status/summary/children\n"
        "  - node_insights: dict，key 为节点 id，value 为 {title, summary, key_points, knowledge_trace, 可选 knowledge_graph}\n"
        "status 字段只能是：'pending'、'active'、'completed' 三种之一。\n"
    )

    scenario_block = ""
    if scenario is not None:
        scenario_block = (
            f"当前所属支援模型：{model_name}\n"
            f"匹配到的测试任务场景：{scenario.id} - {scenario.name}\n"
            f"该场景的任务示例（one-shot 提示）：{scenario.example_input}\n"
            f"该场景在文档中描述的推理链条：{scenario.reasoning_chain}\n"
            "请严格遵循上述推理链条的逻辑顺序设计行为树节点，以及节点洞察中的 summary 和 key_points。\n"
        )

    user_instruction = (
        f"{scenario_block}"
        f"现在的真实任务描述为：{task_description or '（空）'}。\n"
        "请先进行任务解析（目的地/对象/时间或安全约束等），"
        "再结合 one-shot 示例和推理链条，生成一棵清晰的行为树，以及对应的节点洞察。\n"
        "最终只输出一个 JSON 对象，不要包含任何额外说明或 Markdown 标记。"
    )

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_instruction},
    ]
    return messages


def _extract_json(content: str) -> Dict[str, Any]:
    """
    从模型返回的文本中尽可能鲁棒地提取 JSON。

    - 优先直接 json.loads
    - 若失败，则尝试截取首尾花括号之间内容再解析
    """
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # 尝试从首尾大括号截取
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            snippet = content[start : end + 1]
            return json.loads(snippet)
        raise


def generate_blueprint_with_llm(
    model_name: str, task_description: str
) -> BlueprintResult:
    """
    使用大模型根据任务描述动态生成蓝图。

    - 会自动在预设的测试任务场景中查找与 task_description 最相近的一条，
      并将其作为 one-shot 示例融入提示词。
    - 返回 BlueprintResult，便于上层在需要时查看匹配到的场景和原始内容。
    """
    best: Tuple[Optional[Scenario], float] = find_best_scenario(
        model_name=model_name, query=task_description
    )
    scenario, score = best

    # 可以根据相似度阈值决定是否使用场景信息，这里只要找到就使用
    messages = _build_prompt(model_name=model_name, task_description=task_description, scenario=scenario)

    client = _get_client()
    response = client.chat.completions.create(
        model=os.environ.get("GLM_MODEL_NAME", "glm-4-flash"),
        messages=[{"role": "user", "content": messages}],
    )

    # 兼容 OpenAI 风格的返回结构
    message = response.choices[0].message
    raw_content = ""
    if isinstance(message.content, list):
        # 多模态内容，这里只拼接文本部分
        raw_content = "".join(
            part.get("text", "") for part in message.content if isinstance(part, dict)
        )
    else:
        raw_content = str(message.content or "")

    blueprint = _extract_json(raw_content)

    return BlueprintResult(
        blueprint=blueprint,
        scenario=scenario,
        raw_content=raw_content,
    )


__all__ = ["BlueprintResult", "generate_blueprint_with_llm"]


