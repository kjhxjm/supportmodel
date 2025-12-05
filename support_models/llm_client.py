import json
import os
import re
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
        # base_url = os.environ.get("GLM_BASE_URL")
        # api_key = os.environ.get("GLM_API_KEY")
        base_url = os.environ.get("BASE_URL")
        api_key = os.environ.get("API_KEY")

        if not base_url or not api_key:
            raise RuntimeError(
                "GLM_BASE_URL 或 GLM_API_KEY 未配置，无法调用大模型生成蓝图。"
            )
        print(
            f"[LLM] 初始化 OpenAI 客户端 base_url={base_url!r}, model={os.environ.get('MODEL_NAME', 'glm-4-flash')!r}",
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
    # JSON Schema 格式说明
    json_schema_example = """{
  "default_focus": "priority_plan",
  "behavior_tree": {
    "id": "task_parse",
    "label": "任务解析",
    "status": "completed",
    "summary": "解析任务描述并对接相关清单。",
    "children": [
      {
        "id": "data_clean",
        "label": "数据清洗",
        "status": "completed",
        "summary": "融合多源数据。",
        "children": []
      }
    ]
  },
  "node_insights": {
    "task_parse": {
      "title": "任务解析",
      "summary": "抽取任务地点、数量与通联方式，构建统一任务面板。",
      "key_points": [
        "语义解析识别关键结构",
        "与知识库比对标签",
        "向下游节点广播标准化任务包"
      ],
      "knowledge_trace": "通过"任务文本→标准任务模板"链路定位到支援模型的场景入口。"
    },
    "priority_plan": {
      "title": "优先级排序",
      "summary": "结合指数与资源约束动态生成排序列表。",
      "key_points": [
        "指数计算：多维度指标加权",
        "资源约束：实时评估",
        "动态重排：变动即刻刷新序列"
      ],
      "knowledge_trace": "综合指数与资源匹配逻辑，输出实时排序。",
      "knowledge_graph": {
        "nodes": [
          {"id": "input_data", "label": "输入数据", "type": "input"},
          {"id": "calculation", "label": "计算过程", "type": "process"},
          {"id": "result", "label": "排序结果", "type": "output"}
        ],
        "edges": [
          {"source": "input_data", "target": "calculation"},
          {"source": "calculation", "target": "result"}
        ]
      }
    }
  }
}"""

    # 通用说明
    base_system_content = (
        "你是一个支援模型推理可视化系统的后端推理助手，需要根据任务描述生成行为树蓝图。\n\n"
        "📋 输出格式要求（严格遵循）：\n"
        "1. 必须输出有效的 JSON 对象，不要包含任何 Markdown 代码块标记（如 ```json 或 ```）。\n"
        "2. JSON 结构必须包含以下三个顶级字段：\n"
        "   - default_focus: string，默认聚焦的节点 ID（必须是 behavior_tree 中存在的节点 id）\n"
        "   - behavior_tree: object，行为树根节点，包含以下字段：\n"
        "     * id: string（唯一标识符）\n"
        "     * label: string（简体中文显示名称，必须包含具体数值结果）\n"
        "     * status: string（只能是 'pending'、'active'、'completed' 之一）\n"
        "     * summary: string（节点简要描述，简体中文，必须包含具体数值而非空泛描述）\n"
        "     * children: array（子节点数组，每个子节点结构相同，递归定义）\n"
        "   - node_insights: object，节点洞察字典，key 为节点 id，value 为对象，包含：\n"
        "     * title: string（洞察标题，简体中文）\n"
        "     * summary: string（详细描述，简体中文，必须包含具体数值而非空泛描述）\n"
        "     * key_points: array<string>（关键要点列表，3-5 条，简体中文，每条必须包含具体数值或计算过程）\n"
        "     * knowledge_trace: string（推理过程说明，简体中文，使用箭头（→）连接各个推理步骤）\n"
        "     * knowledge_graph: object（可选，仅关键决策节点需要，包含 nodes 和 edges）\n"
        "       - nodes: array<{id: string, label: string, type: string}>\n"
        "       - edges: array<{source: string, target: string}>\n\n"
        "3. 所有文本字段（label、summary、title、key_points、knowledge_trace、knowledge_graph.nodes[].label）必须使用简体中文。\n"
        "4. status 字段只能是：'pending'、'active'、'completed' 三种之一。\n"
        "5. knowledge_graph 中节点的 type 字段只能是：'input'、'process'、'decision'、'output' 之一。\n"
        "6. knowledge_graph 的 nodes[].label 必须包含具体参数信息，格式：\"节点名称(具体参数1, 具体参数2, ...)\"\n"
        "7. knowledge_graph 的 nodes 和 edges 必须形成有向无环图，能够清晰体现从任务解析 → 方案设计 → 结果输出的推理链条。\n\n"
        "🌳 行为树结构要求（必须遵循）：\n"
        "1. 行为树必须至少包含两层结构：\n"
        "   - 根节点必须有子节点（第一层）\n"
        "   - 至少有一个子节点还有子节点（第二层）\n"
        "   - 这样可以确保行为树有足够的层级深度，体现完整的推理过程\n"
        "2. 节点 label 必须包含具体数值结果，不能使用空泛描述。\n"
        "   示例：\"✅ 车队编成结果：2辆中型越野无人车\"、\"✅ 数量计算：2辆\"、\"📦 物资属性解析：医疗物资X，50箱，2.5m³\"\n"
        "3. 节点 summary 必须包含具体数值、时间、比例等量化信息，不能使用\"合适的\"、\"一定的\"、\"若干\"等模糊词汇。\n"
        "   正确示例：\"在2小时时限与道路损毁风险约束下，选择2辆中型越野无人车运输资源Y，其中车辆1装载60%，车辆2装载40%作为冗余备份。\"\n"
        "   错误示例：\"选择合适的车辆进行运输\"（过于空泛，缺少具体数值）\n\n"
        "📊 node_insights 内容要求（必须遵循）：\n"
        "1. 为 behavior_tree 中出现的每一个节点（包括所有子节点）提供详细的 node_insights。\n"
        "2. summary 必须包含：\n"
        "   - 具体数值（如：2小时、2辆、60%、50kg、120箱、115箱等）\n"
        "   - 具体对象（如：位置X、资源Y、中型越野无人车、医疗物资X等）\n"
        "   - 具体约束条件（如：道路损毁风险、20%冗余、有效期至2025年12月等）\n"
        "   - 不能使用\"合适的\"、\"一定的\"、\"若干\"等模糊词汇\n"
        "3. key_points 每条必须：\n"
        "   - 包含具体数值或计算过程\n"
        "   - 对于计算类/分析类节点，必须包含：计算假设、计算公式或推理步骤、具体结果、验证条件\n"
        "   - 每条 key_point 应该是一个完整的、可独立理解的句子，避免过于简短的短语\n"
        "4. knowledge_trace 必须：\n"
        "   - 使用箭头（→）连接各个推理步骤\n"
        "   - 包含具体的输入、处理过程、输出结果\n"
        "   - 体现完整的推理链条，格式示例：\"任务文本解析 → 目的地/货物/时间/路况要素抽取 → 形成可供后续节点复用的标准任务描述。\"\n"
        "5. 至少有一个 node_insights 内的节点包含 knowledge_graph 字段：\n"
        "   - 通常为核心决策节点（如最终方案、优先级排序、资源匹配、车队编成、仓位推荐等）\n"
        "   - knowledge_graph 必须体现完整因果链路，从输入到输出的推理过程\n"
        "   - nodes 的 label 必须包含具体参数信息，格式：\"节点名称(具体参数1, 具体参数2, ...)\"\n"
        "   示例：\"任务解析(位置X, 资源Y, 2小时, 道路损毁风险)\"、\"数量计算(2辆, 含20%冗余)\"、\"装载方案(1车60%,1车40%)\"\n\n"
        f"📝 参考格式示例：\n{json_schema_example}\n\n"
        "⚠️ 输出质量检查清单（生成内容后，请确保）：\n"
        "□ 行为树至少包含两层结构（根节点有子节点，且至少一个子节点有子节点）\n"
        "□ 至少有一个 node_insights 内的节点包含 knowledge_graph\n"
        "□ 所有 label 包含具体数值\n"
        "□ 所有 summary 包含具体数值而非空泛描述\n"
        "□ 所有 key_points 包含分析过程或具体参数\n"
        "□ 所有 knowledge_trace 使用箭头连接且包含具体步骤\n"
        "□ knowledge_graph 的 nodes label 包含参数信息\n"
        "□ 输出必须是纯 JSON，不要包含任何解释文字、Markdown 标记或代码块\n"
        "□ 确保所有节点 id 在 behavior_tree 和 node_insights 中保持一致\n"
        "□ node_insights 中必须为 behavior_tree 中的每个节点提供对应的洞察信息"
    )

    # 优先使用匹配到的 scenario 的专项提示词，如果没有则使用通用模型提示词
    extra_model_hint = ""
    
    if scenario is not None and scenario.prompt:
        # 使用匹配到的 scenario 的专项提示词（最精准）
        extra_model_hint = (
            f"\n🎯 【专项场景要求】\n"
            f"{scenario.prompt}\n"
            f"注意：上述要求中的节点必须严格遵循 JSON 格式规范，确保所有字段类型正确。\n"
        )
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
        f"现在的真实任务描述为：{task_description or '（空）'}。\n\n"
        "📌 生成要求：\n"
        "1. 请先进行任务解析（目的地/对象/时间或安全约束等），理解任务的核心需求。\n"
        "2. 结合 one-shot 示例和推理链条，生成一棵清晰的行为树，确保：\n"
        "   - 行为树至少包含两层结构（根节点有子节点，且至少一个子节点有子节点）\n"
        "   - 节点层级合理、逻辑连贯\n"
        "   - 所有节点的 label 和 summary 包含具体数值而非空泛描述\n"
        "3. 为 behavior_tree 中的每个节点在 node_insights 中提供对应的洞察信息：\n"
        "   - summary 必须包含具体数值、对象和约束条件\n"
        "   - key_points 每条必须包含具体数值或计算过程\n"
        "   - knowledge_trace 使用箭头（→）连接推理步骤\n"
        "4. 确保所有节点 id 在 behavior_tree 和 node_insights 中保持一致。\n"
        "5. 为关键决策节点（如最终方案、优先级排序、资源匹配、车队编成、仓位推荐等）添加 knowledge_graph：\n"
        "   - 至少有一个节点包含 knowledge_graph\n"
        "   - knowledge_graph 的 nodes label 必须包含具体参数信息\n"
        "   - knowledge_graph 必须体现完整的因果推理链路\n\n"
        "⚠️ 输出要求：\n"
        "- 最终只输出一个纯 JSON 对象，不要包含任何额外说明、Markdown 代码块标记（```json 或 ```）或解释文字。\n"
        "- JSON 必须格式正确，可以被 json.loads() 直接解析。\n"
        "- 确保所有必需字段都存在且类型正确。\n"
        "- 生成后请对照上述检查清单验证输出质量。"
    )

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_instruction},
    ]
    return messages


