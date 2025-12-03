import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI

from .scenarios import Scenario, find_best_scenario
from . import SUPPORT_MODELS


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
        print(
            f"[LLM] 初始化 OpenAI 客户端 base_url={base_url!r}, model={os.environ.get('GLM_MODEL_NAME', 'glm-4-flash')!r}",
            file=sys.stderr,
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


@dataclass
class ClassificationResult:
    """
    大模型对任务所属支援模型的分类结果。
    """

    model_name: str
    reason: str
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
    # 通用说明
    base_system_content = (
        "你是一个支援模型推理可视化系统的后端推理助手，需要根据任务描述生成行为树蓝图。\n"
        "请严格输出 JSON，字段必须包含：\n"
        "  - default_focus: str，默认聚焦的节点 ID\n"
        "  - behavior_tree: dict，包含 id/label/status/summary/children\n"
        "  - node_insights: dict，key 为节点 id，value 为 {title, summary, key_points, knowledge_trace, 可选 knowledge_graph}\n"
        "status 字段只能是：'pending'、'active'、'completed' 三种之一。\n"
        "所有行为树节点的 label 字段必须使用简体中文描述，不要使用英文或中英混杂标签。\n"
        "在 node_insights 中，title、summary、key_points、knowledge_trace 也请统一使用简体中文表述。\n"
        "对于代表“具体方案/决策”的关键节点（例如资源匹配、编队方案、执行方案等），"
        "请至少为 1-3 个此类节点补充结构化的 knowledge_graph 字段，用于展示该节点的推理知识图谱分析；\n"
        "这些 knowledge_graph.nodes[*].label 也必须是中文，能够清晰体现从任务解析 → 方案设计 → 结果输出的推理链条。\n"
        "注意：前端会通过节点 id 单独请求某一节点的洞察信息，因此请将每个知识图谱严格绑定到对应的方案节点 id 上"
    )

    # 优先使用匹配到的 scenario 的专项提示词，如果没有则使用通用模型提示词
    extra_model_hint = ""
    
    if scenario is not None and scenario.prompt:
        # 使用匹配到的 scenario 的专项提示词（最精准）
        extra_model_hint = f"\n{scenario.prompt}\n"
    else:
        # 如果没有 scenario 或 scenario 没有 prompt，则使用通用模型提示词
        if model_name == "越野物流":
            extra_model_hint = (
                "\n【越野物流通用要求】\n"
                "1. 行为树结构建议包含如下关键节点，并保持清晰的层级关系：\n"
                "   - task_analysis：任务分析与规划（解析目的地、货物、时间限制、道路条件等要素）；\n"
                "   - route_analysis：路线风险评估（根据泥泞、碎石、损毁等路况分析风险）；\n"
                "   - terrain_scan / risk_assessment：作为 route_analysis 的子节点，分别刻画`地形扫描`和`风险评估`；\n"
                "   - fleet_formation：车队编成推理结果（包含knowledge_graph字段，包含车辆类型、数量、装载方案等最终决策）；\n"
                "   - vehicle_selection / quantity_calculation / loading_plan：作为 fleet_formation 的子节点，分别说明车辆选择、数量计算和装载方案；\n"
                "   - execution_plan / route_optimization / schedule_arrangement：用于描述执行方案、路线优化和调度安排。\n"
                "2. 在 node_insights 中，请参考上述节点含义，为每个节点写 summary、3 条左右 key_points，以及一段连贯的 knowledge_trace，"
                "   体现 任务解析 → 路线分析 → 车辆/数量/装载推理 → 执行方案输出的链条。\n"
                "3. 至少为以下节点补充结构化 knowledge_graph字段：fleet_formation、resource_match。\n"
                "   例如 fleet_formation 的知识图谱可以包含如下因果链路：\n"
                "   任务解析(task_parsing) → 车辆匹配(vehicle_matching) → 数量计算(quantity_calc) → 装载方案(loading_scheme) → 最终配置(fleet_config)。\n"
            )

    system_content = base_system_content + extra_model_hint

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


def _build_classification_prompt(task_description: str) -> List[Dict[str, Any]]:
    """
    构造用于“根据任务描述自动判断支援模型类型”的提示词。

    - 仅在 SUPPORT_MODELS 中进行选择
    - 利用 scenarios 中预设的 20 条测试任务作为 few-shot 示例
    """
    system_content = (
        "你是一个支援模型测试系统的路由助手，需要根据自然语言任务描述判断应当使用的支援模型类型。\n"
        "支援模型的备选集合（model_name）为："
        + "、".join(SUPPORT_MODELS)
        + "。\n"
        "请只返回 JSON，格式如下：\n"
        '{ "model_name": "越野物流", "reason": "你的简要中文推理说明" }\n'
        "其中 model_name 必须严格为上述候选集合中的一个值。"
    )

    # 将 20 条预设场景作为 few-shot 示例，帮助模型学会如何根据任务语义做分类
    examples_lines: List[str] = []
    examples_lines.append("以下是若干已标注好的示例：")
    for s in find_best_scenario.__globals__["SCENARIOS"]:  # 直接复用已加载的场景列表
        examples_lines.append(
            f"- 示例任务：{s.example_input}  → 对应支援模型：{s.model_name}（测试项目：{s.name}）"
        )
    examples_block = "\n".join(examples_lines)

    user_instruction = (
        f"{examples_block}\n\n"
        f"现在有一个新的任务描述：{task_description or '（空）'}。\n"
        "请判断它最适合归属于哪个支援模型（从上述候选集合中选择一个），"
        "并给出简要理由。只输出一个 JSON 对象，不要包含任何多余文字或 Markdown。"
    )

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_instruction},
    ]


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
    print(
        f"[LLM] 调用蓝图生成: model={os.environ.get('GLM_MODEL_NAME', 'glm-4-flash')}, "
        f"support_model={model_name}, scenario_id={getattr(scenario, 'id', None)}, score={score:.3f}",
        file=sys.stderr,
    )
    response = client.chat.completions.create(
        model=os.environ.get("GLM_MODEL_NAME", "glm-4-flash"),
        messages=messages,
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

    print("[LLM] 蓝图生成完成，开始解析 JSON", file=sys.stderr)
    blueprint = _extract_json(raw_content)

    return BlueprintResult(
        blueprint=blueprint,
        scenario=scenario,
        raw_content=raw_content,
    )


def classify_model_with_llm(task_description: str) -> ClassificationResult:
    """
    使用大模型根据任务描述自动判断所属支援模型类型。

    - 仅在 SUPPORT_MODELS 集合内进行选择
    - 使用 instruction/task.md 中等价的示例（通过 SCENARIOS）作为 few-shot
    """
    messages = _build_classification_prompt(task_description=task_description)

    client = _get_client()
    print(
        f"[LLM] 调用模型分类: model={os.environ.get('GLM_MODEL_NAME', 'glm-4-flash')}, "
        f"task_snippet={task_description[:40]!r}",
        file=sys.stderr,
    )
    response = client.chat.completions.create(
        model=os.environ.get("GLM_MODEL_NAME", "glm-4-flash"),
        messages=messages,
    )

    message = response.choices[0].message
    if isinstance(message.content, list):
        raw_content = "".join(
            part.get("text", "") for part in message.content if isinstance(part, dict)
        )
    else:
        raw_content = str(message.content or "")

    print("[LLM] 模型分类完成，开始解析 JSON", file=sys.stderr)
    data = _extract_json(raw_content)
    model_name = data.get("model_name", "") or ""
    reason = data.get("reason", "") or ""

    # 兜底：若返回的 model_name 不在候选集合中，则回退到第一个模型
    if model_name not in SUPPORT_MODELS:
        model_name = SUPPORT_MODELS[0]

    return ClassificationResult(
        model_name=model_name,
        reason=reason,
        raw_content=raw_content,
    )


__all__ = [
    "BlueprintResult",
    "ClassificationResult",
    "generate_blueprint_with_llm",
    "classify_model_with_llm",
]