def _build_classification_prompt(task_description: str) -> List[Dict[str, Any]]:
    """
    构造用于"根据任务描述自动判断支援模型类型"的提示词。

    - 仅在 SUPPORT_MODELS 中进行选择
    - 利用 scenarios 中预设的测试任务作为 few-shot 示例
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
    - 若失败，则尝试移除 Markdown 代码块标记
    - 再尝试使用平衡括号算法提取完整的 JSON 对象
    """
    content = content.strip()
    
    # 移除可能的 Markdown 代码块标记
    if content.startswith("```"):
        # 移除开头的 ```json 或 ```
        lines = content.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        # 移除结尾的 ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()
    
    # 尝试直接解析
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    # 尝试从首尾大括号截取（使用平衡括号算法）
    start = content.find("{")
    if start != -1:
        # 使用平衡括号算法找到匹配的结束括号
        bracket_count = 0
        in_string = False
        escape_next = False
        
        for i in range(start, len(content)):
            char = content[i]
            
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '{':
                    bracket_count += 1
                elif char == '}':
                    bracket_count -= 1
                    if bracket_count == 0:
                        # 找到匹配的结束括号
                        end = i
                        snippet = content[start : end + 1]
                        try:
                            return json.loads(snippet)
                        except json.JSONDecodeError:
                            pass
                        break
        
        # 如果平衡括号算法失败，尝试简单的首尾截取
        end = content.rfind("}")
        if end != -1 and end > start:
            snippet = content[start : end + 1]
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                pass
    
    # 最后尝试：查找所有可能的JSON对象，选择最长的有效对象
    json_candidates = []
    start_pos = 0
    while True:
        start = content.find("{", start_pos)
        if start == -1:
            break
        
        bracket_count = 0
        in_string = False
        escape_next = False
        
        for i in range(start, len(content)):
            char = content[i]
            
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '{':
                    bracket_count += 1
                elif char == '}':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end = i
                        snippet = content[start : end + 1]
                        try:
                            parsed = json.loads(snippet)
                            json_candidates.append((len(snippet), parsed))
                        except json.JSONDecodeError:
                            pass
                        break
        
        start_pos = start + 1
    
    # 选择最长的有效JSON对象
    if json_candidates:
        json_candidates.sort(reverse=True)  # 按长度降序排列
        return json_candidates[0][1]
    
    raise ValueError(f"无法从内容中提取有效的 JSON。内容开头：{content[:500]}")


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

    # 若与某个预设场景的 example_input 相似度 >= 0.9，且该场景预置了标准 example_output，
    # 则直接返回该标准蓝图，不再调用大模型，以保证结果稳定且粒度一致。
    if scenario is not None and score >= 0.9 and getattr(scenario, "example_output", None):
        print(
            f"[LLM] 命中高相似度标准场景，直接返回预置 example_output: "
            f"support_model={model_name}, scenario_id={scenario.id}, score={score:.3f}",
            file=sys.stderr,
        )
        return BlueprintResult(
            blueprint=scenario.example_output,  # type: ignore[arg-type]
            scenario=scenario,
            raw_content="__STATIC_EXAMPLE_OUTPUT__",
        )

    # 否则使用匹配到的场景提示词，构造对话调用大模型生成蓝图
    messages = _build_prompt(
        model_name=model_name,
        task_description=task_description,
        scenario=scenario,
    )

    client = _get_client()
    print(
        f"[LLM] 调用蓝图生成: model={os.environ.get('MODEL_NAME', 'glm-4-flash')}, "
        f"support_model={model_name}, scenario_id={getattr(scenario, 'id', None)}, score={score:.3f}",
        file=sys.stderr,
    )
    response = client.chat.completions.create(
        model=os.environ.get("MODEL_NAME", "glm-4-flash"),
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
    print(f"[LLM] 原始内容长度: {len(raw_content)} 字符", file=sys.stderr)
    try:
        blueprint = _extract_json(raw_content)
        print(f"[LLM] JSON提取成功，提取出的键: {list(blueprint.keys())}", file=sys.stderr)
        
        # 验证蓝图结构
        if not isinstance(blueprint, dict):
            raise ValueError("蓝图必须是字典类型")
        
        if "behavior_tree" not in blueprint:
            print(f"[LLM] 调试: 提取出的JSON结构: {list(blueprint.keys())}", file=sys.stderr)
            print(f"[LLM] 调试: 原始内容前1000字符: {raw_content[:1000]}", file=sys.stderr)
            raise ValueError("蓝图缺少 'behavior_tree' 字段")
        
        if "node_insights" not in blueprint:
            raise ValueError("蓝图缺少 'node_insights' 字段")
        
        # 验证 behavior_tree 结构
        tree = blueprint["behavior_tree"]
        if not isinstance(tree, dict):
            raise ValueError("behavior_tree 必须是字典类型")
        
        required_tree_fields = ["id", "label", "status", "summary", "children"]
        for field in required_tree_fields:
            if field not in tree:
                raise ValueError(f"behavior_tree 缺少必需字段: {field}")
        
        # 验证 status 值
        if tree["status"] not in ["pending", "active", "completed"]:
            print(f"[LLM] 警告: behavior_tree.status 值 '{tree['status']}' 不在标准值列表中，将使用 'pending'", file=sys.stderr)
            tree["status"] = "pending"
        
        # 验证 node_insights 结构
        insights = blueprint["node_insights"]
        if not isinstance(insights, dict):
            raise ValueError("node_insights 必须是字典类型")
        
        # 验证每个节点的洞察信息
        for node_id, insight in insights.items():
            if not isinstance(insight, dict):
                print(f"[LLM] 警告: 节点 {node_id} 的洞察信息不是字典类型，将使用默认值", file=sys.stderr)
                continue
            
            required_insight_fields = ["title", "summary", "key_points", "knowledge_trace"]
            for field in required_insight_fields:
                if field not in insight:
                    print(f"[LLM] 警告: 节点 {node_id} 的洞察信息缺少字段 '{field}'，将使用默认值", file=sys.stderr)
                    if field == "key_points":
                        insight[field] = []
                    else:
                        insight[field] = ""
            
            # 验证 knowledge_graph（如果存在）
            if "knowledge_graph" in insight:
                kg = insight["knowledge_graph"]
                if not isinstance(kg, dict):
                    print(f"[LLM] 警告: 节点 {node_id} 的 knowledge_graph 不是字典类型，将移除", file=sys.stderr)
                    del insight["knowledge_graph"]
                else:
                    if "nodes" not in kg or "edges" not in kg:
                        print(f"[LLM] 警告: 节点 {node_id} 的 knowledge_graph 缺少 nodes 或 edges，将移除", file=sys.stderr)
                        del insight["knowledge_graph"]
        
        print("[LLM] 蓝图结构验证通过", file=sys.stderr)
        
    except (ValueError, json.JSONDecodeError) as e:
        print(f"[LLM] 蓝图解析或验证失败: {e}", file=sys.stderr)
        print(f"[LLM] 原始内容长度: {len(raw_content)} 字符", file=sys.stderr)
        print(f"[LLM] 原始内容前1000字符: {raw_content[:1000]}", file=sys.stderr)
        if len(raw_content) > 1000:
            print(f"[LLM] 原始内容后500字符: {raw_content[-500:]}", file=sys.stderr)
        raise

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
        f"[LLM] 调用模型分类: model={os.environ.get('MODEL_NAME', 'glm-4-flash')}, "
        f"task_snippet={task_description[:40]!r}",
        file=sys.stderr,
    )
    response = client.chat.completions.create(
        model=os.environ.get("MODEL_NAME", "glm-4-flash"),
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


