from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple


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


# 表1的 30 条测试项目 one-shot 场景。
SCENARIOS: List[Scenario] = [
    # 一、越野物流支援模型测试（1~6）
    Scenario(
        id="offroad_fleet_formation",  # 1. 任务编组
        model_name="越野物流",
        name="任务编组",
        example_input="向位置X运输资源Y，道路存在不确定损毁风险，要求Z小时内送达。",
        reasoning_chain="任务解析（运输、重量、时限、路况）→ 车辆类型匹配（选择中型越野无人车，理由：载重能力与地形适应性）→ 数量计算（基于单车载重和冗余要求推导车辆数量）→ 装载方案（物资分配与固定方式）",
        prompt=(
            "【越野物流-任务编组专项要求（详细输出版）】\n"
            "\n"
            "=== 一、行为树结构要求 ===\n"
            "1. 行为树必须至少包含以下核心节点，且严格按照推理链条自上而下展开：\n"
            "   - task_analysis（任务分析与规划，根节点）：\n"
            "       * 明确目的地、货物类型与重量、时间限制、道路条件（泥泞/碎石/损毁风险等）、安全要求；\n"
            "       * 至少拆分出\"任务要素提取\"和\"约束条件识别\"两个子层级节点；\n"
            "   - route_analysis（路线风险评估）：\n"
            "       * 至少包含 terrain_scan（地形扫描）和 risk_assessment（风险评估）两个子节点；\n"
            "   - fleet_formation（车队编成推理结果，核心决策节点）：\n"
            "       * 下方必须细化出 vehicle_selection（车辆类型匹配）、quantity_calculation（数量计算）、loading_plan（装载方案）三个子节点；\n"
            "       * 该节点必须包含 knowledge_graph 字段。\n"
            "\n"
            "2. behavior_tree 中每个节点的格式要求：\n"
            "   - label 字段：必须包含具体数值结果，格式示例：\"🚛 任务编组：2辆中型越野无人车运输资源Y\"、\"✅ 车队编成结果：2辆中型越野无人车\"、\"✅ 数量计算：2辆\"；\n"
            "   - summary 字段：必须包含具体数值、时间、比例等量化信息，不能使用空泛描述。例如：\n"
            "     * 正确示例：\"在2小时时限与道路损毁风险约束下，选择2辆中型越野无人车运输资源Y，其中车辆1装载60%，车辆2装载40%作为冗余备份。\"\n"
            "     * 错误示例：\"选择合适的车辆进行运输\"（过于空泛，缺少具体数值）\n"
            "\n"
            "=== 二、knowledge_graph 要求 ===\n"
            "fleet_formation 节点的 knowledge_graph 必须体现完整因果链路：\n"
            "任务解析(task_parsing) → 车辆匹配(vehicle_matching) → 数量计算(quantity_calc) → 装载方案(loading_scheme) → 最终配置(fleet_config)\n"
            "\n"
            "具体要求：\n"
            "- nodes[].label 必须包含具体参数信息，格式：\"节点名称(具体参数1, 具体参数2, ...)\"\n"
            "  示例：\"任务解析(位置X, 资源Y, 2小时, 道路损毁风险)\"、\"数量计算(2辆, 含20%冗余)\"、\"装载方案(1车60%,1车40%)\"\n"
            "- nodes[].type 必须明确标注：input（输入）、process（处理）、decision（决策）、output（输出）\n"
            "- edges 必须明确表示推理方向，连接所有相关节点\n"
            "\n"
            "=== 三、node_insights 详细要求 ===\n"
            "为 behavior_tree 中出现的每一个节点（包括所有子节点）提供详细的 node_insights，每个节点包含：\n"
            "\n"
            "1. title：节点标题（简洁明确）\n"
            "\n"
            "2. summary：\n"
            "   - 具体数值（如：2小时、2辆、60%、50kg等）\n"
            "   - 具体对象（如：位置X、资源Y、中型越野无人车等）\n"
            "   - 具体约束条件（如：道路损毁风险、20%冗余等）\n"
            "   - 不能使用\"合适的\"、\"一定的\"、\"若干\"等模糊词汇\n"
            "\n"
            "3. key_points：3-5条关键要点，每条必须：\n"
            "   - 包含具体数值或计算过程\n"
            "   - 对于计算类节点（vehicle_selection、quantity_calculation、loading_plan、fleet_formation），必须包含：\n"
            "     * 计算假设（如：\"假定单车载重能力约50kg\"、\"增加20%冗余\"）\n"
            "     * 计算公式或推理步骤（如：\"计算理论最少车辆数量 = 资源总量 ÷ 单车载重\"）\n"
            "     * 具体结果（如：\"向上取整得到2辆车\"）\n"
            "     * 验证条件（如：\"验证在一辆车失效情况下仍能在2小时内完成运输\"）\n"
            "   - 每条 key_point 应该是一个完整的、可独立理解的句子，避免过于简短的短语\n"
            "\n"
            "4. knowledge_trace：知识追踪路径，必须：\n"
            "   - 使用箭头（→）连接各个推理步骤\n"
            "   - 包含具体的输入、处理过程、输出结果\n"
            "   - 体现完整的推理链条，格式示例：\"任务文本解析 → 目的地/货物/时间/路况要素抽取 → 形成可供后续节点复用的标准任务描述。\"\n"
            "   - 对于核心决策节点，knowledge_trace 应该体现：输入要素 → 中间推理步骤 → 最终输出结果\n"
            "\n"
            "=== 四、核心节点的特殊要求 ===\n"
            "对以下四个节点（vehicle_selection、quantity_calculation、loading_plan、fleet_formation），必须提供可用于教学展示的详细计算/推理细节：\n"
            "\n"
            "- vehicle_selection：\n"
            "  * key_points 中必须包含：单车载重假设（如\"约50kg\"）、车辆类型选择理由（如\"越野悬挂与轮胎/履带设计适配泥泞与损毁混合路段\"）、可靠性考虑\n"
            "\n"
            "- quantity_calculation：\n"
            "  * key_points 中必须包含：计算公式（如\"理论最少车辆数量 = 资源总量 ÷ 单车载重\"）、冗余比例（如\"20%冗余\"）、向上取整逻辑、故障场景验证\n"
            "\n"
            "- loading_plan：\n"
            "  * key_points 中必须包含：具体装载比例（如\"1车60%，1车40%\"）、主/备功能划分理由、重量平衡考虑、内部固定方式\n"
            "\n"
            "- fleet_formation：\n"
            "  * summary 和 key_points 必须整合上述三个子节点的结果，形成完整的编队方案\n"
            "  * knowledge_trace 必须体现：\"任务与路况要素 → 车辆类型筛选 → 数量与冗余计算 → 装载比例设计 → 形成最终车队编成方案\"\n"
            "\n"
            "=== 五、输出质量检查清单 ===\n"
            "生成内容后，请确保：\n"
            "□ 行为树至少包含两层结构（根节点有子节点，且至少一个子节点有子节点）\n"
            "□ 至少有一个 node_insights 内的节点包含 knowledge_graph\n"
            "□ 所有 label 包含 emoji 和具体数值\n"
            "□ 所有 summary 包含具体数值而非空泛描述\n"
            "□ 所有 key_points 包含计算过程或具体参数\n"
            "□ 所有 knowledge_trace 使用箭头连接且包含具体步骤\n"
            "□ knowledge_graph 的 nodes label 包含参数信息\n"
            "□ 核心决策节点包含完整的推理细节"
        ),
        example_output={
            "default_focus": "fleet_formation",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "🚛 任务编组：2辆中型越野无人车运输资源Y",
                "status": "completed",
                "summary": "解析任务：在2小时内，将资源Y从当前位置运输至位置X，道路存在不确定损毁风险，需要形成具备冗余能力的越野车队编组方案。",
                "children": [
                    {
                        "id": "route_analysis",
                        "label": "路线风险评估",
                        "status": "completed",
                        "summary": "综合评估前往位置X可能遇到的道路损毁、高风险路段等因素，为后续车辆选择与装载方案提供约束条件。",
                        "children": [
                            {
                                "id": "terrain_scan",
                                "label": "地形扫描",
                                "status": "completed",
                                "summary": "扫描前往位置X沿途的坡度、土壤与障碍物分布，标注潜在陷车与侧翻区域。",
                                "children": []
                            },
                            {
                                "id": "risk_assessment",
                                "label": "风险评估",
                                "status": "completed",
                                "summary": "基于地形与道路损毁信息，估计通行成功率与备选绕行路径，为车队编组提供安全边界。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "fleet_formation",
                        "label": "✅ 车队编成结果：2辆中型越野无人车",
                        "status": "active",
                        "summary": "在2小时时限与道路损毁风险约束下，选择2辆中型越野无人车运输资源Y，其中车辆1装载60%，车辆2装载40%作为冗余备份。",
                        "children": [
                            {
                                "id": "vehicle_selection",
                                "label": "✅ 车辆类型匹配：中型越野无人车",
                                "status": "completed",
                                "summary": "车辆具备约50kg 级载重与越野悬挂能力，适应碎石与损毁混合路段。",
                                "children": []
                            },
                            {
                                "id": "quantity_calculation",
                                "label": "✅ 数量计算：2辆",
                                "status": "completed",
                                "summary": "根据资源Y总重量与单车载重能力，叠加20% 冗余，推导至少需要2辆车以保证任务完成与故障备份。",
                                "children": []
                            },
                            {
                                "id": "loading_plan",
                                "label": "✅ 装载方案：1车60%，1车40%",
                                "status": "completed",
                                "summary": "车辆1承担主运输负载，车辆2作为冗余与补充载荷，兼顾重量平衡与故障冗余。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "execution_plan",
                        "label": "执行方案",
                        "status": "pending",
                        "summary": "在满足2小时内送达的前提下，编制发车时间、途中检查点与返程预案。",
                        "children": [
                            {
                                "id": "route_optimization",
                                "label": "路线优化",
                                "status": "pending",
                                "summary": "在可选路径中优选兼顾时间与安全性的路线，必要时预留一条备选绕行路径。",
                                "children": []
                            },
                            {
                                "id": "schedule_arrangement",
                                "label": "调度安排",
                                "status": "pending",
                                "summary": "结合2小时时限与路况风险，确定发车时间、行驶速度与途中安全检查节奏。",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务分析与规划",
                    "summary": "对“向位置X运输资源Y，道路存在不确定损毁风险，要求2小时内送达”的任务进行结构化解析，明确目的地、货物、时间与路况约束。",
                    "key_points": [
                        "抽取任务要素：位置X、资源Y、2小时时限、不确定道路损毁风险",
                        "区分硬性约束（时限、安全）与软性约束（舒适性、效率）",
                        "为路线评估与车队编成提供统一的数据输入框架"
                    ],
                    "knowledge_trace": "任务文本解析 → 目的地/货物/时间/路况要素抽取 → 形成可供后续节点复用的标准任务描述。"
                },
                "route_analysis": {
                    "title": "路线风险评估",
                    "summary": "围绕道路不确定损毁风险，综合分析前往位置X的路线条件与潜在危险点。",
                    "key_points": [
                        "基于历史地图与实时侦察信息识别可能损毁路段",
                        "将坡度、路面附着系数等转化为通行成功率指标",
                        "为车辆选择与数量冗余计算提供风险输入参数"
                    ],
                    "knowledge_trace": "地形数据与侦察信息融合 → 风险因子量化 → 向车队编成节点输出风险等级。"
                },
                "terrain_scan": {
                    "title": "地形扫描",
                    "summary": "利用卫星影像、先验地图与传感器数据获取路段坡度、凹凸度与障碍分布。",
                    "key_points": [
                        "读取位置X周边的多源地形/路况数据",
                        "对泥泞、碎石、塌陷等路面特征进行分类标注",
                        "形成用于车辆适应性评估的地形剖面"
                    ],
                    "knowledge_trace": "数据采集 → 特征提取 → 生成可视化地形剖面供风险评估与车辆匹配使用。"
                },
                "risk_assessment": {
                    "title": "风险评估",
                    "summary": "结合地形扫描结果与任务时限，估计不同路径的陷车概率与通过时间区间。",
                    "key_points": [
                        "为各路段打分：通行难度、潜在损毁程度、绕行成本",
                        "识别必须避开的高风险区段并标注为禁行",
                        "输出候选主路线与备选路线，为后续编队与调度提供依据"
                    ],
                    "knowledge_trace": "路段评分 → 组合成路径方案 → 筛选主备路线并输出给车队编成与执行方案节点。"
                },
                "fleet_formation": {
                    "title": "车队编成推理结果",
                    "summary": "在2小时时限与道路损毁风险约束下，选择2辆中型越野无人车并给出主/备装载方案，保证任务完成与故障冗余。",
                    "key_points": [
                        "在车辆类型候选集中筛选具备越野能力与稳定性的中型平台",
                        "基于资源Y重量、单车载重与20%冗余假设推导出2辆车配置",
                        "制定“1车60%+1车40%”的装载比例以兼顾利用率与故障冗余"
                    ],
                    "knowledge_trace": "任务与路况要素 → 车辆类型筛选 → 数量与冗余计算 → 装载比例设计 → 形成最终车队编成方案。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "task_parsing", "label": "任务解析(位置X, 资源Y, 2小时, 道路损毁风险)", "type": "input"},
                            {"id": "vehicle_matching", "label": "车辆匹配(中型越野无人车)", "type": "process"},
                            {"id": "quantity_calc", "label": "数量计算(2辆, 含20%冗余)", "type": "process"},
                            {"id": "loading_scheme", "label": "装载方案(1车60%,1车40%)", "type": "decision"},
                            {"id": "fleet_config", "label": "最终配置(2辆中型越野无人车)", "type": "output"}
                        ],
                        "edges": [
                            {"source": "task_parsing", "target": "quantity_calc"},
                            {"source": "vehicle_matching", "target": "quantity_calc"},
                            {"source": "quantity_calc", "target": "loading_scheme"},
                            {"source": "loading_scheme", "target": "fleet_config"}
                        ]
                    }
                },
                "vehicle_selection": {
                    "title": "车辆类型匹配",
                    "summary": "在道路存在不确定损毁风险的情况下，选择具备越野能力的中型无人车作为运输平台。",
                    "key_points": [
                        "假定单车载重能力约50kg，满足资源Y总重量需求",
                        "越野悬挂与轮胎/履带设计适配泥泞与损毁混合路段",
                        "考虑可靠性与维护便利性，优先选用成熟型号"
                    ],
                    "knowledge_trace": "路况与载重需求 → 候选车型能力对比 → 选定中型越野无人车作为基准平台。"
                },
                "quantity_calculation": {
                    "title": "数量计算",
                    "summary": "依据资源Y总重量、单车载重与20% 冗余要求，推导需要2辆车以保证运输成功与故障备份。",
                    "key_points": [
                        "计算理论最少车辆数量 = 资源总量 ÷ 单车载重",
                        "在理论最少基础上增加20%冗余，向上取整得到2辆车",
                        "验证在一辆车失效情况下仍能在2小时内完成运输"
                    ],
                    "knowledge_trace": "载重需求建模 → 理论车辆数计算 → 加入冗余系数并验证任务完成可能性。"
                },
                "loading_plan": {
                    "title": "装载方案",
                    "summary": "将资源Y按60%/40%划分至两辆车，以提升故障冗余与重量平衡。",
                    "key_points": [
                        "车辆1作为主运输载具，承担约60% 货物以提高利用率",
                        "车辆2承担40% 货物，兼具补充运输与故障接替功能",
                        "在每辆车内部按照重心与绑扎要求进行分层固定"
                    ],
                    "knowledge_trace": "资源总量与车辆数量 → 主/备功能划分 → 按比例分配并结合车体结构设计装载细节。"
                },
                "execution_plan": {
                    "title": "执行方案",
                    "summary": "围绕“2小时内到达位置X”的目标制定发车节奏、途中检查点与返程路径预案。",
                    "key_points": [
                        "根据路径长度与路况估算行驶时间与安全余量",
                        "设置关键路段的减速检查与通信打点",
                        "规划返程路径与途中补给/维护节点"
                    ],
                    "knowledge_trace": "时间约束与路径评估 → 行程与检查点规划 → 形成可执行的任务时间表。"
                },
                "route_optimization": {
                    "title": "路线优化",
                    "summary": "在安全前提下尽量压缩行程时间，同时预留绕行能力。",
                    "key_points": [
                        "比较多条可行路线的时间消耗与风险等级",
                        "对高风险路段设置备选绕行路径",
                        "将路线决策结果传递给调度与驾驶控制模块"
                    ],
                    "knowledge_trace": "多路径评估 → 主路线选择 → 备选绕行策略绑定。"
                },
                "schedule_arrangement": {
                    "title": "调度安排",
                    "summary": "在2小时时限内合理安排发车时间与途中停靠检查节奏，保证安全与准时兼顾。",
                    "key_points": [
                        "预留装载与出发前检查时间窗口",
                        "将关键路段通过时间与检查点事件写入时间表",
                        "为延误或路况突变预留时间缓冲区"
                    ],
                    "knowledge_trace": "时间约束与路径计划 → 细化为时间节点与事件列表 → 下发至执行单元进行调度控制。"
                }
            }
        },
    ),
    Scenario(
        id="offroad_dynamic_routing",  # 2. 动态路径规划与重规划
        model_name="越野物流",
        name="动态路径规划与重规划",
        example_input="向X位置运输资源Y，道路可能受损",
        reasoning_chain="路径规划（读取地图与路况信息生成初始路径）→ 异常感知与处理（感知数据异常，派遣无人机/机器狗抵近观察）→ 路径重规划（综合车队状态、地图与异常信息重新规划可行路径）",
        prompt=(
            "【越野物流-动态路径规划与重规划专项要求（粒度强化版）】\n"
            "1. 行为树必须包含以下核心节点：\n"
            "   - task_analysis（任务解析）：\n"
            "       * 明确目的地X、资源Y与时间/安全等基础约束；\n"
            "   - route_planning（初始路径规划）：\n"
            "       * 至少细分出 path_generation（路径生成）与 path_evaluation（路径评估）两个子节点；\n"
            "   - anomaly_detection（异常感知与处理）：\n"
            "       * 体现感知数据异常→触发无人机/机器狗抵近观察→回传异常信息的链条；\n"
            "   - route_replanning（路径重规划，核心决策节点）：\n"
            "       * 综合初始路径、异常信息、车队状态重新生成新路径，必须包含 knowledge_graph 字段。\n"
            "2. route_replanning 节点的 knowledge_graph 必须体现：\n"
            "   初始路径(initial_route) → 异常感知(anomaly_detection) → 环境评估(env_assessment) → 路径优化(route_optimization) → 新路径生成(new_route)。\n"
            "3. node_insights 要求：\n"
            "   - 对 anomaly_detection、route_replanning 详细描述触发条件、传感器类型、决策依据与新旧路径对比要点；\n"
            "   - knowledge_trace 需完整刻画“初始规划 → 异常发现 → 信息补充 → 重规划”四段式逻辑。"
        ),
        example_output={
            "default_focus": "route_replanning",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "🚛 任务解析：前往X位置运输资源Y",
                "status": "completed",
                "summary": "解析任务：向位置X运输资源Y，道路可能受损，需要具备动态路径调整能力的越野运输方案。",
                "children": [
                    {
                        "id": "route_planning",
                        "label": "初始路径规划",
                        "status": "completed",
                        "summary": "基于地图与既有路况信息生成一条可行的初始路径，并评估时间与风险等级。",
                        "children": [
                            {
                                "id": "path_generation",
                                "label": "路径生成",
                                "status": "completed",
                                "summary": "从当前位置到位置X自动生成若干候选路径。",
                                "children": []
                            },
                            {
                                "id": "path_evaluation",
                                "label": "路径评估",
                                "status": "completed",
                                "summary": "综合距离、预计时间与已知受损路段对候选路径打分，选出初始主路径。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "anomaly_detection",
                        "label": "异常感知与处理",
                        "status": "active",
                        "summary": "在执行过程中实时监控道路受损、障碍物与天气变化，必要时派遣无人机/机器狗抵近观察并回传细节。",
                        "children": [],
                        "control_meta": {
                            "control_type": "decentralized_rl",
                            "agent_scope": ["convoy_vehicles", "uav_units", "ugv_dog_units"],
                            "policy_id": "offroad_anomaly_probe_pi",
                            "algo_family": "DTDE_consistency_AC",
                            "training_scenario": "offroad_dynamic_routing"
                        }
                    },
                    {
                        "id": "route_replanning",
                        "label": "路径重规划",
                        "status": "pending",
                        "summary": "融合初始路径、异常感知结果与车队状态，对原路径进行调整或重新规划生成新路径。",
                        "children": [],
                        "control_meta": {
                            "control_type": "decentralized_rl",
                            "agent_scope": ["convoy_vehicles"],
                            "policy_id": "offroad_route_replanning_pi",
                            "algo_family": "DTDE_consistency_AC",
                            "training_scenario": "offroad_dynamic_routing"
                        }
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务解析",
                    "summary": "明确任务目标为“将资源Y运输至位置X”，道路可能受损，对路径规划提出安全与鲁棒性要求。",
                    "key_points": [
                        "识别目的地X与货物Y等核心任务参数",
                        "将“道路可能受损”转化为路径可靠性约束",
                        "为后续路径规划与异常感知模块提供统一任务上下文"
                    ],
                    "knowledge_trace": "任务文本 → 目的地与货物抽取 → 风险约束建模 → 输出给路径规划与异常感知节点。"
                },
                "route_planning": {
                    "title": "初始路径规划",
                    "summary": "在任务开始前生成一条时间与安全性均可接受的初始运输路径。",
                    "key_points": [
                        "利用地图数据和历史路况生成多条候选路径",
                        "对每条路径计算距离、预计时间与已知风险权重",
                        "选择综合评分最高的路径作为主路径，并记录可行备选路径"
                    ],
                    "knowledge_trace": "候选路径生成 → 指标计算与加权 → 主/备路径筛选。"
                },
                "path_generation": {
                    "title": "路径生成",
                    "summary": "基于拓扑路网结构从起点到位置X生成若干连通路径。",
                    "key_points": [
                        "在路网图上搜索多条从起点到X的连通路径",
                        "剔除明显不可行或超出任务时限的路径",
                        "保留满足基本约束的路径集合供评估模块使用"
                    ],
                    "knowledge_trace": "路网拓扑 → 多路径搜索 → 过滤不可行路径并输出候选集。"
                },
                "path_evaluation": {
                    "title": "路径评估",
                    "summary": "对候选路径进行距离、时间与损毁风险打分，输出排序结果。",
                    "key_points": [
                        "计算每条路径的总距离与预计行驶时间",
                        "叠加历史损毁记录与已知障碍物信息形成风险得分",
                        "按综合评分排序，选出主路径与若干备选路径"
                    ],
                    "knowledge_trace": "指标计算 → 加权打分 → 主/备路径排序输出。"
                },
                "anomaly_detection": {
                    "title": "异常感知与处理",
                    "summary": "在任务执行中持续监听传感器与外部情报，一旦发现异常路段，触发抵近观察与路径重评估。",
                    "key_points": [
                        "监控激光雷达、视觉与惯性导航数据的异常模式",
                        "当检测到严重受损或阻断迹象时，发起无人机/机器狗抵近侦察",
                        "将实测路况与原始地图对比，更新路段通行状态"
                    ],
                    "knowledge_trace": "在线监控 → 异常触发 → 抵近观察 → 通行状态更新并通知重规划模块；关键探查与机动动作由去中心化RL策略 offroad_anomaly_probe_pi 在车队与无人机/机器狗智能体上本地生成。"
                },
                "route_replanning": {
                    "title": "路径重规划",
                    "summary": "结合初始路径、异常感知结果与车队剩余时间/油量等状态，生成新的最优路径或启用备选路径。",
                    "key_points": [
                        "将异常阻断路段标记为禁行或高代价边",
                        "在更新后的路网中重新执行路径搜索与评估",
                        "比较新路径与原路径的时间与风险差异，形成调整建议"
                    ],
                    "knowledge_trace": "路网状态更新 → 新路径搜索与评估 → 新旧路径对比 → 输出重规划结果并同步给执行控制；新路径及对应速度/机动方案由去中心化RL策略 offroad_route_replanning_pi 在各车队车辆智能体上分布式计算。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "initial_route", "label": "初始路径", "type": "input"},
                            {"id": "anomaly_detection", "label": "异常感知结果", "type": "input"},
                            {"id": "env_assessment", "label": "环境评估与路网更新", "type": "process"},
                            {"id": "route_optimization", "label": "路径优化决策", "type": "decision"},
                            {"id": "new_route", "label": "新路径生成", "type": "output"}
                        ],
                        "edges": [
                            {"source": "initial_route", "target": "env_assessment"},
                            {"source": "anomaly_detection", "target": "env_assessment"},
                            {"source": "env_assessment", "target": "route_optimization"},
                            {"source": "route_optimization", "target": "new_route"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="offroad_cargo_monitor",  # 3. 货物状态监控
        model_name="越野物流",
        name="货物状态监控与保全",
        example_input="向X位置运输冷冻食品Y",
        reasoning_chain="货物运输要求（温度等约束）→ 车辆匹配（选择具备温度传感器和保温/制冷能力的车辆）→ 异常感知与处理（设定温度采集频率，登记并上报温度异常，触发保全策略）",
        prompt=(
            "【越野物流-货物状态监控与保全专项要求（粒度强化版）】\n"
            "1. 行为树必须包含：\n"
            "   - task_analysis（任务解析）：解析“冷冻食品Y”对温度、湿度、震动的要求；\n"
            "   - vehicle_matching（车辆匹配）：细化为传感器配置、制冷/保温能力匹配等子要点；\n"
            "   - monitoring_setup（监控设置）：必须明确采样频率、告警阈值、上报周期；\n"
            "   - anomaly_handling（异常感知与处理，核心决策节点）：实时监控温度/震动等参数并触发保全策略，必须包含 knowledge_graph。\n"
            "2. anomaly_handling 节点的 knowledge_graph 必须体现：\n"
            "   状态监测(status_monitoring) → 异常识别(anomaly_detection) → 风险评估(risk_assessment) → 保全策略(preservation_strategy) → 执行响应(action_response)。\n"
            "3. node_insights 要求：\n"
            "   - 对监控参数设置、告警阈值设计与保全动作（调温、减速、改道、紧急停车等）进行条目化说明；\n"
            "   - knowledge_trace 体现“持续监控 → 及时告警 → 策略选择 → 行动闭环”的全过程。"
        ),
        example_output={
            "default_focus": "anomaly_handling",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "🚛 任务解析：向X位置运输冷冻食品Y",
                "status": "completed",
                "summary": "解析冷冻食品Y的运输要求：保持在规定低温区间，尽量避免剧烈震动，确保全程冷链不中断。",
                "children": [
                    {
                        "id": "vehicle_matching",
                        "label": "车辆匹配",
                        "status": "completed",
                        "summary": "选择具备冷链仓、温度传感器与基础减震能力的越野运输车辆。",
                        "children": []
                    },
                    {
                        "id": "monitoring_setup",
                        "label": "监控设置",
                        "status": "completed",
                        "summary": "配置温度与震动传感器采样频率、告警阈值与上报策略。",
                        "children": []
                    },
                    {
                        "id": "anomaly_handling",
                        "label": "异常感知与处理",
                        "status": "active",
                        "summary": "实时监测冷链仓温度和运输震动情况，一旦异常立即触发保全策略并记录闭环结果。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务解析",
                    "summary": "将“向X位置运输冷冻食品Y”拆解为温度控制、震动限制与时效约束三个关键方面。",
                    "key_points": [
                        "识别冷冻食品Y对温度区间的严格约束（如 -18℃ 以下）",
                        "考虑越野路面带来的震动风险对包装与产品质量的影响",
                        "评估运输时长对冷链设备持续工作的要求"
                    ],
                    "knowledge_trace": "货物属性分析 → 约束条件抽取 → 形成冷链运输任务配置。"
                },
                "vehicle_matching": {
                    "title": "车辆匹配",
                    "summary": "在可用车辆中选择具备冷链舱、温度传感器与适度减震能力的越野平台。",
                    "key_points": [
                        "筛选具备密闭冷链舱与独立制冷单元的车辆",
                        "确保车体具备足够的悬挂行程以降低越野震动",
                        "确认电源与制冷能力可以覆盖任务全程"
                    ],
                    "knowledge_trace": "货物冷链需求 → 车辆配置筛查 → 选定满足温控与减震能力的车辆。"
                },
                "monitoring_setup": {
                    "title": "监控设置",
                    "summary": "为冷链仓配置温度与震动监控方案，设置采样频率与多级告警阈值。",
                    "key_points": [
                        "设定温度传感器高/低阈值与连续超限判定时间窗",
                        "配置震动传感器的采样频率与峰值/均方根告警标准",
                        "定义正常上报周期与异常时的加密快速上报机制"
                    ],
                    "knowledge_trace": "监控参数设计 → 阈值与频率配置 → 与告警与上报逻辑绑定。"
                },
                "anomaly_handling": {
                    "title": "异常感知与处理",
                    "summary": "在发现温度或震动异常时，快速评估风险等级并触发调温、减速或停车等保全措施。",
                    "key_points": [
                        "对采集到的温度与震动数据进行实时阈值与趋势分析",
                        "根据偏差程度划分为预警、告警与紧急三类等级",
                        "针对不同等级执行调整制冷功率、降低车速或紧急停车检查等动作"
                    ],
                    "knowledge_trace": "状态监测 → 异常识别 → 风险分级 → 选择保全策略 → 执行动作并记录反馈。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "status_monitoring", "label": "状态监测(温度/震动)", "type": "input"},
                            {"id": "anomaly_detection", "label": "异常识别", "type": "process"},
                            {"id": "risk_assessment", "label": "风险评估", "type": "process"},
                            {"id": "preservation_strategy", "label": "保全策略选择", "type": "decision"},
                            {"id": "action_response", "label": "执行响应与记录", "type": "output"}
                        ],
                        "edges": [
                            {"source": "status_monitoring", "target": "anomaly_detection"},
                            {"source": "anomaly_detection", "target": "risk_assessment"},
                            {"source": "risk_assessment", "target": "preservation_strategy"},
                            {"source": "preservation_strategy", "target": "action_response"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="offroad_convoy_coordination",  # 4. 车队协同
        model_name="越野物流",
        name="车队协同与效率调度",
        example_input="向X位置运输4车食品和水",
        reasoning_chain="行进编队规划（依据道路宽度选择单列或并行队列）→ 协同动作管理（依据道路宽度组织依序掉头或队列整体倒置等动作）",
        prompt=(
            "【越野物流-车队协同与效率调度专项要求（粒度强化版）】\n"
            "1. 行为树必须包含：\n"
            "   - task_analysis（任务解析）：解析车队规模、货物类型、目的地与道路条件；\n"
            "   - formation_planning（行进编队规划）：根据道路宽度与安全距离选择单列/并行/分段编队方式；\n"
            "   - coordination_management（协同动作管理，核心决策节点）：规划依序掉头、队列整体倒置、紧急避让等动作，必须包含 knowledge_graph。\n"
            "2. coordination_management 节点的 knowledge_graph 必须体现：\n"
            "   编队规划(formation_planning) → 动作需求识别(action_requirement) → 协同策略(coordination_strategy) → 执行顺序(execution_sequence) → 状态同步(status_sync)。\n"
            "3. node_insights 要求：\n"
            "   - 对编队选择依据、协同动作触发条件、执行顺序与通信同步机制进行细致说明；\n"
            "   - knowledge_trace 描述“编队设计 → 动作需求 → 协同策略 → 执行与同步”的完整闭环。"
        ),
        example_output={
            "default_focus": "coordination_management",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "🚛 任务解析：向X位置运输4车食品和水",
                "status": "completed",
                "summary": "解析车队规模为4车，货物为食品与水，目标为安全高效抵达位置X，并在越野环境下保持队形稳定与协同顺畅。",
                "children": [
                    {
                        "id": "formation_planning",
                        "label": "行进编队规划",
                        "status": "completed",
                        "summary": "根据道路宽度与安全间距选择合适的单列或部分并行队列，确定车序与间距。",
                        "children": []
                    },
                    {
                        "id": "coordination_management",
                        "label": "协同动作管理",
                        "status": "active",
                        "summary": "针对掉头、超车、避障与通过狭窄路段等场景规划协同动作顺序与通信策略。",
                        "children": [],
                        "control_meta": {
                            "control_type": "decentralized_rl",
                            "agent_scope": ["vehicle_1", "vehicle_2", "vehicle_3", "vehicle_4"],
                            "policy_id": "convoy_coordination_pi",
                            "algo_family": "DTDE_consistency_AC",
                            "training_scenario": "offroad_convoy_coordination"
                        }
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务解析",
                    "summary": "将“向X位置运输4车食品和水”解析为多车协同行进任务，重点关注队形稳定与效率优化。",
                    "key_points": [
                        "识别车队规模为4车，货物类型为食品与水",
                        "结合路况推断是否存在狭窄路段与会车场景",
                        "提出“既要保障安全距离，又要控制整体用时”的调度目标"
                    ],
                    "knowledge_trace": "任务文本解析 → 车队规模与货物属性识别 → 协同与效率目标定义。"
                },
                "formation_planning": {
                    "title": "行进编队规划",
                    "summary": "根据道路宽度与安全间距要求，确定4车队列采用单列或局部并行的编队方式。",
                    "key_points": [
                        "估算道路宽度与会车可能性，判断是否允许并行队列",
                        "设计前后纵向间距以兼顾制动距离与通信链路稳定性",
                        "给出初始车序安排，如前车装载较轻、具备更强侦察能力"
                    ],
                    "knowledge_trace": "道路与安全约束 → 编队方式筛选 → 车序与间距配置。"
                },
                "coordination_management": {
                    "title": "协同动作管理",
                    "summary": "为4车队列规划在掉头、避障、通过狭窄路段等典型场景下的协同动作顺序与通信同步方案。",
                    "key_points": [
                        "识别需要协同的动作类型：依序掉头、整体倒置、紧急避让等，并为每辆车建立本地决策规则",
                        "各车辆基于自身局部感知与历史轨迹维护本地策略/值函数，通过车间通信交换关键信息",
                        "在分布式一致性更新后形成协同动作策略，并按既定顺序执行与状态同步"
                    ],
                    "knowledge_trace": "编队规划结果 → 各车本地策略与轨迹收集 → 分布式一致性聚合与去中心化策略更新 → 形成协同动作策略并执行与同步。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "formation_planning", "label": "编队规划结果", "type": "input"},
                            {"id": "local_policy_agents", "label": "各车本地策略 π_i / Q_i", "type": "process"},
                            {"id": "local_experience", "label": "本地轨迹与经验回放 D_i", "type": "process"},
                            {"id": "consensus_weight", "label": "分布式一致性权重估计 ω(τ)", "type": "process"},
                            {"id": "decentralized_update", "label": "去中心化策略更新(Actor–Critic)", "type": "process"},
                            {"id": "coordination_strategy", "label": "协同动作策略", "type": "process"},
                            {"id": "execution_sequence", "label": "协同行动执行顺序", "type": "decision"},
                            {"id": "status_sync", "label": "车队状态同步与反馈", "type": "output"}
                        ],
                        "edges": [
                            {"source": "formation_planning", "target": "local_policy_agents"},
                            {"source": "local_policy_agents", "target": "local_experience"},
                            {"source": "local_experience", "target": "consensus_weight"},
                            {"source": "consensus_weight", "target": "decentralized_update"},
                            {"source": "decentralized_update", "target": "coordination_strategy"},
                            {"source": "coordination_strategy", "target": "execution_sequence"},
                            {"source": "execution_sequence", "target": "status_sync"},
                            {"source": "status_sync", "target": "local_policy_agents"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="offroad_terrain_passability",  # 5. 复杂地形通行能力评估
        model_name="越野物流",
        name="复杂地形通行能力评估",
        example_input="需穿越泥泞与部分坍塌区域，将物资送至前线A点。",
        reasoning_chain="地形与障碍抽取（泥泞、坍塌、湿滑坡地）→ 通行风险判定（低速通过/需绕行）→ 车辆能力匹配（四驱越野车、履带式无人车）→ 策略生成（加设无人机侦察、选择坡度最小路径、通过速度限制）",
        prompt=(
            "【越野物流-复杂地形通行能力评估专项要求】\n"
            "1. 行为树必须至少包含以下核心节点：\n"
            "   - task_analysis（任务解析）：\n"
            "       * 从任务文本中抽取目的地、载荷、时间要求以及地形描述（山地、丘陵、泥泞、断路等）；\n"
            "   - terrain_obstacle_extraction（地形与障碍抽取）：\n"
            "       * 细化提取泥泞、坍塌、湿滑坡地、狭窄通道等要素，可拆为地形分类与障碍标注两个子层级；\n"
            "   - passability_risk_assessment（通行风险判定）：\n"
            "       * 根据坡度、附着系数、障碍密度等指标评估“可直接通过/需减速通过/需绕行/禁止通行”级别；\n"
            "   - vehicle_capability_matching（车辆能力匹配）：\n"
            "       * 在四驱越野车、履带式无人车等候选平台中匹配满足通过能力与安全冗余的配置；\n"
            "   - passability_strategy（通行策略生成，核心决策节点）：\n"
            "       * 综合前述信息生成通过或规避策略，必须包含 knowledge_graph 字段。\n"
            "2. passability_strategy 节点的 knowledge_graph 必须体现：\n"
            "   地形与障碍抽取(terrain_obstacle) → 通行风险判定(risk_level) → 车辆能力匹配(vehicle_capability) → 策略生成(pass_strategy) → 任务可行性结论(feasibility_conclusion)。\n"
            "3. 在 node_insights 中：\n"
            "   - 对各类典型地形（泥泞、坍塌、陡坡、碎石）给出通行判定依据；\n"
            "   - 说明为何选择四驱越野车或履带式无人车，以及在不同风险级别下的速度限制、侦察需求与绕行条件；\n"
            "   - knowledge_trace 需完整描绘“任务解析 → 地形/障碍建模 → 风险打分 → 车辆能力对比 → 通行/绕行策略输出”的推理路径。"
        ),
        example_output={
            "default_focus": "passability_strategy",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "🚛 任务解析：穿越泥泞与坍塌区域，补给前线A点",
                "status": "completed",
                "summary": "解析任务文本“需穿越泥泞与部分坍塌区域，将物资送至前线A点”，抽取目的地、物资类型、地形风险与大致时效要求，为通行评估提供上下文。",
                "children": [
                    {
                        "id": "terrain_obstacle_extraction",
                        "label": "地形与障碍抽取",
                        "status": "completed",
                        "summary": "从任务描述与先验地图中识别泥泞地段、局部坍塌、湿滑坡地与狭窄通道等关键障碍。",
                        "children": []
                    },
                    {
                        "id": "passability_risk_assessment",
                        "label": "通行风险判定",
                        "status": "completed",
                        "summary": "基于坡度、附着系数与障碍密度，对各路段进行通行等级与风险系数评估。",
                        "children": []
                    },
                    {
                        "id": "vehicle_capability_matching",
                        "label": "车辆能力匹配",
                        "status": "completed",
                        "summary": "在四驱越野轮式平台与履带式无人车等候选中，匹配满足通过能力与安全冗余的车辆方案。",
                        "children": []
                    },
                    {
                        "id": "passability_strategy",
                        "label": "✅ 通行策略生成与可行性结论",
                        "status": "active",
                        "summary": "综合地形障碍、风险等级与车辆能力，给出穿越/绕行策略、速度限制与侦察配置，并形成整体可行性结论。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务解析",
                    "summary": "围绕“需穿越泥泞与部分坍塌区域，将物资送至前线A点”的描述，提炼任务目标与地形风险。",
                    "key_points": [
                        "识别目的地为前线A点，任务性质为补给运输",
                        "从描述中抽取“泥泞”“部分坍塌”等地形风险关键词",
                        "推断对安全性与稳定性的要求高于速度需求"
                    ],
                    "knowledge_trace": "任务文本解析 → 目的地/任务类型抽取 → 地形风险要素识别 → 为后续地形与风险评估提供输入。"
                },
                "terrain_obstacle_extraction": {
                    "title": "地形与障碍抽取",
                    "summary": "结合地图、侦察信息与任务文本，将泥泞区、坍塌段、湿滑坡地等转化为结构化障碍信息。",
                    "key_points": [
                        "从自然语言描述和地理数据中识别泥泞、坍塌、陡坡等标签",
                        "估计各障碍段的长度、宽度与分布位置",
                        "为每类障碍关联典型物理特性（附着系数、承载力等）"
                    ],
                    "knowledge_trace": "任务与地图数据 → 障碍特征提取与分类 → 形成可用于评分的地形/障碍集合。"
                },
                "passability_risk_assessment": {
                    "title": "通行风险判定",
                    "summary": "基于坡度、附着系数和障碍密度，对每个路段给出通行等级与风险系数。",
                    "key_points": [
                        "对坡度大、承载力低的路段标记为“高风险或禁止通行”",
                        "对中等风险路段建议采取减速或单车分步通过策略",
                        "为每个路段计算通行成功率与陷车/侧翻概率"
                    ],
                    "knowledge_trace": "地形/障碍集合 → 指标量化与打分 → 输出通行等级与风险系数。"
                },
                "vehicle_capability_matching": {
                    "title": "车辆能力匹配",
                    "summary": "将各候选车辆的越野能力与地形风险相匹配，筛选出可通过或可在策略辅助下通过的配置。",
                    "key_points": [
                        "对比四驱轮式与履带式平台的通过高度、附着系数容忍度与抗陷车能力",
                        "结合车辆自重、载荷与底盘高度评估通过坍塌边缘与泥泞段的安全裕度",
                        "在必要时建议配置救援/拖拽能力作为冗余保障"
                    ],
                    "knowledge_trace": "车辆能力参数表 → 与路段风险指标对齐 → 输出适配车辆组合及其安全裕度说明。"
                },
                "passability_strategy": {
                    "title": "通行策略生成",
                    "summary": "在匹配好的车辆与风险评估结果基础上，生成包含通过/绕行选择、速度限制与侦察配置的综合策略。",
                    "key_points": [
                        "对可控风险路段给出限速通过与车距控制建议",
                        "对高风险或未知路段配置无人机/机器人先行侦察并评估是否绕行",
                        "形成整体路径通行可行性结论，并标注关键危险点与应急预案"
                    ],
                    "knowledge_trace": "风险等级 + 车辆能力 → 路段级策略（通过/减速/绕行） → 汇总为全程通行方案与任务可行性结论。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "terrain_obstacle", "label": "地形与障碍抽取结果", "type": "input"},
                            {"id": "risk_level", "label": "通行风险判定(等级+系数)", "type": "process"},
                            {"id": "vehicle_capability", "label": "车辆能力匹配", "type": "process"},
                            {"id": "pass_strategy", "label": "通行/绕行策略生成", "type": "decision"},
                            {"id": "feasibility_conclusion", "label": "任务可行性结论", "type": "output"}
                        ],
                        "edges": [
                            {"source": "terrain_obstacle", "target": "risk_level"},
                            {"source": "risk_level", "target": "vehicle_capability"},
                            {"source": "vehicle_capability", "target": "pass_strategy"},
                            {"source": "pass_strategy", "target": "feasibility_conclusion"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="offroad_time_energy_estimation",  # 6. 任务耗时与能耗预测
        model_name="越野物流",
        name="任务耗时与能耗预测",
        example_input="运输 400kg 物资至 12km 外的山区前线，道路泥泞且有连续上下坡。",
        reasoning_chain="载重与坡度解析 → 单位距离能耗估计 → 任务总行程预测 → 能耗模型推理（考虑低温、湿滑导致能耗增加）→ 输出总耗时预测与补能需求（如需中途更换电池或安排补给车辆）",
        prompt=(
            "【越野物流-任务耗时与能耗预测专项要求】\n"
            "1. 行为树必须至少包含以下核心节点：\n"
            "   - task_analysis（任务解析）：解析运输距离、载重400kg、道路泥泞与连续上下坡、温度等环境因素；\n"
            "   - load_slope_analysis（载重与坡度解析）：将载重、坡度分布与路面附着条件转化为分段阻力与能耗因子；\n"
            "   - unit_energy_estimation（单位距离能耗估计）：基于车辆动力学模型与经验参数估算不同路段的单位距离能耗；\n"
            "   - mission_profile_estimation（任务总行程预测）：综合有效速度、停靠/减速段与坡度影响，预测总行程时间；\n"
            "   - energy_time_inference（能耗与耗时推理，核心决策节点）：\n"
            "       * 综合载重、坡度、温度和路况对能耗的影响，给出总能耗与耗时预测，并生成补能/补给建议，必须包含 knowledge_graph 字段。\n"
            "2. energy_time_inference 节点的 knowledge_graph 必须体现：\n"
            "   载重与坡度解析(load_slope_profile) → 单位距离能耗(unit_energy) → 行程时间预测(travel_time) → 总能耗推理(total_energy) → 补能与补给建议(resupply_plan)。\n"
            "3. 在 node_insights 中：\n"
            "   - 说明如何根据坡度、泥泞程度与温度对单位能耗进行修正；\n"
            "   - 给出电池容量或油箱容量与预测总能耗之间的对比，并推导是否需要中途补能或补给车辆；\n"
            "   - knowledge_trace 体现“任务与环境解析 → 分段能耗与速度估计 → 累积行程与总能耗 → 补能/补给策略生成”的完整链路。"
        ),
        example_output={
            "default_focus": "energy_time_inference",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "🚛 任务解析：400kg 越野运输至12km 山区前线",
                "status": "completed",
                "summary": "解析“运输 400kg 物资至 12km 外的山区前线，道路泥泞且有连续上下坡”任务，明确载重、距离、路况与环境因素。",
                "children": [
                    {
                        "id": "load_slope_analysis",
                        "label": "载重与坡度解析",
                        "status": "completed",
                        "summary": "将400kg载重与12km路线的坡度分布、泥泞程度转化为分段阻力与附加能耗因子。",
                        "children": []
                    },
                    {
                        "id": "unit_energy_estimation",
                        "label": "单位距离能耗估计",
                        "status": "completed",
                        "summary": "基于车辆动力学与经验模型，估算在不同坡度与路况下的单位距离能耗。",
                        "children": []
                    },
                    {
                        "id": "mission_profile_estimation",
                        "label": "任务总行程预测",
                        "status": "completed",
                        "summary": "综合可行平均速度、减速路段与坡度影响，预测总行程时间与速度剖面。",
                        "children": []
                    },
                    {
                        "id": "energy_time_inference",
                        "label": "✅ 能耗与耗时推理与补能建议",
                        "status": "active",
                        "summary": "在分段能耗与时间预测基础上，给出任务总能耗与总耗时，并生成是否需要中途补能或补给车辆的建议。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务解析",
                    "summary": "从任务文本中提取运输距离12km、载重400kg以及“泥泞”“连续上下坡”等关键约束。",
                    "key_points": [
                        "识别任务为中等距离的山区越野补给任务",
                        "将“泥泞”和“连续上下坡”转化为滚动阻力与爬坡阻力增加的因素",
                        "推断任务对能耗与时间的不确定性较大，需要保守估计与冗余"
                    ],
                    "knowledge_trace": "任务文本 → 距离/载重/路况要素提取 → 为后续能耗与耗时建模提供输入。"
                },
                "load_slope_analysis": {
                    "title": "载重与坡度解析",
                    "summary": "根据线路高度剖面与路面状况，将12km路线划分为若干坡度区间，并结合400kg载重计算分段阻力。",
                    "key_points": [
                        "基于地形数据得到爬坡、下坡和平路区段的比例与平均坡度",
                        "在泥泞路段上设置更高的滚动阻力与打滑损耗系数",
                        "将载重与坡度共同映射为每个区段的牵引力和能耗需求因子"
                    ],
                    "knowledge_trace": "高度剖面 + 路况标签 → 分段坡度与路面模型 → 输出 load_slope_profile。"
                },
                "unit_energy_estimation": {
                    "title": "单位距离能耗估计",
                    "summary": "结合车辆动力系统效率、载重与环境温度，对不同区段的单位距离能耗进行估算。",
                    "key_points": [
                        "根据车辆参数设定基准单位能耗（如kWh/km或L/km）",
                        "在上坡与泥泞区段叠加额外能耗系数，在下坡利用能量回收或滑行降低净能耗",
                        "考虑低温导致电池效率下降或油耗增加，对整体单位能耗进行修正"
                    ],
                    "knowledge_trace": "基准能耗模型 → 按区段叠加坡度/路况/温度修正 → 得到 unit_energy 曲线。"
                },
                "mission_profile_estimation": {
                    "title": "任务总行程预测",
                    "summary": "在速度、安全与路况约束下，预测整个12km任务的行驶时间。",
                    "key_points": [
                        "为平缓路段设定较高巡航速度，为泥泞与陡坡路段设定限速",
                        "在关键转弯、上坡前后与危险点附近加入减速与加速时间",
                        "累加各区段行驶时间与可能的短暂停靠时间，得到总耗时区间"
                    ],
                    "knowledge_trace": "速度与安全策略 → 区段行驶时间计算 → 累加得到 total_travel_time。"
                },
                "energy_time_inference": {
                    "title": "能耗与耗时推理与补能建议",
                    "summary": "综合分段能耗与总行程时间，推导任务总能耗与耗时，并对电池/燃料余量与补能策略给出建议。",
                    "key_points": [
                        "将 unit_energy 与分段距离相乘并累加，得到任务总能耗估计",
                        "将总能耗与车辆电池容量或油箱容量对比，评估单次补能是否足够",
                        "若单次补能不足，给出中途补能位置、补给车辆编组或备用车辆切换建议"
                    ],
                    "knowledge_trace": "load_slope_profile + unit_energy + total_travel_time → 任务总能耗与耗时 → 与能源容量对比 → 生成补能/补给计划。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "load_slope_profile", "label": "载重与坡度解析结果", "type": "input"},
                            {"id": "unit_energy", "label": "单位距离能耗估计", "type": "process"},
                            {"id": "travel_time", "label": "行程时间预测", "type": "process"},
                            {"id": "total_energy", "label": "总能耗推理", "type": "process"},
                            {"id": "resupply_plan", "label": "补能与补给建议", "type": "output"}
                        ],
                        "edges": [
                            {"source": "load_slope_profile", "target": "unit_energy"},
                            {"source": "unit_energy", "target": "total_energy"},
                            {"source": "load_slope_profile", "target": "travel_time"},
                            {"source": "total_energy", "target": "resupply_plan"},
                            {"source": "travel_time", "target": "resupply_plan"}
                        ]
                    }
                }
            }
        },
    ),

    # 二、设备投放支援模型测试（7~12）
    Scenario(
        id="equipment_fleet_formation",  # 5. 任务编组
        model_name="设备投放",
        name="任务编组",
        example_input="向X前沿阵地投放侦察装置Y，需要多架无人机协同运输",
        reasoning_chain="任务解析（物资类型、重量与体积、投放精度需求、环境风险）→ 设备匹配（匹配适用的无人机或无人车类型）→ 数量推断（根据载荷能力与冗余策略推算所需设备数量）→ 投放方式生成（悬停投放/抛投/着陆放置等）",
        prompt=(
            "【设备投放-任务编组专项要求】\n"
            "1. 行为树必须包含：task_analysis（解析物资类型、重量体积、投放精度需求、环境风险）→ "
            "equipment_matching（匹配适用的无人机/无人车类型，说明选择理由）→ "
            "quantity_inference（根据载荷能力与冗余策略推算设备数量）→ "
            "delivery_method（生成投放方式：悬停投放/抛投/着陆放置等）→ "
            "formation_result（编组结果汇总，包含 knowledge_graph）。\n"
            "2. formation_result 的 knowledge_graph 应体现：任务解析 → 设备匹配 → 数量计算 → 投放方式选择 → 编组方案。"
        ),
        example_output={
            "default_focus": "formation_result",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "📦 任务解析：向X前沿阵地投放侦察装置Y",
                "status": "completed",
                "summary": "解析侦察装置Y的重量体积、投放精度需求与前沿阵地环境风险，为后续设备匹配与数量推断提供约束条件。",
                "children": [
                    {
                        "id": "equipment_matching",
                        "label": "设备匹配",
                        "status": "completed",
                        "summary": "在可用无人机/无人车中筛选适合携带侦察装置Y并满足投放精度需求的平台。",
                        "children": []
                    },
                    {
                        "id": "quantity_inference",
                        "label": "数量推断",
                        "status": "completed",
                        "summary": "结合装置Y重量体积与单台平台载荷能力，叠加冗余策略推算所需设备数量。",
                        "children": []
                    },
                    {
                        "id": "delivery_method",
                        "label": "投放方式生成",
                        "status": "completed",
                        "summary": "根据环境风险与投放精度选取悬停投放或低空抛投等方式。",
                        "children": []
                    },
                    {
                        "id": "formation_result",
                        "label": "✅ 编组结果汇总",
                        "status": "active",
                        "summary": "形成由多架小型多旋翼无人机构成的投放编组，并明确各自装载份额与投放方式。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务解析",
                    "summary": "围绕“向X前沿阵地投放侦察装置Y，需要多架无人机协同运输”的描述，抽取物资属性与作战环境约束。",
                    "key_points": [
                        "识别侦察装置Y的重量、尺寸与安装接口约束",
                        "明确前沿阵地对投放位置误差、落点安全区的精度需求",
                        "分析环境风险，如敌情威胁、高风区、地形遮挡等"
                    ],
                    "knowledge_trace": "任务文本 → 物资属性 + 精度 + 环境风险三类要素抽取 → 为设备匹配与数量推断节点提供统一输入。"
                },
                "equipment_matching": {
                    "title": "设备匹配",
                    "summary": "在候选平台中，选出既能安全携带侦察装置Y，又能达到目标区域的无人机/无人车配置。",
                    "key_points": [
                        "比较多旋翼无人机、固定翼无人机与地面无人车的载荷与航程能力",
                        "考虑起降条件与前沿阵地的地形限制，倾向选择垂直起降平台",
                        "优先选用具备稳定悬停能力的平台以满足投放精度需求"
                    ],
                    "knowledge_trace": "载荷与精度需求 → 平台能力对比 → 选定多旋翼/复合翼等具体机型。"
                },
                "quantity_inference": {
                    "title": "数量推断",
                    "summary": "依据装置Y重量体积与单机载荷，叠加冗余比例，推算所需无人机数量。",
                    "key_points": [
                        "计算单架无人机在安全余量下可携带的装置数量或重量",
                        "按总任务载荷除以单机有效载荷得到理论最少架数",
                        "在理论值基础上增加一定比例冗余以应对故障或返航失败"
                    ],
                    "knowledge_trace": "物资总载荷建模 → 理论平台数计算 → 冗余策略叠加 → 得到最终编组数量。"
                },
                "delivery_method": {
                    "title": "投放方式生成",
                    "summary": "在安全与精度约束下，确定装置Y采用悬停投放、低空抛投或着陆放置等方式。",
                    "key_points": [
                        "若前沿阵地周边存在敌情威胁，优先选择短停或抛投方式缩短暴露时间",
                        "对高精度需求任务，倾向选择悬停慢速下放或短暂着陆放置",
                        "综合风场、地形遮挡等因素，评估各方式对落点偏差的影响"
                    ],
                    "knowledge_trace": "环境风险 + 精度要求 → 候选投放方式评估 → 选定最优或组合方案。"
                },
                "formation_result": {
                    "title": "编组结果汇总",
                    "summary": "将任务解析、设备匹配、数量推断和投放方式四个环节的结论汇总为可执行的编组方案。",
                    "key_points": [
                        "明确编组中各无人机的型号、数量与各自装载份额",
                        "为每台平台绑定具体的投放方式与执行顺序",
                        "为后续任务流程提供结构化的编组描述，可直接用于调度与可视化"
                    ],
                    "knowledge_trace": "任务要素 → 设备匹配 → 数量与方式推断 → 汇总为编组蓝图。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "task_analysis", "label": "任务解析(装置Y, 前沿阵地X)", "type": "input"},
                            {"id": "equipment_matching", "label": "设备匹配(无人机/无人车)", "type": "process"},
                            {"id": "quantity_inference", "label": "数量计算(载荷+冗余)", "type": "process"},
                            {"id": "delivery_method", "label": "投放方式选择", "type": "decision"},
                            {"id": "formation_plan", "label": "编组方案输出", "type": "output"}
                        ],
                        "edges": [
                            {"source": "task_analysis", "target": "equipment_matching"},
                            {"source": "equipment_matching", "target": "quantity_inference"},
                            {"source": "quantity_inference", "target": "delivery_method"},
                            {"source": "delivery_method", "target": "formation_plan"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="equipment_precision_location",  # 6. 高精度目标定位
        model_name="设备投放",
        name="高精度目标定位",
        example_input="向X区域精确投放传感器Y",
        reasoning_chain="环境解析（读取地图、地物特征、遮挡信息）→ 传感器融合定位（无人机视觉、激光雷达、深度感知等多源数据融合）→ 误差纠正（基于航迹、风场、地面标志物进行偏差修正）→ 定位结果生成（输出目标区域精确坐标）",
        prompt=(
            "【设备投放-高精度目标定位专项要求】\n"
            "1. 行为树必须包含：environment_analysis（读取地图、地物特征、遮挡信息）→ "
            "sensor_fusion（多源数据融合：视觉、激光雷达、深度感知）→ "
            "error_correction（基于航迹、风场、地面标志物进行偏差修正）→ "
            "location_result（输出精确坐标，包含 knowledge_graph）。\n"
            "2. location_result 的 knowledge_graph 应体现：环境解析 → 多源融合 → 误差纠正 → 坐标输出。"
        ),
        example_output={
            "default_focus": "location_result",
            "behavior_tree": {
                "id": "environment_analysis",
                "label": "🗺️ 环境解析",
                "status": "completed",
                "summary": "读取X区域的地图、地物特征与遮挡情况，圈定可能的目标投放区域。",
                "children": [
                    {
                        "id": "sensor_fusion",
                        "label": "传感器融合定位",
                        "status": "completed",
                        "summary": "融合无人机视觉、激光雷达与深度感知数据，对预设标记与地物特征进行联合识别。",
                        "children": []
                    },
                    {
                        "id": "error_correction",
                        "label": "误差纠正",
                        "status": "completed",
                        "summary": "利用航迹、风场和地面标志物对候选投放点坐标进行偏差修正。",
                        "children": []
                    },
                    {
                        "id": "location_result",
                        "label": "✅ 定位结果生成",
                        "status": "active",
                        "summary": "输出目标区域的精确坐标，用于后续投放或导航控制模块。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "environment_analysis": {
                    "title": "环境解析",
                    "summary": "通过地图与感知数据，识别X区域的关键地物、遮挡物和候选目标区域。",
                    "key_points": [
                        "从电子地图中提取道路、建筑物、水体等基础地物特征",
                        "结合任务预设标记的大致位置缩小搜索范围",
                        "识别高遮挡区域，为后续传感器视角规划提供参考"
                    ],
                    "knowledge_trace": "地图与先验信息 → 地物特征提取 → 候选目标区域圈定。"
                },
                "sensor_fusion": {
                    "title": "传感器融合定位",
                    "summary": "利用视觉、激光雷达与深度传感器联合识别预设标记，并估算其相对位置。",
                    "key_points": [
                        "视觉模块检测地面或建筑表面的预设标记图案",
                        "激光雷达提供三维点云以刻画空间结构和障碍物",
                        "深度感知补充距离信息，提升目标位置估计的精度"
                    ],
                    "knowledge_trace": "多源数据对齐 → 特征级或决策级融合 → 输出目标的初始空间位置估计。"
                },
                "error_correction": {
                    "title": "误差纠正",
                    "summary": "结合无人机航迹、风场估计与地面标志物位置，修正初始定位误差。",
                    "key_points": [
                        "利用历史航迹和IMU/GNSS数据对定位漂移进行估计",
                        "将风场对无人机姿态与轨迹的影响纳入误差模型",
                        "使用已知坐标的地面标志物进行绝对坐标对齐"
                    ],
                    "knowledge_trace": "初始定位结果 → 引入航迹与风场模型 → 与地面标志物对齐 → 得到修正后坐标。"
                },
                "location_result": {
                    "title": "定位结果生成",
                    "summary": "在误差纠正后的基础上，输出可用于后续任务的目标区域精确坐标。",
                    "key_points": [
                        "将修正后的目标位置转换为统一坐标系（如WGS84或本地平面坐标）",
                        "附带定位精度评估指标（如误差椭圆或置信区间）",
                        "为投放控制或导航系统提供接口友好的数据结构"
                    ],
                    "knowledge_trace": "修正后空间位置 → 坐标系转换与精度评估 → 输出标准化定位结果。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "env_analysis", "label": "环境解析", "type": "input"},
                            {"id": "fusion", "label": "多源传感器融合", "type": "process"},
                            {"id": "correction", "label": "误差纠正", "type": "process"},
                            {"id": "coord_output", "label": "坐标输出", "type": "output"}
                        ],
                        "edges": [
                            {"source": "env_analysis", "target": "fusion"},
                            {"source": "fusion", "target": "correction"},
                            {"source": "correction", "target": "coord_output"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="equipment_auto_loading",  # 7. 自主装卸控制
        model_name="设备投放",
        name="自主装卸控制",
        example_input="将设备Y通过无人车运输至X点，并由机械臂自主卸载",
        reasoning_chain="装卸需求解析（重量、尺寸、抓取方式）→ 动作规划（机械臂抓取路径、姿态调整、力控策略）→ 安全检测（防倾倒、防滑落、力反馈监测）→ 装卸完成确认（识别设备是否已稳定装载/完成卸载）",
        prompt=(
            "【设备投放-自主装卸控制专项要求】\n"
            "1. 行为树必须包含：loading_requirement（解析重量、尺寸、抓取方式）→ "
            "motion_planning（机械臂抓取路径、姿态调整、力控策略）→ "
            "safety_detection（防倾倒、防滑落、力反馈监测）→ "
            "completion_confirmation（确认装卸完成，包含 knowledge_graph）。\n"
            "2. completion_confirmation 的 knowledge_graph 应体现：需求解析 → 动作规划 → 安全检测 → 完成确认。"
        ),
        example_output={
            "default_focus": "completion_confirmation",
            "behavior_tree": {
                "id": "loading_requirement",
                "label": "📦 装卸需求解析",
                "status": "completed",
                "summary": "解析设备Y的重量、尺寸与抓取特性，明确无人车装卸任务的基本约束。",
                "children": [
                    {
                        "id": "motion_planning",
                        "label": "动作规划",
                        "status": "completed",
                        "summary": "为机械臂生成抓取路径、姿态调整与力控策略。",
                        "children": []
                    },
                    {
                        "id": "safety_detection",
                        "label": "安全检测",
                        "status": "completed",
                        "summary": "在装卸过程中监测倾倒、滑落与异常力反馈风险。",
                        "children": []
                    },
                    {
                        "id": "completion_confirmation",
                        "label": "✅ 装卸完成确认",
                        "status": "active",
                        "summary": "综合视觉与传感器数据，确认设备Y已稳定装载/完成卸载。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "loading_requirement": {
                    "title": "装卸需求解析",
                    "summary": "将“将设备Y通过无人车运输至X点，并由机械臂自主卸载”的描述转化为对机械臂与载货平台的约束条件。",
                    "key_points": [
                        "分析设备Y重量与尺寸，判断是否需要双臂协作或辅助支撑",
                        "识别设备Y的可抓取区域与禁止接触区域",
                        "考虑无人车货舱空间与重心位置，确定装卸姿态与目标放置点"
                    ],
                    "knowledge_trace": "任务文本解析 → 设备与平台约束抽取 → 形成供动作规划使用的装卸需求配置。"
                },
                "motion_planning": {
                    "title": "动作规划",
                    "summary": "根据装卸需求，为机械臂生成安全平滑的抓取和放置运动轨迹。",
                    "key_points": [
                        "规划从待装载位置到目标货舱位置的关节轨迹，避免碰撞",
                        "在抓取与放置关键阶段引入力控策略，限制接触力",
                        "考虑越野车体姿态微小晃动，对轨迹进行必要冗余与缓冲"
                    ],
                    "knowledge_trace": "装卸需求 → 碰撞约束与关节限制建模 → 轨迹与力控联合规划。"
                },
                "safety_detection": {
                    "title": "安全检测",
                    "summary": "在执行装卸动作时实时监测倾倒、滑落与异常力矩等风险。",
                    "key_points": [
                        "监控关节力矩与末端力传感器数据，识别异常高负载",
                        "利用视觉或深度传感器检查设备Y是否有偏移或滑落趋势",
                        "在检测到高风险时触发暂停或回退动作，保护人员与设备安全"
                    ],
                    "knowledge_trace": "在线监测 → 异常阈值判断 → 风险等级评估 → 触发保护策略。"
                },
                "completion_confirmation": {
                    "title": "装卸完成确认",
                    "summary": "在装载或卸载动作完成后，确认设备Y已稳定定位并处于安全状态。",
                    "key_points": [
                        "通过视觉/深度检查设备是否处于预定放置区域和姿态",
                        "结合力传感器与位置反馈确认设备已脱离机械臂且稳定支撑",
                        "记录装卸完成状态与关键参数，用于追踪与复盘"
                    ],
                    "knowledge_trace": "动作结束 → 姿态与接触状态检查 → 给出“完成/失败/需重试”判定。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "req", "label": "装卸需求解析", "type": "input"},
                            {"id": "plan", "label": "动作规划", "type": "process"},
                            {"id": "safety", "label": "安全检测", "type": "process"},
                            {"id": "confirm", "label": "完成确认", "type": "output"}
                        ],
                        "edges": [
                            {"source": "req", "target": "plan"},
                            {"source": "plan", "target": "safety"},
                            {"source": "safety", "target": "confirm"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="equipment_delivery_confirmation",  # 8. 效效确认 / 投放确认
        model_name="设备投放",
        name="投放确认",
        example_input="将侦察节点Y投放至X点并确认部署成功",
        reasoning_chain="结果感知（投放后图像、姿态信息、设备回传信号）→ 落点偏差分析（比较实际坐标与目标坐标）→ 功能状态检查（是否正常通电、是否建立通信链路）→ 投放成功判定（成功/失败/需重投）",
        prompt=(
            "【设备投放-投放确认专项要求】\n"
            "1. 行为树必须包含：result_perception（投放后图像、姿态信息、设备回传信号）→ "
            "deviation_analysis（比较实际坐标与目标坐标）→ "
            "function_check（检查通电、通信链路状态）→ "
            "deployment_judgment（判定成功/失败/需重投，包含 knowledge_graph）。\n"
            "2. deployment_judgment 的 knowledge_graph 应体现：结果感知 → 偏差分析 → 功能检查 → 成功判定。"
        ),
        example_output={
            "default_focus": "deployment_judgment",
            "behavior_tree": {
                "id": "result_perception",
                "label": "📷 结果感知",
                "status": "completed",
                "summary": "在设备Y投放至X点后，采集图像、姿态与设备回传信号，形成投放结果的第一手信息。",
                "children": [
                    {
                        "id": "deviation_analysis",
                        "label": "落点偏差分析",
                        "status": "completed",
                        "summary": "将设备Y的实际落点坐标与预定坐标进行对比，评估空间偏差。",
                        "children": []
                    },
                    {
                        "id": "function_check",
                        "label": "功能状态检查",
                        "status": "completed",
                        "summary": "检查设备Y是否正常通电、建立通信链路并处于预期工作模式。",
                        "children": []
                    },
                    {
                        "id": "deployment_judgment",
                        "label": "✅ 投放成功判定",
                        "status": "active",
                        "summary": "综合落点偏差与功能状态，给出“成功/失败/需重投”的判定结论。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "result_perception": {
                    "title": "结果感知",
                    "summary": "通过机载和地面传感器获取设备投放后的图像、姿态与通信状态，建立投放结果的感知基础。",
                    "key_points": [
                        "采集覆盖设备周边的全景或多角度图像，观察落点环境",
                        "利用惯导或姿态传感器估计设备的姿态（是否倾倒、是否稳定）",
                        "读取设备回传的基础心跳与状态码，确认是否上线"
                    ],
                    "knowledge_trace": "图像与姿态采集 → 通信状态读取 → 形成可用于分析的投放结果数据集。"
                },
                "deviation_analysis": {
                    "title": "落点偏差分析",
                    "summary": "将设备实际落点坐标与任务规划的目标坐标进行对比，评估偏差是否在可接受范围内。",
                    "key_points": [
                        "根据图像/传感器数据估计设备在地图坐标中的实际位置",
                        "计算与目标坐标之间的水平偏差与高度差",
                        "将偏差与任务容差阈值进行比较，给出“在容差内/超出容差”的结论"
                    ],
                    "knowledge_trace": "实际位置反算 → 与目标坐标对比 → 偏差归类与标记。"
                },
                "function_check": {
                    "title": "功能状态检查",
                    "summary": "检查设备是否正常通电、建立通信链路并在预期模式下运行。",
                    "key_points": [
                        "确认设备电源状态与电量水平在安全范围内",
                        "验证与指挥端或中继节点的通信链路是否建立稳定",
                        "检查关键功能模块（传感器/计算/通信）是否按预期上电自检通过"
                    ],
                    "knowledge_trace": "设备状态采集 → 通信链路与功能模块检查 → 形成“可用/受限/不可用”的功能结论。"
                },
                "deployment_judgment": {
                    "title": "投放成功判定",
                    "summary": "综合落点偏差结果与功能状态，判断本次投放是否成功，如失败则给出是否需要重投的建议。",
                    "key_points": [
                        "若落点在容差范围内且功能完好，则标记为“投放成功”",
                        "若落点偏差较大或设备功能严重受损，则标记为“投放失败/需重投”",
                        "在边界情况（轻微偏差或部分功能受限）下，给出“勉强可用/建议补救策略”的说明"
                    ],
                    "knowledge_trace": "偏差分析结果 + 功能检查结果 → 规则或经验模型推理 → 输出成功/失败/需重投的判定及理由。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "perception", "label": "结果感知", "type": "input"},
                            {"id": "deviation", "label": "落点偏差分析", "type": "process"},
                            {"id": "function", "label": "功能状态检查", "type": "process"},
                            {"id": "judgment", "label": "投放成功判定", "type": "output"}
                        ],
                        "edges": [
                            {"source": "perception", "target": "deviation"},
                            {"source": "perception", "target": "function"},
                            {"source": "deviation", "target": "judgment"},
                            {"source": "function", "target": "judgment"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="equipment_drop_site_safety",  # 11. 投放点环境安全性评估
        model_name="设备投放",
        name="投放点环境安全性评估",
        example_input="需在风速较大、地面碎石较多的区域投放设备A。",
        reasoning_chain="地面状态识别（碎石、坡度）→ 环境因素分析（风速、能见度）→ 降落风险评估（偏移风险、设备损坏风险）→ 策略生成（降低投放高度、调整无人机姿态、改用缓投模式）",
        prompt=(
            "【设备投放-投放点环境安全性评估专项要求】\n"
            "1. 行为树必须至少包含以下核心节点：\n"
            "   - task_analysis（任务解析）：从任务文本中抽取投放区域地形、障碍物、气象条件与敌情风险等要素；\n"
            "   - ground_state_recognition（地面状态识别）：识别碎石、坡度、不平整与障碍物分布，可细化出 ground_type_classification 与 obstacle_layout 两个子节点；\n"
            "   - env_factor_analysis（环境因素分析）：分析风速、风向、能见度等环境因素对投放安全的影响；\n"
            "   - landing_risk_evaluation（降落风险评估）：综合地面状态与环境因素，对偏移风险、设备损坏风险等进行分级评估；\n"
            "   - landing_strategy_generation（策略生成，核心决策节点）：根据风险等级给出降落方式/接近策略（降低投放高度、调整无人机姿态、改用缓投模式或更换投放点），必须包含 knowledge_graph 字段。\n"
            "2. landing_strategy_generation 节点的 knowledge_graph 必须体现：\n"
            "   地面状态识别(ground_state) → 环境因素分析(env_factors) → 降落风险评估(landing_risk) → 策略生成(landing_strategy) → 投放点安全等级(safety_level)。\n"
            "3. node_insights 中需：\n"
            "   - 明确在碎石大、坡度大、风速大等典型组合下的风险判断规则；\n"
            "   - 给出不同安全等级下建议的投放高度、姿态控制与是否更换投放点的策略；\n"
            "   - knowledge_trace 体现“任务解析 → 地面与环境建模 → 风险分级 → 策略选择”的完整逻辑链条。"
        ),
        example_output={
            "default_focus": "landing_strategy_generation",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "📍 任务解析：评估碎石+大风区域的投放安全性",
                "status": "completed",
                "summary": "解析“需在风速较大、地面碎石较多的区域投放设备A”的描述，抽取地面状态、风场与能见度等关键安全要素。",
                "children": [
                    {
                        "id": "ground_state_recognition",
                        "label": "地面状态识别",
                        "status": "completed",
                        "summary": "识别投放区域地面主要由碎石构成，坡度中等且存在局部不平整。",
                        "children": []
                    },
                    {
                        "id": "env_factor_analysis",
                        "label": "环境因素分析",
                        "status": "completed",
                        "summary": "分析当前风速较大、风向变化与能见度等因素对投放偏移与姿态稳定性的影响。",
                        "children": []
                    },
                    {
                        "id": "landing_risk_evaluation",
                        "label": "降落风险评估",
                        "status": "completed",
                        "summary": "综合地面碎石与大风环境，评估设备A存在中高水平的偏移风险与局部撞击风险。",
                        "children": []
                    },
                    {
                        "id": "landing_strategy_generation",
                        "label": "✅ 策略生成与安全等级判定",
                        "status": "active",
                        "summary": "生成降低投放高度、调整无人机姿态与选择缓投模式等策略，并给出投放点安全等级评定。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务解析",
                    "summary": "将“风速较大、地面碎石较多的区域投放设备A”的自然语言描述转化为结构化的安全评估要素。",
                    "key_points": [
                        "提取投放区域地面类型为碎石，推断摩擦系数与支撑稳定性偏低",
                        "识别风速较大且可能阵风，易引起投放过程中的姿态扰动与落点偏移",
                        "为后续风险评估提供地面、风场与设备特性三类输入"
                    ],
                    "knowledge_trace": "任务文本解析 → 地面/气象/设备要素抽取 → 形成安全评估输入配置。"
                },
                "ground_state_recognition": {
                    "title": "地面状态识别",
                    "summary": "通过地图、视觉与先验信息识别地面为碎石、不平整且具有一定坡度。",
                    "key_points": [
                        "利用视觉与高度图判断地表主要为松散碎石而非硬质平整地面",
                        "估计局部坡度与起伏程度，识别潜在滚落或倾倒方向",
                        "标注附近大型障碍物与空旷区，为落点选择提供参考"
                    ],
                    "knowledge_trace": "地面图像与地形数据 → 地面类型与坡度分析 → 输出 ground_state 特征。"
                },
                "env_factor_analysis": {
                    "title": "环境因素分析",
                    "summary": "对风速、风向与能见度等环境因素进行量化，评估其对投放过程的扰动程度。",
                    "key_points": [
                        "根据气象数据与无人机机载传感器估计当前风速与风向波动范围",
                        "结合能见度与光照条件判断视觉感知与姿态控制的可靠性",
                        "将风场扰动转化为潜在偏移量与姿态误差的估计"
                    ],
                    "knowledge_trace": "气象与传感数据 → 风场与能见度建模 → 输出 env_factors 指标。"
                },
                "landing_risk_evaluation": {
                    "title": "降落风险评估",
                    "summary": "综合地面碎石与大风环境，对偏移与设备损坏风险进行分级评估。",
                    "key_points": [
                        "在碎石+中等坡度组合下，设备落点稍有偏移就可能导致支撑不稳",
                        "大风与阵风增加投放偏移与姿态失稳概率",
                        "基于经验阈值将综合风险评为“中高”，建议启用保守投放策略"
                    ],
                    "knowledge_trace": "ground_state + env_factors → 风险指标计算 → 输出 landing_risk 等级。"
                },
                "landing_strategy_generation": {
                    "title": "策略生成与安全等级判定",
                    "summary": "依据降落风险等级生成投放策略，并给出投放点安全等级与建议是否更换投放点。",
                    "key_points": [
                        "在中高风险等级下建议降低投放高度、减小水平速度并采用缓投模式",
                        "根据风向选择更有利的进场方向以降低横向偏移",
                        "若综合风险超过阈值，则建议更换至邻近更平整、更低风速的备选投放点"
                    ],
                    "knowledge_trace": "landing_risk → 候选投放策略评估 → 选择具体策略与安全等级 → 输出安全评估结果与建议。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "ground_state", "label": "地面状态识别结果", "type": "input"},
                            {"id": "env_factors", "label": "环境因素分析结果", "type": "input"},
                            {"id": "landing_risk", "label": "降落风险评估", "type": "process"},
                            {"id": "landing_strategy", "label": "投放策略生成", "type": "decision"},
                            {"id": "safety_level", "label": "投放点安全等级与建议", "type": "output"}
                        ],
                        "edges": [
                            {"source": "ground_state", "target": "landing_risk"},
                            {"source": "env_factors", "target": "landing_risk"},
                            {"source": "landing_risk", "target": "landing_strategy"},
                            {"source": "landing_strategy", "target": "safety_level"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="equipment_drop_anomaly_response",  # 12. 投放流程异常检测与应急策略生成
        model_name="设备投放",
        name="投放流程异常检测与应急策略生成",
        example_input="投放设备时出现挂载装置开合异常。",
        reasoning_chain="投放动作监测（挂载开合状态、姿态角度）→ 异常模式识别（开合卡滞、偏移、风扰动）→ 风险等级判断 → 应急策略生成（重试开合、调整姿态、切换到备用投放方式、重新选择投放点）",
        prompt=(
            "【设备投放-投放流程异常检测与应急策略生成专项要求】\n"
            "1. 行为树必须至少包含以下核心节点：\n"
            "   - task_analysis（任务解析）：识别投放流程涉及的关键动作与设备；\n"
            "   - drop_action_monitoring（投放动作监测）：实时监测挂载开合状态、无人机姿态角度与投放高度变化；\n"
            "   - anomaly_pattern_recognition（异常模式识别）：识别开合卡滞、姿态偏移、风场扰动等异常模式；\n"
            "   - risk_level_evaluation（风险等级判断）：根据异常程度与当前高度/环境给出风险分级；\n"
            "   - emergency_strategy_generation（应急策略生成，核心决策节点）：针对不同风险等级生成重试开合、姿态调整、切换备用投放方式或重新选择投放点等应急策略，必须包含 knowledge_graph 字段。\n"
            "2. emergency_strategy_generation 节点的 knowledge_graph 必须体现：\n"
            "   投放动作监测(drop_monitoring) → 异常模式识别(anomaly_pattern) → 风险等级判断(risk_level) → 应急策略生成(emergency_strategy) → 执行结果与流程恢复(execution_result)。\n"
            "3. node_insights 中需：\n"
            "   - 描述挂载开合异常、姿态偏移与风场扰动三类典型异常的检测指标；\n"
            "   - 对不同风险等级说明应急策略的优先顺序与约束条件（如在低高度不宜直接抛投）；\n"
            "   - knowledge_trace 体现“监测 → 识别 → 分级 → 决策 → 执行与恢复”的闭环。"
        ),
        example_output={
            "default_focus": "emergency_strategy_generation",
            "behavior_tree": {
                "id": "drop_action_monitoring",
                "label": "🎯 投放动作监测",
                "status": "completed",
                "summary": "在投放过程中持续监测挂载装置开合状态、无人机姿态与投放高度变化。",
                "children": [
                    {
                        "id": "anomaly_pattern_recognition",
                        "label": "异常模式识别",
                        "status": "completed",
                        "summary": "识别挂载开合卡滞、姿态偏移与风场扰动等异常模式。",
                        "children": []
                    },
                    {
                        "id": "risk_level_evaluation",
                        "label": "风险等级判断",
                        "status": "completed",
                        "summary": "根据异常类型与当前高度/环境条件，将风险分为低、中、高等级。",
                        "children": []
                    },
                    {
                        "id": "emergency_strategy_generation",
                        "label": "✅ 应急策略生成与流程恢复",
                        "status": "active",
                        "summary": "针对不同风险等级生成重试开合、姿态调整或切换投放方式等应急策略，并推动流程恢复到安全状态。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "drop_action_monitoring": {
                    "title": "投放动作监测",
                    "summary": "对投放过程中的挂载开合、姿态角度与高度变化进行高频监测，为异常识别提供数据基础。",
                    "key_points": [
                        "实时读取挂载机构的开合角度、驱动电流与反馈信号",
                        "监控无人机姿态角与角速度，识别异常俯仰/滚转偏移趋势",
                        "记录投放高度与垂直速度，以区分不同阶段的安全约束"
                    ],
                    "knowledge_trace": "传感器与执行机构数据采集 → 统一时间轴对齐 → 输出用于异常识别的监测序列。"
                },
                "anomaly_pattern_recognition": {
                    "title": "异常模式识别",
                    "summary": "基于监测数据识别开合卡滞、姿态偏移与风场扰动等典型异常模式。",
                    "key_points": [
                        "通过驱动电流突增与位置反馈不一致识别挂载开合卡滞",
                        "根据姿态角偏离与姿态控制输出不匹配判断姿态异常",
                        "利用风速/风向突变与位置偏移模式识别风场扰动引发的异常"
                    ],
                    "knowledge_trace": "监测序列 → 模式匹配或阈值判断 → 输出 anomaly_pattern 标签与置信度。"
                },
                "risk_level_evaluation": {
                    "title": "风险等级判断",
                    "summary": "考虑异常类型、当前高度与设备特性，对风险进行分级判断。",
                    "key_points": [
                        "在高空轻微卡滞可标记为低至中等级风险，可尝试重试开合",
                        "在低高度严重姿态偏移可能导致设备或平台损坏，应判定为高风险",
                        "综合任务重要性与环境复杂度对相同异常进行差异化分级"
                    ],
                    "knowledge_trace": "anomaly_pattern + 高度/环境上下文 → 风险规则/模型评估 → 输出 risk_level。"
                },
                "emergency_strategy_generation": {
                    "title": "应急策略生成与流程恢复",
                    "summary": "根据风险等级和异常类型选择合适的应急策略，使投放流程恢复到安全可控状态。",
                    "key_points": [
                        "对低风险卡滞优先尝试在安全高度重试开合并监控结果",
                        "对中风险姿态偏移先进行姿态调整与悬停稳定，再评估是否继续投放",
                        "对高风险情况启动终止投放或切换到备用投放方式/备选投放点，并记录事件"
                    ],
                    "knowledge_trace": "risk_level + anomaly_pattern → 候选应急动作集 → 选择并执行策略 → 评估流程是否恢复至安全状态。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "drop_monitoring", "label": "投放动作监测数据", "type": "input"},
                            {"id": "anomaly_pattern", "label": "异常模式识别结果", "type": "process"},
                            {"id": "risk_level", "label": "风险等级判断", "type": "process"},
                            {"id": "emergency_strategy", "label": "应急策略生成", "type": "decision"},
                            {"id": "execution_result", "label": "执行结果与流程恢复状态", "type": "output"}
                        ],
                        "edges": [
                            {"source": "drop_monitoring", "target": "anomaly_pattern"},
                            {"source": "anomaly_pattern", "target": "risk_level"},
                            {"source": "risk_level", "target": "emergency_strategy"},
                            {"source": "emergency_strategy", "target": "execution_result"}
                        ]
                    }
                }
            }
        },
    ),

    # 三、伤员救助支援模型测试（9~12）
    Scenario(
        id="casualty_team_formation",  # 9. 任务编组
        model_name="伤员救助",
        name="任务编组",
        example_input="在X区域发现两名伤员，需要无人救援设备前往救助并运回安全点",
        reasoning_chain="任务解析（伤员数量、地形环境、救助紧急度）→ 设备类型匹配（医疗无人机、担架无人车或机器人）→ 数量计算（根据伤员人数与运载能力推算设备数量）→ 救援方式规划（空投急救包/无人机抵近观察/无人车运送）",
        prompt=(
            "【伤员救助-任务编组专项要求】\n"
            "1. 行为树必须包含：task_analysis（解析伤员数量、地形环境、救助紧急度）→ "
            "equipment_matching（匹配医疗无人机、担架无人车或机器人）→ "
            "quantity_calculation（根据伤员人数与运载能力推算设备数量）→ "
            "rescue_planning（规划空投急救包/无人机抵近观察/无人车运送）→ "
            "team_formation（编组结果，包含 knowledge_graph）。\n"
            "2. team_formation 的 knowledge_graph 应体现：任务解析 → 设备匹配 → 数量计算 → 救援方式 → 编组方案。"
        ),
        example_output={
            "default_focus": "team_formation",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "🆘 任务解析：X区域两名伤员救助与转运",
                "status": "completed",
                "summary": "解析在X区域发现两名伤员的环境、紧急程度与可达性，为选择救援设备与路径提供约束。",
                "children": [
                    {
                        "id": "equipment_matching",
                        "label": "设备类型匹配",
                        "status": "completed",
                        "summary": "根据地形与伤情选择医疗无人机、担架无人车或救援机器人等组合。",
                        "children": []
                    },
                    {
                        "id": "quantity_calculation",
                        "label": "数量计算",
                        "status": "completed",
                        "summary": "依据伤员数量、各类设备运载能力与冗余要求推算所需平台数量。",
                        "children": []
                    },
                    {
                        "id": "rescue_planning",
                        "label": "救援方式规划",
                        "status": "completed",
                        "summary": "综合任务紧急度与地形条件，规划空投急救包、无人机抵近观察和无人车转运的组合方式。",
                        "children": []
                    },
                    {
                        "id": "team_formation",
                        "label": "✅ 救助编组结果",
                        "status": "active",
                        "summary": "给出由医疗无人机与担架无人车构成的协同救援编组方案。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务解析",
                    "summary": "将“两名伤员、X区域、需前往救助并运回安全点”的文本拆解为救援规模、时间压力和地形风险等关键要素。",
                    "key_points": [
                        "识别伤员数量与可能分布位置，决定是否需要多点同时接入",
                        "评估X区域地形（山地、废墟、浅水等）对设备通行能力的影响",
                        "根据“发现伤员”到“必须撤离”的时间窗口评估救助紧急度"
                    ],
                    "knowledge_trace": "任务文本解析 → 伤员/地形/时间三类约束建模 → 为设备选择与数量推算提供输入。"
                },
                "equipment_matching": {
                    "title": "设备类型匹配",
                    "summary": "在医疗无人机、担架无人车与地面机器人中进行组合选择，以覆盖侦察、急救和搬运功能。",
                    "key_points": [
                        "为快速抵近和远程观察选配医疗无人机，承担先期侦察与急救包投放",
                        "为稳定搬运与撤离选配担架无人车，满足承重与地形通过性需求",
                        "在复杂地形或狭窄空间场景下考虑增配多足救援机器人"
                    ],
                    "knowledge_trace": "任务要素 → 功能需求拆解（侦察/急救/搬运） → 匹配具备相应能力的无人平台。"
                },
                "quantity_calculation": {
                    "title": "数量计算",
                    "summary": "基于每类设备的载荷能力与行动效率，结合冗余策略推算所需设备数量。",
                    "key_points": [
                        "按照“两名伤员+可能随身物资”估算搬运需求",
                        "考虑单台担架车一次只能搬运一名伤员，推导至少需要两次往返或两台设备",
                        "为防止设备故障或路径被阻断，增加1台冗余平台或预备替代路径"
                    ],
                    "knowledge_trace": "伤员与物资载荷建模 → 按设备能力计算理论最小数量 → 加入冗余与调度弹性。"
                },
                "rescue_planning": {
                    "title": "救援方式规划",
                    "summary": "生成“空投急救包 + 无人机抵近侦察 + 担架无人车转运”的组合救援流程。",
                    "key_points": [
                        "先由医疗无人机抵近观察，确认周边环境与伤情，必要时空投急救包",
                        "随后安排担架无人车沿安全路径接近伤员位置并完成转运",
                        "在高风险区域预留备选撤离路径或分步中转点"
                    ],
                    "knowledge_trace": "任务与设备能力 → 先侦察后搬运的流程设计 → 形成时间与路径均可执行的救援方案。"
                },
                "team_formation": {
                    "title": "救助编组结果",
                    "summary": "综合前序分析，确定由1~2架医疗无人机与2台担架无人车组成的协同救援编组。",
                    "key_points": [
                        "为每台设备分配具体角色，如“前出侦察机”“急救包投放机”“主搬运车”“备用搬运车”",
                        "给出设备间的到达与撤离先后顺序，避免路线拥堵与冲突",
                        "形成可直接下发给调度模块的结构化编组描述"
                    ],
                    "knowledge_trace": "任务解析 + 设备匹配 + 数量与方式推理 → 汇总为可执行的救援编组蓝图。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "task", "label": "任务解析(两名伤员,X区域)", "type": "input"},
                            {"id": "equip", "label": "设备匹配(无人机/担架车/机器人)", "type": "process"},
                            {"id": "qty", "label": "数量计算(载荷+冗余)", "type": "process"},
                            {"id": "plan", "label": "救援方式规划", "type": "process"},
                            {"id": "team", "label": "编组方案输出", "type": "output"}
                        ],
                        "edges": [
                            {"source": "task", "target": "equip"},
                            {"source": "equip", "target": "qty"},
                            {"source": "qty", "target": "plan"},
                            {"source": "plan", "target": "team"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="casualty_remote_triage",  # 10. 远程伤情初步评估与分类
        model_name="伤员救助",
        name="远程伤情初步评估与分类",
        example_input="对X位置可能受伤的人员进行远程伤情初判",
        reasoning_chain="环境与风险解析（烟尘、水流、危险源）→ 视觉识别与姿态判断（倒地、出血、意识状态）→ 生命体征远程检测（基于远红外/毫米波估计呼吸和心率）→ 伤情分类与优先救援级别标注",
        prompt=(
            "【伤员救助-远程伤情初步评估专项要求】\n"
            "1. 行为树必须包含：environment_risk（解析烟尘、水流、危险源）→ "
            "visual_recognition（识别倒地、出血、意识状态）→ "
            "vital_signs_detection（基于远红外/毫米波估计呼吸和心率）→ "
            "triage_classification（伤情分类与优先救援级别，包含 knowledge_graph）。\n"
            "2. triage_classification 的 knowledge_graph 应体现：环境风险 → 视觉识别 → 生命体征 → 伤情分类。"
        ),
        example_output={
            "default_focus": "triage_classification",
            "behavior_tree": {
                "id": "environment_risk",
                "label": "🌫️ 环境与风险解析",
                "status": "completed",
                "summary": "分析X位置周边的烟尘、水流、危险源等远程环境信息，评估接近风险。",
                "children": [
                    {
                        "id": "visual_recognition",
                        "label": "视觉识别与姿态判断",
                        "status": "completed",
                        "summary": "通过无人机图像识别倒地、出血与意识状态等宏观伤情特征。",
                        "children": []
                    },
                    {
                        "id": "vital_signs_detection",
                        "label": "生命体征远程检测",
                        "status": "completed",
                        "summary": "利用远红外/毫米波对疑似伤员进行呼吸与心率估计。",
                        "children": []
                    },
                    {
                        "id": "triage_classification",
                        "label": "✅ 伤情分类与优先级标注",
                        "status": "active",
                        "summary": "综合环境风险、视觉特征与生命体征，对疑似伤员进行分级并标注优先救援级别。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "environment_risk": {
                    "title": "环境与风险解析",
                    "summary": "基于远程传感器与视频，分析现场是否存在烟尘、高温、水流或次生爆炸等风险。",
                    "key_points": [
                        "识别能见度受损区域和浓烟/粉尘分布",
                        "检测积水、急流或坍塌风险等环境威胁",
                        "评估是否适合无人平台立即靠近或需要先清除风险"
                    ],
                    "knowledge_trace": "环境数据采集 → 危险因子识别 → 形成现场风险等级评估。"
                },
                "visual_recognition": {
                    "title": "视觉识别与姿态判断",
                    "summary": "通过无人机视频流识别倒地人员、出血迹象与大致意识状态，为初步分级提供线索。",
                    "key_points": [
                        "检测人体轮廓与姿态，判断是否倒地不动或有自主活动",
                        "识别明显出血、血泊或异常体位（如四肢扭曲）",
                        "结合头部朝向与肢体反应判断可能的意识状态"
                    ],
                    "knowledge_trace": "视频帧解析 → 姿态与外观特征提取 → 输出视觉层面的伤情线索。"
                },
                "vital_signs_detection": {
                    "title": "生命体征远程检测",
                    "summary": "利用远红外成像和毫米波雷达估计疑似伤员的呼吸和心率。",
                    "key_points": [
                        "通过远红外检测胸腹部周期性温度变化以估计呼吸频率",
                        "使用毫米波在胸部区域测量微小位移以估计心率",
                        "对信号质量进行评估，过滤伪影与噪声"
                    ],
                    "knowledge_trace": "传感器数据采集 → 周期信号提取 → 估计呼吸/心率并给出置信度。"
                },
                "triage_classification": {
                    "title": "伤情分类与优先级标注",
                    "summary": "综合环境风险、视觉线索与生命体征，对疑似伤员进行“轻伤/中度伤/重伤”分类并标注优先救援级别。",
                    "key_points": [
                        "若检测到呼吸/心率显著异常或大量出血迹象，则标记为重伤，高优先级",
                        "若生命体征基本稳定且环境风险较低，可标记为轻伤或中度伤，次级优先",
                        "在环境风险极高时，即便伤情较重，也需同步考虑救援人员与设备安全"
                    ],
                    "knowledge_trace": "环境风险等级 + 视觉与体征线索 → 规则/模型推理 → 输出伤情分级与救援优先队列。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "env", "label": "环境风险", "type": "input"},
                            {"id": "visual", "label": "视觉伤情线索", "type": "input"},
                            {"id": "vital", "label": "生命体征估计", "type": "input"},
                            {"id": "triage", "label": "伤情分级与优先级", "type": "output"}
                        ],
                        "edges": [
                            {"source": "env", "target": "triage"},
                            {"source": "visual", "target": "triage"},
                            {"source": "vital", "target": "triage"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="casualty_near_field_assessment",  # 11. 过程/近程伤情评估
        model_name="伤员救助",
        name="近程伤情评估",
        example_input="无人救援车抵近X点后对伤员进行详细伤情检查",
        reasoning_chain="近距感知初始化（高清视觉、深度、红外）→ 重点部位识别（出血点、骨折可疑部位、胸腹部异常）→ 生命体征精细测量（血氧、心率、呼吸、体温）→ 伤情诊断与建议（止血、固定、搬运姿势调整等）",
        prompt=(
            "【伤员救助-近程伤情评估专项要求】\n"
            "1. 行为树必须包含：near_field_sensing（初始化高清视觉、深度、红外）→ "
            "key_area_identification（识别出血点、骨折可疑部位、胸腹部异常）→ "
            "precise_vital_signs（精细测量血氧、心率、呼吸、体温）→ "
            "diagnosis_recommendation（伤情诊断与建议，包含 knowledge_graph）。\n"
            "2. diagnosis_recommendation 的 knowledge_graph 应体现：近距感知 → 重点部位识别 → 精细测量 → 诊断建议。"
        ),
        example_output={
            "default_focus": "diagnosis_recommendation",
            "behavior_tree": {
                "id": "near_field_sensing",
                "label": "📹 近距感知初始化",
                "status": "completed",
                "summary": "在无人救援车抵近后，启动高清视觉、深度与红外感知，构建伤员近场环境模型。",
                "children": [
                    {
                        "id": "key_area_identification",
                        "label": "重点部位识别",
                        "status": "completed",
                        "summary": "识别出血点、骨折疑似部位以及胸腹部异常区域。",
                        "children": []
                    },
                    {
                        "id": "precise_vital_signs",
                        "label": "生命体征精细测量",
                        "status": "completed",
                        "summary": "通过专用传感器精确测量血氧、心率、呼吸频率与体温。",
                        "children": []
                    },
                    {
                        "id": "diagnosis_recommendation",
                        "label": "✅ 伤情诊断与救治建议",
                        "status": "active",
                        "summary": "基于综合评估给出止血、固定、搬运姿势调整等建议。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "near_field_sensing": {
                    "title": "近距感知初始化",
                    "summary": "在安全距离内展开传感器，对伤员周边环境与身体表征进行精细扫描。",
                    "key_points": [
                        "使用高清相机获取可见光图像，观察皮肤颜色和明显外伤",
                        "利用深度相机重建三维姿态与周边障碍布局",
                        "通过红外成像识别局部温度异常区域，如炎症或大出血"
                    ],
                    "knowledge_trace": "多模态传感器启动 → 空间与温度场重建 → 为后续重点部位识别提供基础。"
                },
                "key_area_identification": {
                    "title": "重点部位识别",
                    "summary": "在近场图像与三维模型中自动定位出血点、疑似骨折部位和胸腹部异常。",
                    "key_points": [
                        "基于颜色与纹理检测大面积出血或开放性伤口",
                        "通过肢体形变与非自然角度判断骨折或关节脱位可能",
                        "分析胸腹部起伏模式与轮廓，对可能的内伤或呼吸异常进行预警"
                    ],
                    "knowledge_trace": "图像与3D模型特征提取 → 出血/骨折/胸腹异常多通道检测 → 输出重点关注区域集合。"
                },
                "precise_vital_signs": {
                    "title": "生命体征精细测量",
                    "summary": "利用贴近式或短距离非接触传感器精确量化血氧、心率、呼吸与体温。",
                    "key_points": [
                        "使用指夹或额温/耳温探头获取高精度血氧与体温数据",
                        "通过心电或胸带式传感器测量心率和心律特征",
                        "结合胸腹运动与气流传感器统计呼吸频率与通气情况"
                    ],
                    "knowledge_trace": "传感器布置与接触 → 体征信号采集与滤波 → 输出标准化生命体征指标。"
                },
                "diagnosis_recommendation": {
                    "title": "伤情诊断与建议",
                    "summary": "综合重点受伤部位与生命体征信息，形成结构化初步诊断与救治建议。",
                    "key_points": [
                        "若存在大出血且血压/心率异常，优先建议止血与液体复苏",
                        "在疑似骨折情况下，推荐固定方式与搬运姿势以避免二次损伤",
                        "对于呼吸困难或意识不清等情况，标记为高危并给出快速撤离建议"
                    ],
                    "knowledge_trace": "重点部位 + 精细体征 → 规则/模型推理 → 生成可操作的急救与搬运行为建议。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "sense", "label": "近距感知结果", "type": "input"},
                            {"id": "areas", "label": "重点部位识别", "type": "process"},
                            {"id": "vitals", "label": "精细生命体征", "type": "process"},
                            {"id": "diag", "label": "伤情诊断与建议", "type": "output"}
                        ],
                        "edges": [
                            {"source": "sense", "target": "areas"},
                            {"source": "sense", "target": "vitals"},
                            {"source": "areas", "target": "diag"},
                            {"source": "vitals", "target": "diag"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="casualty_data_sync",  # 12. 伤情数据同步
        model_name="伤员救助",
        name="伤情数据同步",
        example_input="将X伤员的最新伤情数据同步至后方指挥所",
        reasoning_chain="数据结构整理（生命体征、伤情分级、位置）→ 通信链路选择（点对点、组网中继、卫星链路）→ 数据同步策略（周期同步、事件触发、异常加密传输）→ 同步确认（指挥端数据校验与时间戳比对）",
        prompt=(
            "【伤员救助-伤情数据同步专项要求】\n"
            "1. 行为树必须包含：data_structure（整理生命体征、伤情分级、位置）→ "
            "communication_selection（选择点对点、组网中继、卫星链路）→ "
            "sync_strategy（周期同步、事件触发、异常加密传输）→ "
            "sync_confirmation（指挥端数据校验与时间戳比对，包含 knowledge_graph）。\n"
            "2. sync_confirmation 的 knowledge_graph 应体现：数据整理 → 链路选择 → 同步策略 → 确认机制。"
        ),
        example_output={
            "default_focus": "sync_confirmation",
            "behavior_tree": {
                "id": "data_structure",
                "label": "🗂️ 数据结构整理",
                "status": "completed",
                "summary": "将X伤员的生命体征、伤情分级与地理位置整理为标准化数据结构。",
                "children": [
                    {
                        "id": "communication_selection",
                        "label": "通信链路选择",
                        "status": "completed",
                        "summary": "在点对点、组网中继与卫星链路中选择合适的传输路径组合。",
                        "children": []
                    },
                    {
                        "id": "sync_strategy",
                        "label": "数据同步策略",
                        "status": "completed",
                        "summary": "根据任务阶段与网络条件，配置周期同步、事件触发与异常加密传输策略。",
                        "children": []
                    },
                    {
                        "id": "sync_confirmation",
                        "label": "✅ 同步确认",
                        "status": "active",
                        "summary": "在指挥端对接收数据进行校验与时间戳比对，确认为最新有效状态。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "data_structure": {
                    "title": "数据结构整理",
                    "summary": "对来自远程与近程评估的多源伤情数据进行清洗与结构化，确保可在多终端间一致理解。",
                    "key_points": [
                        "统一生命体征、伤情分级与位置信息的字段命名和单位",
                        "合并多设备来源的数据，解决时间轴与标识不一致问题",
                        "为不同优先级信息打标签，支持按需增量同步"
                    ],
                    "knowledge_trace": "原始多源数据 → 字段对齐与清洗 → 形成标准化“伤情状态包”。"
                },
                "communication_selection": {
                    "title": "通信链路选择",
                    "summary": "在多种通信手段中，基于带宽、时延与可靠性要求选择最合适的链路组合。",
                    "key_points": [
                        "优先选择低时延高带宽链路，用于实时监控与语音/视频",
                        "在前线网络不稳定时，启用组网中继或卫星链路作为备份",
                        "为关键告警信息预留更可靠的链路路径"
                    ],
                    "knowledge_trace": "任务通信需求分析 → 候选链路能力评估 → 建立主链路+备链路配置。"
                },
                "sync_strategy": {
                    "title": "数据同步策略",
                    "summary": "根据任务节奏与网络状况，设计周期同步、事件触发与异常加密传输的组合策略。",
                    "key_points": [
                        "为常规状态信息配置较长周期的定时同步以节省带宽",
                        "对伤情突变或生命体征告警采用事件触发的即时同步",
                        "在异常或敌情威胁环境下，对敏感数据启用端到端加密与重传机制"
                    ],
                    "knowledge_trace": "数据重要性与频率评估 → 映射到周期/事件/异常传输模式 → 生成同步策略配置。"
                },
                "sync_confirmation": {
                    "title": "同步确认",
                    "summary": "在指挥端对接收的伤情数据进行完整性与时序性校验，确保救援决策基于最新信息。",
                    "key_points": [
                        "对比数据包中的时间戳与本地时间，检测延迟与乱序情况",
                        "使用校验和/签名确认数据在传输过程中未被篡改或丢失",
                        "当发现数据缺失或过期时，主动向前线节点请求重传或更新"
                    ],
                    "knowledge_trace": "接收数据 → 时间戳与完整性校验 → 标记为“最新有效/需更新/无效”并反馈结果。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "data", "label": "标准化伤情数据", "type": "input"},
                            {"id": "link", "label": "通信链路选择", "type": "process"},
                            {"id": "strategy", "label": "同步策略配置", "type": "process"},
                            {"id": "confirm", "label": "同步确认与回执", "type": "output"}
                        ],
                        "edges": [
                            {"source": "data", "target": "link"},
                            {"source": "data", "target": "strategy"},
                            {"source": "link", "target": "confirm"},
                            {"source": "strategy", "target": "confirm"}
                        ]
                    }
                }
            }
        },
    ),

    # 四、人员输送支援模型测试（13~16）
    Scenario(
        id="personnel_transport_formation",  # 13. 任务编组
        model_name="人员输送",
        name="任务编组",
        example_input="向X区域输送8名人员，需确保途中安全与舒适性",
        reasoning_chain="任务解析（乘员数量、随行物资、路况风险）→ 车辆类型匹配（选择人员运输无人车或越野运输平台）→ 数量计算（依据单车载员数推导需要的车辆数量）→ 搭载方案规划（座位分配、随行物资固定）",
        prompt=(
            "【人员输送-任务编组专项要求】\n"
            "1. 行为树必须包含：task_analysis（解析乘员数量、随行物资、路况风险）→ "
            "vehicle_matching（选择人员运输无人车或越野运输平台）→ "
            "quantity_calculation（依据单车载员数推导车辆数量）→ "
            "boarding_plan（规划座位分配、随行物资固定）→ "
            "formation_result（编组结果，包含 knowledge_graph）。\n"
            "2. formation_result 的 knowledge_graph 应体现：任务解析 → 车辆匹配 → 数量计算 → 搭载方案 → 编组结果。"
        ),
        example_output={
            "default_focus": "formation_result",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "🧍‍♀️🧍‍♂️ 任务解析：向X区域输送8名人员",
                "status": "completed",
                "summary": "解析乘员数量、随行物资与路况风险，为车辆选择和搭载方案提供约束。",
                "children": [
                    {
                        "id": "vehicle_matching",
                        "label": "车辆类型匹配",
                        "status": "completed",
                        "summary": "在人员运输无人车与越野运输平台中选择合适的组合。",
                        "children": []
                    },
                    {
                        "id": "quantity_calculation",
                        "label": "车辆数量计算",
                        "status": "completed",
                        "summary": "根据单车载员能力与随行物资体积推算所需车辆数量并预留冗余。",
                        "children": []
                    },
                    {
                        "id": "boarding_plan",
                        "label": "搭载方案规划",
                        "status": "completed",
                        "summary": "规划座位分配与随行物资固定位置，兼顾安全与舒适性。",
                        "children": []
                    },
                    {
                        "id": "formation_result",
                        "label": "✅ 输送编组结果",
                        "status": "active",
                        "summary": "确定若干辆人员运输车的编组与各车的乘员/物资分配方案。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务解析",
                    "summary": "围绕“向X区域输送8名人员，确保途中安全与舒适性”的目标，提取关键信息。",
                    "key_points": [
                        "统计实际乘员数量与角色分布（指挥、保障等）",
                        "确定随行物资种类与体积，如装备、医疗包、补给品",
                        "分析路况（山路、非铺装路面、涉水路段）对车辆与舒适性的影响"
                    ],
                    "knowledge_trace": "任务文本 → 乘员/物资/路况三类要素抽取 → 形成车辆与编组设计的输入条件。"
                },
                "vehicle_matching": {
                    "title": "车辆类型匹配",
                    "summary": "根据任务约束选择人员运输无人车或越野平台，必要时组合使用。",
                    "key_points": [
                        "若路况平顺且对舒适性要求高，优先选择专用人员运输无人车",
                        "在复杂地形或越野环境下，引入越野运输平台保证通过性",
                        "考虑车体悬挂与减振能力以保障乘坐舒适度"
                    ],
                    "knowledge_trace": "路况与舒适性需求 → 车辆能力对比 → 选定一类或多类车辆组合。"
                },
                "quantity_calculation": {
                    "title": "车辆数量计算",
                    "summary": "结合乘员数量、单车载员上限与物资占用空间计算车辆数，并考虑备份。",
                    "key_points": [
                        "按单车额定载员数初步计算理论车辆数量",
                        "为避免超载与保证舒适度，预留适当空座与物资空间",
                        "根据任务重要性增加1辆冗余车辆或规划二次往返方案"
                    ],
                    "knowledge_trace": "乘员与物资需求建模 → 按车辆上限约束求解最小车数 → 加入冗余安全系数。"
                },
                "boarding_plan": {
                    "title": "搭载方案规划",
                    "summary": "在已确定的车辆数量基础上，规划每辆车的乘员与物资分配。",
                    "key_points": [
                        "优先将行动不便或关键岗位人员安排在颠簸较小的位置",
                        "将重心偏高的物资放置在车体低位并进行固定",
                        "尽量将同任务小组成员安排在同一车辆或相邻车辆，便于协同"
                    ],
                    "knowledge_trace": "车辆编组结果 → 座位与货位资源映射 → 形成安全舒适的搭载方案。"
                },
                "formation_result": {
                    "title": "输送编组结果",
                    "summary": "输出包括车辆类型、数量、每车乘员与物资分配的完整编组方案。",
                    "key_points": [
                        "列出每辆车的车型、编号、负责运送的乘员名单与主要物资",
                        "说明编组设计中与安全和舒适度相关的关键考虑因素",
                        "生成可供后续路径规划与监控模块直接使用的结构化描述"
                    ],
                    "knowledge_trace": "任务解析 + 车辆匹配 + 数量计算 + 搭载规划 → 汇总为人员输送编组蓝图。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "task", "label": "任务解析(8名乘员,X区域)", "type": "input"},
                            {"id": "veh", "label": "车辆类型匹配", "type": "process"},
                            {"id": "qty", "label": "车辆数量计算", "type": "process"},
                            {"id": "board", "label": "搭载方案规划", "type": "process"},
                            {"id": "form", "label": "输送编组结果", "type": "output"}
                        ],
                        "edges": [
                            {"source": "task", "target": "veh"},
                            {"source": "task", "target": "qty"},
                            {"source": "veh", "target": "qty"},
                            {"source": "qty", "target": "board"},
                            {"source": "board", "target": "form"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="personnel_comfort_routing",  # 14. 舒适性导向路径规划
        model_name="人员输送",
        name="舒适连续导航路径规划",
        example_input="将人员运送至X点，优先选择颠簸最小的路线",
        reasoning_chain="路况综合解析（坡度、崎岖度、障碍密度）→ 舒适度模型评估（振动预测、加速度变化分析）→ 路径优选（选择起伏小、加减速稳定的路线）→ 动态调整（根据实时振动/颠簸感知进行微调）",
        prompt=(
            "【人员输送-舒适性导向路径规划专项要求】\n"
            "1. 行为树必须包含：road_condition_analysis（解析坡度、崎岖度、障碍密度）→ "
            "comfort_model（评估振动预测、加速度变化）→ "
            "route_optimization（选择起伏小、加减速稳定的路线）→ "
            "dynamic_adjustment（根据实时振动/颠簸感知进行微调，包含 knowledge_graph）。\n"
            "2. dynamic_adjustment 的 knowledge_graph 应体现：路况解析 → 舒适度评估 → 路径优选 → 动态调整。"
        ),
        example_output={
            "default_focus": "dynamic_adjustment",
            "behavior_tree": {
                "id": "road_condition_analysis",
                "label": "🛣️ 路况综合解析",
                "status": "completed",
                "summary": "分析通往X点的候选路段坡度、崎岖度与障碍密度。",
                "children": [
                    {
                        "id": "comfort_model",
                        "label": "舒适度模型评估",
                        "status": "completed",
                        "summary": "基于振动预测和加速度变化对不同候选路线的舒适度进行量化评估。",
                        "children": []
                    },
                    {
                        "id": "route_optimization",
                        "label": "路径优选",
                        "status": "completed",
                        "summary": "在满足安全和效率约束的前提下选择起伏小、加减速平顺的路线。",
                        "children": []
                    },
                    {
                        "id": "dynamic_adjustment",
                        "label": "✅ 动态舒适性调整",
                        "status": "active",
                        "summary": "根据实时振动/颠簸感知对行驶速度与局部路径进行微调。",
                        "children": [],
                        "control_meta": {
                            "control_type": "decentralized_rl",
                            "agent_scope": ["transport_vehicle"],
                            "policy_id": "comfort_dynamic_adjust_pi",
                            "algo_family": "DTDE_consistency_AC",
                            "training_scenario": "personnel_comfort_routing"
                        }
                    }
                ]
            },
            "node_insights": {
                "road_condition_analysis": {
                    "title": "路况综合解析",
                    "summary": "结合高精地图与在线感知信息，识别坡度大、坑洼多和障碍密集的区域。",
                    "key_points": [
                        "分析纵坡与横坡变化，检测陡坡和急弯路段",
                        "基于路面点云与振动历史数据识别颠簸区段",
                        "标注潜在障碍密集区域，为后续路径规避提供依据"
                    ],
                    "knowledge_trace": "地图+感知数据 → 路面特征提取 → 为舒适度评估提供路段标签。"
                },
                "comfort_model": {
                    "title": "舒适度模型评估",
                    "summary": "根据车辆动力学模型与历史振动数据，对候选路线的舒适度进行预测。",
                    "key_points": [
                        "利用车辆悬挂与车速模型预测不同路段的垂向加速度",
                        "结合乘员对振动频段敏感度构建舒适度评分函数",
                        "为每条候选路径计算综合舒适度指数"
                    ],
                    "knowledge_trace": "路段特征 + 车辆模型 → 振动与加速度预测 → 转化为舒适度评分。"
                },
                "route_optimization": {
                    "title": "路径优选",
                    "summary": "在安全、时间与舒适度三者之间做权衡，选择综合最优路线。",
                    "key_points": [
                        "过滤掉安全风险不可接受的路线",
                        "在剩余路径中以舒适度为主目标、时间为次目标进行多目标优化",
                        "可根据任务偏好调整“舒适度优先”或“效率优先”权重"
                    ],
                    "knowledge_trace": "候选路径 + 舒适度评分 → 多目标优化 → 选定主行驶路线。"
                },
                "dynamic_adjustment": {
                    "title": "动态舒适性调整",
                    "summary": "运行过程中利用实时振动/姿态数据对速度和局部路线进行在线微调。",
                    "key_points": [
                        "监测车辆纵向与垂向加速度，当超出舒适阈值时自动减速",
                        "在允许的范围内对车道内横向位置或微小绕行路径做优化",
                        "记录颠簸热点区域，为后续任务更新路况与舒适度模型"
                    ],
                    "knowledge_trace": "实时传感数据 → 与舒适度阈值对比 → 触发速度/路径微调控制指令；具体速度曲线与微小绕行动作由去中心化RL策略 comfort_dynamic_adjust_pi 在车辆智能体上在线生成，实现个体与全局舒适性的兼顾。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "road", "label": "路况解析结果", "type": "input"},
                            {"id": "model", "label": "舒适度模型评估", "type": "process"},
                            {"id": "route", "label": "静态路径优选", "type": "process"},
                            {"id": "realtime", "label": "实时振动/姿态感知", "type": "input"},
                            {"id": "adjust", "label": "动态行驶调整", "type": "output"}
                        ],
                        "edges": [
                            {"source": "road", "target": "model"},
                            {"source": "model", "target": "route"},
                            {"source": "route", "target": "adjust"},
                            {"source": "realtime", "target": "adjust"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="personnel_safety_monitor",  # 15. 人员与环境安全监控
        model_name="人员输送",
        name="人员与环境安全监控",
        example_input="运输途中需实时监控人员状态和外界潜在危险",
        reasoning_chain="乘员状态监控（安全带状态、姿态监测、体征波动）→ 环境风险感知（落石、积水、滑坡风险、车辆周界异常）→ 异常识别与处理（减速避让、停车保护、告警回传）→ 安全策略更新（基于实时风险调整行驶参数）",
        prompt=(
            "【人员输送-人员与环境安全监控专项要求】\n"
            "1. 行为树必须包含：passenger_monitoring（监控安全带状态、姿态、体征波动）→ "
            "environment_risk（感知落石、积水、滑坡风险、车辆周界异常）→ "
            "anomaly_handling（减速避让、停车保护、告警回传）→ "
            "safety_strategy_update（基于实时风险调整行驶参数，包含 knowledge_graph）。\n"
            "2. safety_strategy_update 的 knowledge_graph 应体现：乘员监控 → 环境风险 → 异常处理 → 策略更新。"
        ),
        example_output={
            "default_focus": "safety_strategy_update",
            "behavior_tree": {
                "id": "passenger_monitoring",
                "label": "🧑‍✈️ 乘员状态监控",
                "status": "completed",
                "summary": "实时监控安全带系紧情况、乘员姿态与体征波动，识别潜在风险。",
                "children": [
                    {
                        "id": "environment_risk",
                        "label": "环境风险感知",
                        "status": "completed",
                        "summary": "感知落石、积水、滑坡风险与车辆周界异常目标。",
                        "children": []
                    },
                    {
                        "id": "anomaly_handling",
                        "label": "异常识别与处理",
                        "status": "completed",
                        "summary": "对乘员或环境异常进行识别，并执行减速、避让或停车保护等措施。",
                        "children": []
                    },
                    {
                        "id": "safety_strategy_update",
                        "label": "✅ 安全策略更新",
                        "status": "active",
                        "summary": "基于实时风险自动调整行驶参数与告警策略。",
                        "children": [],
                        "control_meta": {
                            "control_type": "decentralized_rl",
                            "agent_scope": ["transport_vehicle"],
                            "policy_id": "safety_strategy_update_pi",
                            "algo_family": "DTDE_consistency_AC",
                            "training_scenario": "personnel_safety_monitor"
                        }
                    }
                ]
            },
            "node_insights": {
                "passenger_monitoring": {
                    "title": "乘员状态监控",
                    "summary": "通过车内摄像头与体征传感器监控乘员是否安全、舒适。",
                    "key_points": [
                        "检测安全带是否系好，姿态是否异常（如大幅晃动或跌倒）",
                        "监测心率、呼吸等体征是否出现应激反应",
                        "识别乘员中是否有人出现明显不适或急性症状"
                    ],
                    "knowledge_trace": "车内感知数据 → 安全与舒适指标计算 → 输出乘员风险等级。"
                },
                "environment_risk": {
                    "title": "环境风险感知",
                    "summary": "利用雷达、摄像头与环境传感器识别道路与周边风险。",
                    "key_points": [
                        "检测前方落石、塌方、积水和泥泞区域",
                        "识别路侧滑坡、悬崖等高危地形",
                        "监测车辆周界异常目标，如突然闯入的行人或其他车辆"
                    ],
                    "knowledge_trace": "外部感知数据 → 危险目标与地形特征识别 → 形成环境风险地图。"
                },
                "anomaly_handling": {
                    "title": "异常识别与处理",
                    "summary": "对乘员和环境的综合异常进行识别，并触发相应的应对策略。",
                    "key_points": [
                        "若前方存在高风险障碍，则减速、绕行或紧急制动",
                        "若乘员出现严重不适，可在安全位置停车并上报",
                        "将关键异常事件记录并回传指挥端以便后续分析"
                    ],
                    "knowledge_trace": "乘员风险 + 环境风险 → 异常级别评估 → 选择对应处置动作。"
                },
                "safety_strategy_update": {
                    "title": "安全策略更新",
                    "summary": "根据实时监测结果动态调整行驶参数与安全策略，以降低整体风险。",
                    "key_points": [
                        "在风险较高路段降低最高车速并提高安全距离",
                        "在乘员状态较差时偏向更平稳的加减速策略",
                        "在风险解除后逐步恢复常规行驶策略"
                    ],
                    "knowledge_trace": "异常处理结果反馈 → 更新速度、加速度与告警阈值 → 持续闭环优化安全策略；行驶参数与告警阈值的具体调整由去中心化RL策略 safety_strategy_update_pi 在车辆智能体侧基于本地观测与邻居信息分布式优化。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "pax", "label": "乘员状态监控", "type": "input"},
                            {"id": "env", "label": "环境风险感知", "type": "input"},
                            {"id": "anom", "label": "异常识别与处置", "type": "process"},
                            {"id": "policy", "label": "行驶安全策略", "type": "output"}
                        ],
                        "edges": [
                            {"source": "pax", "target": "anom"},
                            {"source": "env", "target": "anom"},
                            {"source": "anom", "target": "policy"},
                            {"source": "policy", "target": "pax"},
                            {"source": "policy", "target": "env"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="personnel_multi_destination_dispatch",  # 16. 多目的地协同调度
        model_name="人员输送",
        name="多目的地协同调度",
        example_input="需将人员A送至X点，人员B送至Y点，人员C送至Z点",
        reasoning_chain="任务拆解（人员与目的地映射）→ 路径代价计算（距离、时间、路况）→ 停靠顺序规划（基于总体效率的最优顺序）→ 多车协同（车辆分工、同步与交叉任务处理）",
        prompt=(
            "【人员输送-多目的地协同调度专项要求】\n"
            "1. 行为树必须包含：task_decomposition（人员与目的地映射）→ "
            "path_cost_calculation（计算距离、时间、路况代价）→ "
            "stop_sequence_planning（基于总体效率规划最优顺序）→ "
            "multi_vehicle_coordination（车辆分工、同步与交叉任务处理，包含 knowledge_graph）。\n"
            "2. multi_vehicle_coordination 的 knowledge_graph 应体现：任务拆解 → 路径代价 → 顺序规划 → 多车协同。"
        ),
        example_output={
            "default_focus": "multi_vehicle_coordination",
            "behavior_tree": {
                "id": "task_decomposition",
                "label": "📍 任务拆解：人员与目的地映射",
                "status": "completed",
                "summary": "将人员A/B/C与目的地X/Y/Z建立映射，形成多目的地任务集合。",
                "children": [
                    {
                        "id": "path_cost_calculation",
                        "label": "路径代价计算",
                        "status": "completed",
                        "summary": "计算各人员-目的地组合在不同车辆与路径下的距离、时间与路况代价。",
                        "children": []
                    },
                    {
                        "id": "stop_sequence_planning",
                        "label": "停靠顺序规划",
                        "status": "completed",
                        "summary": "在整体效率与约束条件下规划各车辆的停靠顺序。",
                        "children": []
                    },
                    {
                        "id": "multi_vehicle_coordination",
                        "label": "✅ 多车协同调度",
                        "status": "active",
                        "summary": "生成多车之间的任务分工与时间协调方案。",
                        "children": [],
                        "control_meta": {
                            "control_type": "decentralized_rl",
                            "agent_scope": ["vehicle_1", "vehicle_2", "vehicle_3"],
                            "policy_id": "multi_dest_dispatch_pi",
                            "algo_family": "DTDE_consistency_AC",
                            "training_scenario": "personnel_multi_destination_dispatch"
                        }
                    }
                ]
            },
            "node_insights": {
                "task_decomposition": {
                    "title": "任务拆解",
                    "summary": "将“一车多点”或“多车多点”的输送任务拆解为若干人员-目的地-时间窗子任务。",
                    "key_points": [
                        "为每名乘员记录起点、目的地与必须到达时间等约束",
                        "识别是否存在必须同行或禁止同行的乘员组合约束",
                        "将任务转化为适合路径与调度算法求解的结构化实例"
                    ],
                    "knowledge_trace": "自然语言任务 → 约束与目标提取 → 人员-目的地-时间窗任务集。"
                },
                "path_cost_calculation": {
                    "title": "路径代价计算",
                    "summary": "对不同车辆和可能路径，计算服务各子任务的综合代价。",
                    "key_points": [
                        "基于路网与路况估算行驶时间与里程",
                        "考虑坡度、路面情况等对能耗与舒适度的影响",
                        "构建多维代价函数（时间、距离、风险、舒适度）"
                    ],
                    "knowledge_trace": "路网与路况数据 → 单段路径代价 → 聚合得到车辆-任务组合代价矩阵。"
                },
                "stop_sequence_planning": {
                    "title": "停靠顺序规划",
                    "summary": "为每辆车规划在多个目的地之间的访问顺序，兼顾总时间与乘员体验。",
                    "key_points": [
                        "在满足时间窗约束的前提下最小化总行驶时间或里程",
                        "避免让同一乘员在车上绕行过多无关目的地",
                        "优先安排紧急或距离较近任务，减少等待时间"
                    ],
                    "knowledge_trace": "任务集 + 代价矩阵 → 车辆层面的TSP/VRP求解 → 得到停靠顺序。"
                },
                "multi_vehicle_coordination": {
                    "title": "多车协同调度",
                    "summary": "在各车辆停靠顺序基础上进行跨车协同，利用去中心化决策与信息一致性提升整体效率与鲁棒性。",
                    "key_points": [
                        "在多辆车之间分配人员与目的地任务，各车基于本地任务视角维护本地策略与代价估计",
                        "通过分布式通信在车辆间交换代价与任务负载信息，达到近似一致的全局调度视图",
                        "在此基础上去中心化地更新各车停靠与接驳策略，将最终结果转化为每辆车的时空轨迹与任务时间表"
                    ],
                    "knowledge_trace": "任务拆解 + 路径代价矩阵 → 各车本地调度策略与经验收集 → 分布式一致性聚合与策略更新 → 输出多车协同调度方案。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "decomp", "label": "任务拆解结果", "type": "input"},
                            {"id": "cost", "label": "路径代价矩阵", "type": "process"},
                            {"id": "local_policy", "label": "各车本地调度策略 π_i", "type": "process"},
                            {"id": "local_experience", "label": "本地执行轨迹与经验池 D_i", "type": "process"},
                            {"id": "consensus", "label": "分布式一致性信息聚合", "type": "process"},
                            {"id": "seq", "label": "车辆停靠顺序与任务分配", "type": "process"},
                            {"id": "coord", "label": "多车协同调度方案", "type": "output"}
                        ],
                        "edges": [
                            {"source": "decomp", "target": "cost"},
                            {"source": "cost", "target": "local_policy"},
                            {"source": "local_policy", "target": "local_experience"},
                            {"source": "local_experience", "target": "consensus"},
                            {"source": "consensus", "target": "seq"},
                            {"source": "decomp", "target": "seq"},
                            {"source": "seq", "target": "coord"}
                        ]
                    }
                }
            }
        },
    ),

    # 五、资源保障支援模型测试（17~20）
    Scenario(
        id="resource_tracking",  # 17. 资源追踪 / 资源建模
        model_name="资源保障",
        name="资源追踪",
        example_input="监控当前所有前线单位的物资状态",
        reasoning_chain="资源类别解析（弹药、食物、燃料、备件等）→ 追踪方式匹配（RFID、二维码、GPS、无人机盘点）→ 状态更新机制（位置、数量、消耗速率）→ 异常识别（资源丢失、库存异常、传感器失联）",
        prompt=(
            "【资源保障-资源追踪专项要求】\n"
            "1. 行为树必须包含：resource_category（解析弹药、食物、燃料、备件等）→ "
            "tracking_method（匹配RFID、二维码、GPS、无人机盘点）→ "
            "status_update（更新位置、数量、消耗速率）→ "
            "anomaly_detection（识别资源丢失、库存异常、传感器失联，包含 knowledge_graph）。\n"
            "2. anomaly_detection 的 knowledge_graph 应体现：资源类别 → 追踪方式 → 状态更新 → 异常识别。"
        ),
        example_output={
            "default_focus": "anomaly_detection",
            "behavior_tree": {
                "id": "resource_category",
                "label": "📦 资源类别解析",
                "status": "completed",
                "summary": "将前线单位使用的物资按弹药、食物、燃料、备件等类别进行结构化建模。",
                "children": [
                    {
                        "id": "tracking_method",
                        "label": "追踪方式匹配",
                        "status": "completed",
                        "summary": "为不同资源类别匹配合适的追踪手段，如RFID、二维码、GPS或无人机盘点。",
                        "children": []
                    },
                    {
                        "id": "status_update",
                        "label": "状态更新机制",
                        "status": "completed",
                        "summary": "设计位置、数量与消耗速率等状态字段的更新与存储机制。",
                        "children": []
                    },
                    {
                        "id": "anomaly_detection",
                        "label": "✅ 异常识别",
                        "status": "active",
                        "summary": "发现资源丢失、库存异常或传感器失联等异常情况并上报。",
                        "children": [],
                        "control_meta": {
                            "control_type": "decentralized_rl_consensus",
                            "agent_scope": ["depot_nodes", "frontline_nodes"],
                            "policy_id": "resource_anomaly_detection_pi",
                            "algo_family": "DTDE_consistency_Q_or_AC",
                            "training_scenario": "resource_tracking"
                        }
                    }
                ]
            },
            "node_insights": {
                "resource_category": {
                    "title": "资源类别解析",
                    "summary": "根据物资类型与用途对资源进行分组，为后续追踪与统计提供统一视图。",
                    "key_points": [
                        "将前线单位物资划分为弹药、食物、燃料、备件等主类",
                        "在每个大类下增加规格、批次与存储位置等子属性",
                        "为每件资源分配全局唯一标识符，便于跨区域追踪"
                    ],
                    "knowledge_trace": "原始物资清单 → 类别与属性抽取 → 形成资源建模字典。"
                },
                "tracking_method": {
                    "title": "追踪方式匹配",
                    "summary": "结合成本、精度与实时性，为不同类别资源选择合适的追踪技术。",
                    "key_points": [
                        "对高价值或关键资源优先配置RFID+GPS等组合追踪手段",
                        "对大宗低价值物资采用二维码盘点或无人机盘库",
                        "考虑战场环境对标签与设备可靠性的影响"
                    ],
                    "knowledge_trace": "资源类别 + 价值等级 → 追踪技术能力评估 → 选择一对多的标记与采集方案。"
                },
                "status_update": {
                    "title": "状态更新机制",
                    "summary": "定义资源位置、数量与消耗速率等关键字段的更新流程与触发条件。",
                    "key_points": [
                        "基于RFID/二维码扫描或盘点结果更新库存数量与位置",
                        "根据任务执行记录与加油/补给数据估算消耗速率",
                        "通过增量更新与时间戳机制保持多节点间状态一致"
                    ],
                    "knowledge_trace": "追踪读数 + 任务数据 → 字段级融合与覆盖策略 → 得到最新资源状态表。"
                },
                "anomaly_detection": {
                    "title": "异常识别",
                    "summary": "比较期望状态与实时状态，识别资源丢失、库存异常和传感器失联，并通过多节点去中心化协同提高判断鲁棒性。",
                    "key_points": [
                        "当账面数量与盘点结果差异超出阈值时标记为库存异常，各补给节点在本地先给出初步判定",
                        "利用去中心化一致性算法在多节点间交换与聚合异常线索，降低单点误报影响",
                        "在一致性判断的基础上触发资源丢失、库存异常或传感器失联的告警，并建议人工核查或自动补救"
                    ],
                    "knowledge_trace": "期望状态(模型) + 实时状态(追踪) → 各节点本地异常检测与轨迹记录 → 分布式一致性聚合 → 输出全局异常清单与告警等级。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "cat", "label": "资源类别模型", "type": "input"},
                            {"id": "track", "label": "追踪方式与读数(多节点)", "type": "process"},
                            {"id": "status", "label": "资源状态更新(本地视角)", "type": "process"},
                            {"id": "local_anom", "label": "本地异常检测结果", "type": "process"},
                            {"id": "consensus_anom", "label": "分布式一致性异常聚合", "type": "process"},
                            {"id": "anom", "label": "全局异常识别结果", "type": "output"}
                        ],
                        "edges": [
                            {"source": "cat", "target": "track"},
                            {"source": "track", "target": "status"},
                            {"source": "cat", "target": "status"},
                            {"source": "status", "target": "local_anom"},
                            {"source": "local_anom", "target": "consensus_anom"},
                            {"source": "consensus_anom", "target": "anom"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="resource_allocation",  # 18. 需求分配建议
        model_name="资源保障",
        name="需求分配建议",
        example_input="为A、B、C三个小队分配现有急救物资",
        reasoning_chain="需求解析（数量、紧急度、使用场景）→ 库存与可用量计算 → 分配策略推理（优先级分级、需求满足度、运输成本）→ 分配方案生成（分配比例与对应理由）",
        prompt=(
            "【资源保障-需求分配建议专项要求】\n"
            "1. 行为树必须包含：demand_analysis（解析数量、紧急度、使用场景）→ "
            "inventory_calculation（计算库存与可用量）→ "
            "allocation_strategy（推理优先级分级、需求满足度、运输成本）→ "
            "allocation_plan（生成分配比例与理由，包含 knowledge_graph）。\n"
            "2. allocation_plan 的 knowledge_graph 应体现：需求解析 → 库存计算 → 分配策略 → 方案生成。"
        ),
        example_output={
            "default_focus": "allocation_plan",
            "behavior_tree": {
                "id": "demand_analysis",
                "label": "📋 需求解析",
                "status": "completed",
                "summary": "解析A、B、C三个小队对急救物资的数量、紧急度与使用场景。",
                "children": [
                    {
                        "id": "inventory_calculation",
                        "label": "库存与可用量计算",
                        "status": "completed",
                        "summary": "统计当前中央与各前线仓的库存与可下发可用量。",
                        "children": []
                    },
                    {
                        "id": "allocation_strategy",
                        "label": "分配策略推理",
                        "status": "completed",
                        "summary": "综合任务优先级、需求满足度和运输成本，生成分配策略。",
                        "children": []
                    },
                    {
                        "id": "allocation_plan",
                        "label": "✅ 分配方案生成",
                        "status": "active",
                        "summary": "输出对各小队的分配比例与对应理由。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "demand_analysis": {
                    "title": "需求解析",
                    "summary": "将自然语言描述的物资需求转化为结构化的数量、紧急度与应用场景。",
                    "key_points": [
                        "识别各小队的当前任务类型（进攻、防御、救援等）",
                        "根据任务危险度与持续时间评估急救物资紧急度",
                        "将“不少于”“尽量满足”等模糊表达转化为可计算区间"
                    ],
                    "knowledge_trace": "任务描述与请求文本 → 需求字段抽取 → A/B/C小队的结构化需求列表。"
                },
                "inventory_calculation": {
                    "title": "库存与可用量计算",
                    "summary": "综合中央仓与沿线补给点的库存，计算可在指定时间内下发的有效可用量。",
                    "key_points": [
                        "统计各仓库当前库存及在途补给",
                        "扣除已锁定给其他任务的预分配资源",
                        "考虑有效期、环境适应性等约束，过滤不可用物资"
                    ],
                    "knowledge_trace": "库存数据库 + 任务锁定表 → 可用量计算 → 形成候选可分配资源池。"
                },
                "allocation_strategy": {
                    "title": "分配策略推理",
                    "summary": "在资源有限的情况下综合任务优先级、需求满足度与运输成本推导分配规则。",
                    "key_points": [
                        "根据任务优先级与伤亡风险为各小队分配权重",
                        "在权重约束下最大化整体需求满足度",
                        "在多个满足方案中选择运输成本更低的一组"
                    ],
                    "knowledge_trace": "需求列表 + 可用量 → 优先级加权优化 → 得到分配比例矩阵。"
                },
                "allocation_plan": {
                    "title": "分配方案生成",
                    "summary": "将分配结果转化为每个小队的具体物资数量与调配理由，便于指挥决策。",
                    "key_points": [
                        "量化列出A/B/C各自获得的物资数量与占总量的比例",
                        "解释关键决策原因，如“因任务紧急度更高获得更多配额”",
                        "输出可以被后续补给与调度模块直接读取的结构化结果"
                    ],
                    "knowledge_trace": "分配策略 + 可用资源 → 生成面向人/机双向友好的分配清单。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "dem", "label": "多单位需求解析", "type": "input"},
                            {"id": "inv", "label": "库存与可用量", "type": "input"},
                            {"id": "strat", "label": "分配策略推理", "type": "process"},
                            {"id": "plan", "label": "分配方案输出", "type": "output"}
                        ],
                        "edges": [
                            {"source": "dem", "target": "strat"},
                            {"source": "inv", "target": "strat"},
                            {"source": "strat", "target": "plan"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="resource_replenishment_dispatch",  # 19. 补给任务生成与调度
        model_name="资源保障",
        name="补给任务生成与调度",
        example_input="对X区域缺乏医疗物资，生成补给任务并安排运输",
        reasoning_chain="短缺资源识别（消耗异常、低库存预警）→ 补给任务构建（物资清单、目标位置、时限要求）→ 运输与调度规划（车辆匹配、路线规划、补给顺序）→ 任务执行检测与回传（补给确认、状态更新）",
        prompt=(
            "【资源保障-补给任务生成与调度专项要求】\n"
            "1. 行为树必须包含：shortage_identification（识别消耗异常、低库存预警）→ "
            "replenishment_task（构建物资清单、目标位置、时限要求）→ "
            "transport_planning（车辆匹配、路线规划、补给顺序）→ "
            "execution_monitoring（补给确认、状态更新，包含 knowledge_graph）。\n"
            "2. execution_monitoring 的 knowledge_graph 应体现：短缺识别 → 任务构建 → 运输规划 → 执行监控。"
        ),
        example_output={
            "default_focus": "execution_monitoring",
            "behavior_tree": {
                "id": "shortage_identification",
                "label": "🚨 短缺资源识别",
                "status": "completed",
                "summary": "识别X区域在医疗物资上的异常消耗与低库存预警。",
                "children": [
                    {
                        "id": "replenishment_task",
                        "label": "补给任务构建",
                        "status": "completed",
                        "summary": "根据缺口生成补给物资清单、目标位置与时限要求。",
                        "children": []
                    },
                    {
                        "id": "transport_planning",
                        "label": "运输与调度规划",
                        "status": "completed",
                        "summary": "为补给任务匹配车辆与路线，并规划补给顺序。",
                        "children": []
                    },
                    {
                        "id": "execution_monitoring",
                        "label": "✅ 任务执行检测与回传",
                        "status": "active",
                        "summary": "监控补给任务执行情况，完成后更新库存状态。",
                        "children": [],
                        "control_meta": {
                            "control_type": "decentralized_rl_consensus",
                            "agent_scope": ["supply_vehicles", "depots", "frontline_receivers"],
                            "policy_id": "replenishment_execution_monitor_pi",
                            "algo_family": "DTDE_consistency_AC",
                            "training_scenario": "resource_replenishment_dispatch"
                        }
                    }
                ]
            },
            "node_insights": {
                "shortage_identification": {
                    "title": "短缺资源识别",
                    "summary": "通过对消耗速率与库存阈值的持续监控，提前发现X区域的医疗物资短缺。",
                    "key_points": [
                        "分析历史消耗曲线，识别异常加速消耗段",
                        "对比当前库存与安全库存下限，触发低库存预警",
                        "结合任务计划预测未来一段时间内的缺口规模"
                    ],
                    "knowledge_trace": "历史消耗 + 当前库存 + 未来任务 → 短缺预测与告警。"
                },
                "replenishment_task": {
                    "title": "补给任务构建",
                    "summary": "将缺口信息转化为可执行的补给任务描述。",
                    "key_points": [
                        "根据缺口类型与等级生成细化物资清单与数量",
                        "指定补给目标位置、接收单位与完成时限",
                        "为任务分配优先级以指导调度资源分配"
                    ],
                    "knowledge_trace": "短缺预测结果 → 物资与时间约束 → 标准化补给任务实体。"
                },
                "transport_planning": {
                    "title": "运输与调度规划",
                    "summary": "为补给任务选择合适车辆、规划路线并排序多个补给点。",
                    "key_points": [
                        "根据物资体积与重量匹配合适的运输车辆与数量",
                        "在安全与效率约束下规划补给路线",
                        "若存在多个补给点，设计合理的停靠顺序"
                    ],
                    "knowledge_trace": "补给任务 + 车队资源 → 多目标路径与调度优化 → 生成运输计划。"
                },
                "execution_monitoring": {
                    "title": "任务执行检测与回传",
                    "summary": "在补给执行过程中持续跟踪进度并更新资源数据库。",
                    "key_points": [
                        "监控车辆位置与状态，判断是否按计划到达各补给点",
                        "在完成装卸后更新目标单位与源仓库库存",
                        "异常中断时生成告警并建议改派车辆或调整路线"
                    ],
                    "knowledge_trace": "车队执行数据 + 仓储变更记录 → 补给任务完成度评估与库存同步；跨车辆、仓库与前线接收单位的执行决策与状态一致性由去中心化RL一致性策略 replenishment_execution_monitor_pi 在各类智能体间通过分布式协同实现。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "short", "label": "短缺识别结果", "type": "input"},
                            {"id": "task", "label": "补给任务描述", "type": "process"},
                            {"id": "plan", "label": "运输与调度规划", "type": "process"},
                            {"id": "exec", "label": "执行监控与状态回传", "type": "output"}
                        ],
                        "edges": [
                            {"source": "short", "target": "task"},
                            {"source": "task", "target": "plan"},
                            {"source": "plan", "target": "exec"},
                            {"source": "exec", "target": "short"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="resource_consumption_forecast",  # 20. 资源消耗预测与规划
        model_name="资源保障",
        name="资源消耗预测与规划",
        example_input="预测未来72小时内X作业区的燃料需求",
        reasoning_chain="历史数据分析（消耗模式、任务类型）→ 环境与任务强度建模（温度、地形、操作负载）→ 消耗量预测（短期/中期预测曲线）→ 储备规划与建议（最小库存量、安全冗余、补给周期）",
        prompt=(
            "【资源保障-资源消耗预测与规划专项要求】\n"
            "1. 行为树必须包含：historical_analysis（分析消耗模式、任务类型）→ "
            "modeling（建模温度、地形、操作负载）→ "
            "consumption_forecast（预测短期/中期消耗曲线）→ "
            "reserve_planning（规划最小库存量、安全冗余、补给周期，包含 knowledge_graph）。\n"
            "2. reserve_planning 的 knowledge_graph 应体现：历史分析 → 环境建模 → 消耗预测 → 储备规划。"
        ),
        example_output={
            "default_focus": "reserve_planning",
            "behavior_tree": {
                "id": "historical_analysis",
                "label": "📈 历史数据分析",
                "status": "completed",
                "summary": "分析X作业区历史燃料消耗模式与任务类型分布。",
                "children": [
                    {
                        "id": "modeling",
                        "label": "环境与任务强度建模",
                        "status": "completed",
                        "summary": "建模未来72小时内的温度、地形与操作负载等影响因素。",
                        "children": []
                    },
                    {
                        "id": "consumption_forecast",
                        "label": "消耗量预测",
                        "status": "completed",
                        "summary": "生成短期/中期燃料消耗预测曲线。",
                        "children": []
                    },
                    {
                        "id": "reserve_planning",
                        "label": "✅ 储备规划与建议",
                        "status": "active",
                        "summary": "给出最小库存量、安全冗余与补给周期建议。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "historical_analysis": {
                    "title": "历史数据分析",
                    "summary": "基于历史记录识别X作业区燃料消耗与任务强度之间的关系。",
                    "key_points": [
                        "统计不同任务类型下单位时间燃料消耗水平",
                        "识别昼夜、季节或气候变化带来的消耗模式差异",
                        "发现极端任务或异常用油行为对整体曲线的影响"
                    ],
                    "knowledge_trace": "历史任务+用油数据 → 任务/时间/环境维度聚合 → 得到多场景消耗基线。"
                },
                "modeling": {
                    "title": "环境与任务强度建模",
                    "summary": "根据未来72小时的任务计划与环境预报构建消耗影响因子模型。",
                    "key_points": [
                        "引入温度、地形坡度、路况等环境变量",
                        "根据排班与任务计划推估车辆与设备启用强度",
                        "将上述因素映射为燃料消耗系数的动态调整因子"
                    ],
                    "knowledge_trace": "环境预报 + 任务计划 → 强度与环境因子 → 影响系数模型。"
                },
                "consumption_forecast": {
                    "title": "消耗量预测",
                    "summary": "在历史基线与未来因子模型的基础上，生成未来72小时燃料消耗预测。",
                    "key_points": [
                        "对不同时间段分别计算期望消耗区间与置信度",
                        "识别可能出现高峰消耗的时间窗口",
                        "提供多种情景（乐观/基线/保守）下的预测曲线"
                    ],
                    "knowledge_trace": "历史基线 + 影响系数 → 时间序列预测 → 形成多情景消耗曲线。"
                },
                "reserve_planning": {
                    "title": "储备规划与建议",
                    "summary": "基于预测结果规划最小库存、安全冗余与补给节奏。",
                    "key_points": [
                        "确定在任何时间点下不低于的最小安全库存量",
                        "按高峰消耗与补给不确定性设计冗余比例",
                        "给出补给批次与时间间隔建议，平衡仓储成本与安全性"
                    ],
                    "knowledge_trace": "消耗预测曲线 + 补给能力与风险偏好 → 库存与补给策略优化。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "hist", "label": "历史消耗分析", "type": "input"},
                            {"id": "env_model", "label": "环境与任务模型", "type": "process"},
                            {"id": "forecast", "label": "未来消耗预测", "type": "process"},
                            {"id": "reserve", "label": "库存与补给规划", "type": "output"}
                        ],
                        "edges": [
                            {"source": "hist", "target": "env_model"},
                            {"source": "env_model", "target": "forecast"},
                            {"source": "hist", "target": "forecast"},
                            {"source": "forecast", "target": "reserve"}
                        ]
                    }
                }
            }
        },
    ),

    # 六、后勤物资管控支援模型测试
    # 21. 资源入库
    Scenario(
        id="resource_inbound_processing",  # 21. 资源入库
        model_name="后勤物资管控",
        name="资源入库",
        example_input="新到达一批医疗物资X，需要入库保管。",
        reasoning_chain="物资属性解析（类型、数量、体积、保存条件）→ 仓储类型匹配（冷藏区/常温区/危险品区）→ 仓位推荐（按剩余容量、出入库频次、同类物资位置匹配）→ 入库登记（生成标签、记录批次与有效期）",
        prompt=(
            "【后勤物资管控-资源入库专项要求（详细输出版）】\n"
            "\n"
            "=== 一、行为树结构要求 ===\n"
            "1. 行为树必须至少包含以下核心节点，且严格按照推理链条自上而下展开：\n"
            "   - task_analysis（任务分析与解析，根节点）：\n"
            "       * 明确物资名称、数量、来源、入库时间要求等基础信息；\n"
            "       * 至少拆分出\"物资信息提取\"和\"入库需求识别\"两个子层级节点；\n"
            "   - material_attribute_parsing（物资属性解析）：\n"
            "       * 至少包含 type_identification（类型识别）、quantity_volume_analysis（数量体积分析）、storage_condition_analysis（保存条件分析）三个子节点；\n"
            "   - warehouse_type_matching（仓储类型匹配）：\n"
            "       * 根据物资属性匹配对应的仓储区域（冷藏区/常温区/危险品区/特殊存储区）；\n"
            "   - position_recommendation（仓位推荐，核心决策节点）：\n"
            "       * 下方必须细化出 capacity_analysis（剩余容量分析）、frequency_analysis（出入库频次分析）、similar_material_location（同类物资位置匹配）三个子节点；\n"
            "       * 该节点必须包含 knowledge_graph 字段。\n"
            "   - inventory_recording（入库登记）：\n"
            "       * 生成入库标签、记录批次号、有效期、登记时间等信息。\n"
            "\n"
            "2. behavior_tree 中每个节点的格式要求：\n"
            "   - label 字段：必须包含具体数值结果，格式示例：\"📦 物资属性解析：医疗物资X，数量50箱，体积2.5m³\"、\"✅ 仓储类型匹配：常温区\"、\"✅ 仓位推荐：A区-3号货架-2层\"；\n"
            "   - summary 字段：必须包含具体数值、数量、体积、位置等量化信息，不能使用空泛描述。例如：\n"
            "     * 正确示例：\"解析医疗物资X的属性：类型为急救药品，数量50箱，总体积2.5m³，需在常温（15-25℃）条件下保存，有效期至2025年12月。\"\n"
            "     * 错误示例：\"识别物资的基本属性\"（过于空泛，缺少具体数值）\n"
            "\n"
            "=== 二、knowledge_graph 要求 ===\n"
            "position_recommendation 节点的 knowledge_graph 必须体现完整因果链路：\n"
            "物资属性解析(material_parsing) → 仓储类型匹配(warehouse_matching) → 容量分析(capacity_analysis) → 频次分析(frequency_analysis) → 位置匹配(location_matching) → 仓位推荐(position_recommendation)\n"
            "\n"
            "具体要求：\n"
            "- nodes[].label 必须包含具体参数信息，格式：\"节点名称(具体参数1, 具体参数2, ...)\"\n"
            "  示例：\"物资属性解析(医疗物资X, 50箱, 2.5m³, 常温保存)\"、\"仓储类型匹配(常温区)\"、\"仓位推荐(A区-3号货架-2层)\"\n"
            "- nodes[].type 必须明确标注：input（输入）、process（处理）、decision（决策）、output（输出）\n"
            "- edges 必须明确表示推理方向，连接所有相关节点\n"
            "\n"
            "=== 三、node_insights 详细要求 ===\n"
            "为 behavior_tree 中出现的每一个节点（包括所有子节点）提供详细的 node_insights，每个节点包含：\n"
            "\n"
            "1. title：节点标题（简洁明确）\n"
            "\n"
            "2. summary：\n"
            "   - 具体数值（如：50箱、2.5m³、15-25℃、A区-3号货架等）\n"
            "   - 具体对象（如：医疗物资X、常温区、批次号等）\n"
            "   - 具体约束条件（如：有效期至2025年12月、需避光保存等）\n"
            "   - 不能使用\"合适的\"、\"一定的\"、\"若干\"等模糊词汇\n"
            "\n"
            "3. key_points：3-5条关键要点，每条必须：\n"
            "   - 包含具体数值或计算过程\n"
            "   - 对于分析类节点（material_attribute_parsing、warehouse_type_matching、position_recommendation、inventory_recording），必须包含：\n"
            "     * 解析假设（如：\"基于物资标签识别为医疗物资，类型为急救药品\"、\"根据保存条件要求匹配常温区\"）\n"
            "     * 计算或匹配逻辑（如：\"计算剩余容量 = 货架总容量 - 已占用容量\"、\"查询同类物资位置，优先推荐相邻仓位\"）\n"
            "     * 具体结果（如：\"推荐A区-3号货架-2层，剩余容量3.0m³，满足2.5m³需求\"）\n"
            "     * 验证条件（如：\"验证仓位满足温度要求（15-25℃）且距离同类物资较近\"）\n"
            "   - 每条 key_point 应该是一个完整的、可独立理解的句子，避免过于简短的短语\n"
            "\n"
            "4. knowledge_trace：知识追踪路径，必须：\n"
            "   - 使用箭头（→）连接各个推理步骤\n"
            "   - 包含具体的输入、处理过程、输出结果\n"
            "   - 体现完整的推理链条，格式示例：\"物资标签与单据信息 → 类型/数量/体积/保存条件要素提取 → 形成标准化的物资属性描述。\"\n"
            "   - 对于核心决策节点，knowledge_trace 应该体现：输入要素 → 中间推理步骤 → 最终输出结果\n"
            "\n"
            "=== 四、核心节点的特殊要求 ===\n"
            "对以下四个节点（material_attribute_parsing、warehouse_type_matching、position_recommendation、inventory_recording），必须提供可用于教学展示的详细分析/推理细节：\n"
            "\n"
            "- material_attribute_parsing：\n"
            "  * key_points 中必须包含：物资类型识别依据（如\"基于标签识别为医疗物资\"）、数量与体积计算（如\"50箱，单箱体积0.05m³，总体积2.5m³\"）、保存条件要求（如\"需在15-25℃常温保存，避光\"）、有效期信息\n"
            "\n"
            "- warehouse_type_matching：\n"
            "  * key_points 中必须包含：仓储区域选择依据（如\"根据保存条件15-25℃匹配常温区\"）、区域容量与当前占用情况、特殊要求匹配（如\"无需冷藏，无需危险品隔离\"）\n"
            "\n"
            "- position_recommendation：\n"
            "  * key_points 中必须包含：剩余容量计算（如\"A区-3号货架-2层剩余容量3.0m³，满足2.5m³需求\"）、出入库频次分析（如\"该区域月出入库频次15次，属于中等活跃度\"）、同类物资位置（如\"同类医疗物资位于A区-2号货架，推荐相邻位置\"）、最终推荐仓位及理由\n"
            "\n"
            "- inventory_recording：\n"
            "  * summary 和 key_points 必须整合上述三个节点的结果，形成完整的入库登记方案\n"
            "  * key_points 中必须包含：标签生成规则（如\"生成标签：MED-X-20241215-001\"）、批次号记录（如\"批次号：BATCH-20241215-50\"）、有效期记录（如\"有效期至2025年12月\"）、登记时间与操作人员信息\n"
            "  * knowledge_trace 必须体现：\"物资属性与仓储匹配结果 → 仓位推荐结果 → 生成入库标签与登记信息 → 完成入库登记\"\n"
            "\n"
            "=== 五、输出质量检查清单 ===\n"
            "生成内容后，请确保：\n"
            "□ 行为树至少包含两层结构（根节点有子节点，且至少一个子节点有子节点）\n"
            "□ 至少有一个 node_insights 内的节点包含 knowledge_graph\n"
            "□ 所有 label 包含具体数值和位置信息\n"
            "□ 所有 summary 包含具体数值而非空泛描述\n"
            "□ 所有 key_points 包含分析过程或具体参数\n"
            "□ 所有 knowledge_trace 使用箭头连接且包含具体步骤\n"
            "□ knowledge_graph 的 nodes label 包含参数信息\n"
            "□ 核心决策节点包含完整的推理细节"
        ),
        example_output={
            "default_focus": "position_recommendation",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "📦 资源入库：医疗物资X入库处理",
                "status": "completed",
                "summary": "解析任务：新到达一批医疗物资X，需要完成入库保管，包括物资属性识别、仓储区域匹配、仓位推荐与入库登记。",
                "children": [
                    {
                        "id": "material_attribute_parsing",
                        "label": "✅ 物资属性解析：医疗物资X，50箱，2.5m³",
                        "status": "completed",
                        "summary": "解析医疗物资X的属性：类型为急救药品，数量50箱，总体积2.5m³，需在常温（15-25℃）条件下保存，有效期至2025年12月，需避光。",
                        "children": [
                            {
                                "id": "type_identification",
                                "label": "类型识别：急救药品",
                                "status": "completed",
                                "summary": "基于物资标签与单据信息，识别为医疗物资中的急救药品类别，不属于危险品。",
                                "children": []
                            },
                            {
                                "id": "quantity_volume_analysis",
                                "label": "数量体积分析：50箱，2.5m³",
                                "status": "completed",
                                "summary": "统计物资数量为50箱，单箱体积0.05m³，总体积2.5m³，单箱重量约10kg，总重量约500kg。",
                                "children": []
                            },
                            {
                                "id": "storage_condition_analysis",
                                "label": "保存条件分析：常温15-25℃，避光",
                                "status": "completed",
                                "summary": "分析保存条件：需在15-25℃常温环境下保存，需避光，湿度要求60-70%，有效期至2025年12月。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "warehouse_type_matching",
                        "label": "✅ 仓储类型匹配：常温区",
                        "status": "completed",
                        "summary": "根据保存条件15-25℃匹配常温仓储区，该区域当前可用容量充足，温度控制稳定在20±2℃。",
                        "children": []
                    },
                    {
                        "id": "position_recommendation",
                        "label": "✅ 仓位推荐：A区-3号货架-2层",
                        "status": "active",
                        "summary": "推荐A区-3号货架-2层作为入库仓位，该位置剩余容量3.0m³（满足2.5m³需求），月出入库频次15次（中等活跃度），同类医疗物资位于相邻A区-2号货架，便于统一管理。",
                        "children": [
                            {
                                "id": "capacity_analysis",
                                "label": "剩余容量分析：3.0m³可用",
                                "status": "completed",
                                "summary": "分析A区-3号货架-2层：总容量5.0m³，已占用2.0m³，剩余容量3.0m³，满足2.5m³入库需求，且有0.5m³余量。",
                                "children": []
                            },
                            {
                                "id": "frequency_analysis",
                                "label": "出入库频次分析：月15次",
                                "status": "completed",
                                "summary": "统计该区域月出入库频次为15次，属于中等活跃度，适合存放常用医疗物资，便于快速取用。",
                                "children": []
                            },
                            {
                                "id": "similar_material_location",
                                "label": "同类物资位置匹配：A区-2号货架",
                                "status": "completed",
                                "summary": "查询同类医疗物资（急救药品）位于A区-2号货架，推荐相邻的A区-3号货架，便于统一管理与快速定位。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "inventory_recording",
                        "label": "✅ 入库登记：标签MED-X-20241215-001",
                        "status": "completed",
                        "summary": "生成入库标签MED-X-20241215-001，记录批次号BATCH-20241215-50，有效期至2025年12月，登记时间2024年12月15日14:30，操作人员系统自动登记。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务分析与解析",
                    "summary": "对\"新到达一批医疗物资X，需要入库保管\"的任务进行结构化解析，明确物资名称、数量、入库时间要求等基础信息。",
                    "key_points": [
                        "抽取任务要素：医疗物资X、新到达、需要入库保管",
                        "识别入库紧迫性：常规入库，无紧急时间要求",
                        "为后续物资属性解析与仓储匹配提供统一的数据输入框架"
                    ],
                    "knowledge_trace": "任务文本解析 → 物资名称/数量/时间要素抽取 → 形成可供后续节点复用的标准任务描述。"
                },
                "material_attribute_parsing": {
                    "title": "物资属性解析",
                    "summary": "解析医疗物资X的属性：类型为急救药品，数量50箱，总体积2.5m³，需在常温（15-25℃）条件下保存，有效期至2025年12月，需避光。",
                    "key_points": [
                        "基于物资标签与单据信息识别为医疗物资中的急救药品类别，不属于危险品",
                        "统计物资数量为50箱，单箱体积0.05m³，总体积2.5m³，单箱重量约10kg，总重量约500kg",
                        "分析保存条件：需在15-25℃常温环境下保存，需避光，湿度要求60-70%，有效期至2025年12月",
                        "提取批次信息：生产日期2024年6月，批次号BATCH-20241215-50"
                    ],
                    "knowledge_trace": "物资标签与单据信息 → 类型/数量/体积/保存条件要素提取 → 形成标准化的物资属性描述。"
                },
                "type_identification": {
                    "title": "类型识别",
                    "summary": "基于物资标签与单据信息，识别为医疗物资中的急救药品类别，不属于危险品。",
                    "key_points": [
                        "读取物资标签信息，识别物资类别编码为MED-001（医疗物资）",
                        "进一步识别子类别为急救药品，不属于需要特殊隔离的危险品",
                        "匹配物资分类标准，确定应归类为\"医疗物资-急救药品\"类别"
                    ],
                    "knowledge_trace": "标签信息读取 → 类别编码识别 → 子类别匹配 → 确定物资类型。"
                },
                "quantity_volume_analysis": {
                    "title": "数量体积分析",
                    "summary": "统计物资数量为50箱，单箱体积0.05m³，总体积2.5m³，单箱重量约10kg，总重量约500kg。",
                    "key_points": [
                        "清点物资数量：共50箱，每箱规格统一",
                        "测量单箱体积：长×宽×高 = 0.4m × 0.3m × 0.42m ≈ 0.05m³",
                        "计算总体积：50箱 × 0.05m³/箱 = 2.5m³",
                        "估算重量：单箱约10kg，总重量约500kg"
                    ],
                    "knowledge_trace": "数量清点 → 单箱体积测量 → 总体积计算 → 重量估算。"
                },
                "storage_condition_analysis": {
                    "title": "保存条件分析",
                    "summary": "分析保存条件：需在15-25℃常温环境下保存，需避光，湿度要求60-70%，有效期至2025年12月。",
                    "key_points": [
                        "提取温度要求：15-25℃常温保存，无需冷藏或冷冻",
                        "识别特殊要求：需避光保存，避免阳光直射",
                        "湿度要求：60-70%相对湿度，需在干燥通风环境",
                        "有效期信息：生产日期2024年6月，有效期18个月，有效期至2025年12月"
                    ],
                    "knowledge_trace": "保存条件标签读取 → 温度/湿度/光照要求提取 → 有效期计算 → 形成保存条件规范。"
                },
                "warehouse_type_matching": {
                    "title": "仓储类型匹配",
                    "summary": "根据保存条件15-25℃匹配常温仓储区，该区域当前可用容量充足，温度控制稳定在20±2℃。",
                    "key_points": [
                        "根据保存条件15-25℃匹配常温仓储区（无需冷藏区或危险品区）",
                        "查询常温区当前状态：总容量500m³，已占用300m³，可用容量200m³，容量充足",
                        "验证温度控制：常温区温度稳定在20±2℃，满足15-25℃要求",
                        "确认无需特殊隔离：不属于危险品，无需单独隔离存储"
                    ],
                    "knowledge_trace": "保存条件要求 → 仓储区域类型匹配 → 容量与温度验证 → 确定仓储区域。"
                },
                "position_recommendation": {
                    "title": "仓位推荐",
                    "summary": "推荐A区-3号货架-2层作为入库仓位，该位置剩余容量3.0m³（满足2.5m³需求），月出入库频次15次（中等活跃度），同类医疗物资位于相邻A区-2号货架，便于统一管理。",
                    "key_points": [
                        "计算A区-3号货架-2层剩余容量：总容量5.0m³ - 已占用2.0m³ = 剩余3.0m³，满足2.5m³需求且有0.5m³余量",
                        "分析出入库频次：该区域月出入库频次15次，属于中等活跃度，适合存放常用医疗物资",
                        "查询同类物资位置：同类医疗物资（急救药品）位于A区-2号货架，推荐相邻A区-3号货架便于统一管理",
                        "验证仓位条件：A区-3号货架-2层满足温度（20±2℃）、避光、湿度（65%）要求，距离同类物资较近"
                    ],
                    "knowledge_trace": "物资属性与仓储区域 → 剩余容量计算 → 频次与同类物资位置分析 → 形成仓位推荐方案。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "material_parsing", "label": "物资属性解析(医疗物资X, 50箱, 2.5m³, 常温保存)", "type": "input"},
                            {"id": "warehouse_matching", "label": "仓储类型匹配(常温区)", "type": "process"},
                            {"id": "capacity_analysis", "label": "容量分析(A区-3号货架-2层, 剩余3.0m³)", "type": "process"},
                            {"id": "frequency_analysis", "label": "频次分析(月15次, 中等活跃度)", "type": "process"},
                            {"id": "location_matching", "label": "位置匹配(同类物资A区-2号货架)", "type": "process"},
                            {"id": "position_recommendation", "label": "仓位推荐(A区-3号货架-2层)", "type": "output"}
                        ],
                        "edges": [
                            {"source": "material_parsing", "target": "warehouse_matching"},
                            {"source": "warehouse_matching", "target": "capacity_analysis"},
                            {"source": "capacity_analysis", "target": "frequency_analysis"},
                            {"source": "frequency_analysis", "target": "location_matching"},
                            {"source": "location_matching", "target": "position_recommendation"}
                        ]
                    }
                },
                "capacity_analysis": {
                    "title": "剩余容量分析",
                    "summary": "分析A区-3号货架-2层：总容量5.0m³，已占用2.0m³，剩余容量3.0m³，满足2.5m³入库需求，且有0.5m³余量。",
                    "key_points": [
                        "查询货架容量：A区-3号货架-2层总容量5.0m³",
                        "统计已占用容量：当前已存放物资占用2.0m³",
                        "计算剩余容量：5.0m³ - 2.0m³ = 3.0m³",
                        "验证容量充足：3.0m³ > 2.5m³，满足入库需求，且有0.5m³余量便于后续调整"
                    ],
                    "knowledge_trace": "货架容量查询 → 已占用容量统计 → 剩余容量计算 → 容量充足性验证。"
                },
                "frequency_analysis": {
                    "title": "出入库频次分析",
                    "summary": "统计该区域月出入库频次为15次，属于中等活跃度，适合存放常用医疗物资，便于快速取用。",
                    "key_points": [
                        "统计历史数据：A区-3号货架区域近3个月平均月出入库频次15次",
                        "活跃度评估：15次/月属于中等活跃度（低活跃<10次，中等10-20次，高活跃>20次）",
                        "适用性判断：中等活跃度适合存放常用医疗物资，既保证快速取用又避免过度频繁操作",
                        "同类物资参考：同类医疗物资所在A区-2号货架月频次18次，活跃度相近"
                    ],
                    "knowledge_trace": "历史出入库数据统计 → 活跃度等级评估 → 适用性判断 → 形成频次分析结论。"
                },
                "similar_material_location": {
                    "title": "同类物资位置匹配",
                    "summary": "查询同类医疗物资（急救药品）位于A区-2号货架，推荐相邻的A区-3号货架，便于统一管理与快速定位。",
                    "key_points": [
                        "查询同类物资：在库存系统中查询同类医疗物资（急救药品）的存储位置",
                        "定位同类物资：发现同类物资主要位于A区-2号货架，共存放约30箱同类急救药品",
                        "推荐相邻位置：推荐相邻的A区-3号货架，距离A区-2号货架仅5米，便于统一管理",
                        "管理优势：同类物资集中存放便于快速定位、统一管理、减少查找时间"
                    ],
                    "knowledge_trace": "同类物资查询 → 位置定位 → 相邻仓位推荐 → 形成位置匹配方案。"
                },
                "inventory_recording": {
                    "title": "入库登记",
                    "summary": "生成入库标签MED-X-20241215-001，记录批次号BATCH-20241215-50，有效期至2025年12月，登记时间2024年12月15日14:30，操作人员系统自动登记。",
                    "key_points": [
                        "生成入库标签：按照规则生成标签MED-X-20241215-001（MED表示医疗物资，X为物资名称，20241215为日期，001为序号）",
                        "记录批次信息：批次号BATCH-20241215-50，生产日期2024年6月，有效期至2025年12月",
                        "登记时间信息：入库登记时间2024年12月15日14:30，操作人员系统自动登记",
                        "同步库存系统：将入库信息同步至库存管理系统，更新库存数量、仓位占用、有效期预警等数据"
                    ],
                    "knowledge_trace": "物资属性与仓储匹配结果 → 仓位推荐结果 → 生成入库标签与登记信息 → 完成入库登记并同步系统。"
                }
            }
        },
    ),
    # 22. 资源盘点
    Scenario(
        id="resource_inventory_check",  # 22. 资源盘点
        model_name="后勤物资管控",
        name="资源盘点",
        example_input="对食品与医疗物资进行周期性盘点，确保数据一致。",
        reasoning_chain="库存数据解析（账面数量、实际传感数量）→ 盘点策略制定（优先检查消耗快的品类）→ 差异检测（短缺、过期、误放）→ 异常定位（原因分析，如运输损耗、登记错误、未记录的应急领取）",
        prompt=(
            "【后勤物资管控-资源盘点专项要求（详细输出版）】\n"
            "\n"
            "=== 一、行为树结构要求 ===\n"
            "1. 行为树必须至少包含以下核心节点，且严格按照推理链条自上而下展开：\n"
            "   - task_analysis（任务分析与解析，根节点）：\n"
            "       * 明确盘点范围、盘点类型（周期性/全面/抽查）、时间要求等基础信息；\n"
            "       * 至少拆分出\"盘点范围识别\"和\"盘点类型确定\"两个子层级节点；\n"
            "   - inventory_data_parsing（库存数据解析）：\n"
            "       * 至少包含 book_quantity_analysis（账面数量分析）、sensor_quantity_analysis（实际传感数量分析）、data_comparison（数据对比）三个子节点；\n"
            "   - inventory_strategy_formulation（盘点策略制定）：\n"
            "       * 根据物资类型、消耗速度、重要性等因素制定盘点优先级和策略；\n"
            "   - difference_detection（差异检测，核心决策节点）：\n"
            "       * 下方必须细化出 shortage_detection（短缺检测）、expiry_detection（过期检测）、misplacement_detection（误放检测）三个子节点；\n"
            "       * 该节点必须包含 knowledge_graph 字段。\n"
            "   - anomaly_localization（异常定位）：\n"
            "       * 分析差异原因，如运输损耗、登记错误、未记录的应急领取等。\n"
            "\n"
            "2. behavior_tree 中每个节点的格式要求：\n"
            "   - label 字段：必须包含具体数值结果，格式示例：\"📊 库存数据解析：账面120箱，实际115箱\"、\"✅ 盘点策略制定：优先食品类\"、\"✅ 差异检测：短缺5箱，过期3箱\"；\n"
            "   - summary 字段：必须包含具体数值、数量、差异等量化信息，不能使用空泛描述。例如：\n"
            "     * 正确示例：\"对比账面数量120箱与实际传感数量115箱，发现短缺5箱，差异率4.2%，同时检测到3箱物资已过期。\"\n"
            "     * 错误示例：\"发现库存存在差异\"（过于空泛，缺少具体数值）\n"
            "\n"
            "=== 二、knowledge_graph 要求 ===\n"
            "difference_detection 节点的 knowledge_graph 必须体现完整因果链路：\n"
            "库存数据解析(inventory_parsing) → 盘点策略制定(strategy_formulation) → 短缺检测(shortage_detection) → 过期检测(expiry_detection) → 误放检测(misplacement_detection) → 差异汇总(difference_summary)\n"
            "\n"
            "具体要求：\n"
            "- nodes[].label 必须包含具体参数信息，格式：\"节点名称(具体参数1, 具体参数2, ...)\"\n"
            "  示例：\"库存数据解析(账面120箱, 实际115箱)\"、\"差异检测(短缺5箱, 过期3箱)\"、\"异常定位(运输损耗, 登记错误)\"\n"
            "- nodes[].type 必须明确标注：input（输入）、process（处理）、decision（决策）、output（输出）\n"
            "- edges 必须明确表示推理方向，连接所有相关节点\n"
            "\n"
            "=== 三、node_insights 详细要求 ===\n"
            "为 behavior_tree 中出现的每一个节点（包括所有子节点）提供详细的 node_insights，每个节点包含：\n"
            "\n"
            "1. title：节点标题（简洁明确）\n"
            "\n"
            "2. summary：\n"
            "   - 具体数值（如：120箱、115箱、5箱、4.2%、3箱等）\n"
            "   - 具体对象（如：食品类、医疗物资、A区-3号货架等）\n"
            "   - 具体差异类型（如：短缺、过期、误放等）\n"
            "   - 不能使用\"合适的\"、\"一定的\"、\"若干\"等模糊词汇\n"
            "\n"
            "3. key_points：3-5条关键要点，每条必须：\n"
            "   - 包含具体数值或计算过程\n"
            "   - 对于分析类节点（inventory_data_parsing、inventory_strategy_formulation、difference_detection、anomaly_localization），必须包含：\n"
            "     * 解析假设（如：\"基于库存系统查询账面数量\"、\"通过RFID传感器读取实际数量\"）\n"
            "     * 计算或对比逻辑（如：\"计算差异 = 账面数量 - 实际数量\"、\"差异率 = 差异数量 ÷ 账面数量 × 100%\"）\n"
            "     * 具体结果（如：\"发现短缺5箱，差异率4.2%\"、\"检测到3箱物资已过期\"）\n"
            "     * 验证条件（如：\"验证差异是否在合理范围内（±5%）\"、\"检查过期物资是否已隔离\"）\n"
            "   - 每条 key_point 应该是一个完整的、可独立理解的句子，避免过于简短的短语\n"
            "\n"
            "4. knowledge_trace：知识追踪路径，必须：\n"
            "   - 使用箭头（→）连接各个推理步骤\n"
            "   - 包含具体的输入、处理过程、输出结果\n"
            "   - 体现完整的推理链条，格式示例：\"库存系统数据查询 → 账面数量提取 → 传感器数据读取 → 实际数量统计 → 数据对比分析。\"\n"
            "   - 对于核心决策节点，knowledge_trace 应该体现：输入要素 → 中间推理步骤 → 最终输出结果\n"
            "\n"
            "=== 四、核心节点的特殊要求 ===\n"
            "对以下四个节点（inventory_data_parsing、inventory_strategy_formulation、difference_detection、anomaly_localization），必须提供可用于教学展示的详细分析/推理细节：\n"
            "\n"
            "- inventory_data_parsing：\n"
            "  * key_points 中必须包含：账面数量来源（如\"从库存系统查询账面数量120箱\"）、实际数量获取方式（如\"通过RFID传感器读取实际数量115箱\"）、数据对比方法（如\"计算差异 = 120 - 115 = 5箱\"）、差异率计算（如\"差异率 = 5 ÷ 120 × 100% = 4.2%\"）\n"
            "\n"
            "- inventory_strategy_formulation：\n"
            "  * key_points 中必须包含：盘点优先级排序依据（如\"食品类消耗快，优先盘点\"）、盘点范围确定（如\"重点盘点食品与医疗物资，其他物资抽查\"）、盘点方法选择（如\"全面盘点食品类，抽样盘点其他类\"）\n"
            "\n"
            "- difference_detection：\n"
            "  * key_points 中必须包含：短缺数量计算（如\"账面120箱 - 实际115箱 = 短缺5箱\"）、过期物资检测（如\"检测到3箱物资有效期已过\"）、误放物资识别（如\"发现2箱物资位置与登记不符\"）、差异汇总（如\"总计差异：短缺5箱，过期3箱，误放2箱\"）\n"
            "\n"
            "- anomaly_localization：\n"
            "  * summary 和 key_points 必须整合上述三个节点的结果，形成完整的异常定位分析\n"
            "  * key_points 中必须包含：差异原因分析（如\"短缺5箱可能因运输损耗2箱、登记错误2箱、未记录应急领取1箱\"）、过期原因分析（如\"3箱过期因未及时使用且未设置预警\"）、误放原因分析（如\"2箱误放因入库时登记错误\"）、处理建议（如\"建议加强运输管理、完善登记流程、设置有效期预警\"）\n"
            "  * knowledge_trace 必须体现：\"差异检测结果 → 原因分析（运输损耗/登记错误/应急领取） → 形成异常定位报告与处理建议\"\n"
            "\n"
            "=== 五、输出质量检查清单 ===\n"
            "生成内容后，请确保：\n"
            "□ 行为树至少包含两层结构（根节点有子节点，且至少一个子节点有子节点）\n"
            "□ 至少有一个 node_insights 内的节点包含 knowledge_graph\n"
            "□ 所有 label 包含具体数值和差异信息\n"
            "□ 所有 summary 包含具体数值而非空泛描述\n"
            "□ 所有 key_points 包含分析过程或具体参数\n"
            "□ 所有 knowledge_trace 使用箭头连接且包含具体步骤\n"
            "□ knowledge_graph 的 nodes label 包含参数信息\n"
            "□ 核心决策节点包含完整的推理细节"
        ),
        example_output={
            "default_focus": "difference_detection",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "📊 资源盘点：食品与医疗物资周期性盘点",
                "status": "completed",
                "summary": "解析任务：对食品与医疗物资进行周期性盘点，确保账面数据与实际库存数据一致，识别差异并定位异常原因。",
                "children": [
                    {
                        "id": "inventory_data_parsing",
                        "label": "✅ 库存数据解析：账面120箱，实际115箱",
                        "status": "completed",
                        "summary": "对比账面数量120箱与实际传感数量115箱，发现短缺5箱，差异率4.2%，同时检测到3箱物资已过期，2箱物资位置与登记不符。",
                        "children": [
                            {
                                "id": "book_quantity_analysis",
                                "label": "账面数量分析：120箱",
                                "status": "completed",
                                "summary": "从库存系统查询食品与医疗物资的账面数量：食品类80箱，医疗物资类40箱，合计120箱。",
                                "children": []
                            },
                            {
                                "id": "sensor_quantity_analysis",
                                "label": "实际传感数量分析：115箱",
                                "status": "completed",
                                "summary": "通过RFID传感器读取实际库存数量：食品类77箱，医疗物资类38箱，合计115箱。",
                                "children": []
                            },
                            {
                                "id": "data_comparison",
                                "label": "数据对比：差异5箱，差异率4.2%",
                                "status": "completed",
                                "summary": "计算差异：账面120箱 - 实际115箱 = 短缺5箱，差异率 = 5 ÷ 120 × 100% = 4.2%，超出合理范围（±2%）。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "inventory_strategy_formulation",
                        "label": "✅ 盘点策略制定：优先食品类",
                        "status": "completed",
                        "summary": "制定盘点策略：食品类消耗快、易过期，优先进行全面盘点；医疗物资类进行重点抽查，重点关注有效期和位置准确性。",
                        "children": []
                    },
                    {
                        "id": "difference_detection",
                        "label": "✅ 差异检测：短缺5箱，过期3箱，误放2箱",
                        "status": "active",
                        "summary": "检测到三类差异：短缺5箱（账面120箱 - 实际115箱），过期3箱（有效期已过），误放2箱（位置与登记不符），总计差异10箱。",
                        "children": [
                            {
                                "id": "shortage_detection",
                                "label": "短缺检测：5箱",
                                "status": "completed",
                                "summary": "检测到短缺5箱：食品类短缺3箱（账面80箱 - 实际77箱），医疗物资类短缺2箱（账面40箱 - 实际38箱）。",
                                "children": []
                            },
                            {
                                "id": "expiry_detection",
                                "label": "过期检测：3箱",
                                "status": "completed",
                                "summary": "检测到3箱物资已过期：食品类2箱（有效期至2024年11月，已过期1个月），医疗物资类1箱（有效期至2024年10月，已过期2个月）。",
                                "children": []
                            },
                            {
                                "id": "misplacement_detection",
                                "label": "误放检测：2箱",
                                "status": "completed",
                                "summary": "检测到2箱物资位置与登记不符：食品类1箱（登记在A区-1号货架，实际在A区-3号货架），医疗物资类1箱（登记在B区-2号货架，实际在B区-5号货架）。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "anomaly_localization",
                        "label": "✅ 异常定位：运输损耗2箱，登记错误3箱，应急领取1箱",
                        "status": "completed",
                        "summary": "分析差异原因：短缺5箱可能因运输损耗2箱、登记错误2箱、未记录应急领取1箱；过期3箱因未及时使用且未设置预警；误放2箱因入库时登记错误。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务分析与解析",
                    "summary": "对\"对食品与医疗物资进行周期性盘点，确保数据一致\"的任务进行结构化解析，明确盘点范围、盘点类型、时间要求等基础信息。",
                    "key_points": [
                        "抽取任务要素：食品与医疗物资、周期性盘点、确保数据一致",
                        "识别盘点类型：周期性盘点，非紧急全面盘点",
                        "为后续库存数据解析与差异检测提供统一的数据输入框架"
                    ],
                    "knowledge_trace": "任务文本解析 → 盘点范围/类型/时间要素抽取 → 形成可供后续节点复用的标准任务描述。"
                },
                "inventory_data_parsing": {
                    "title": "库存数据解析",
                    "summary": "对比账面数量120箱与实际传感数量115箱，发现短缺5箱，差异率4.2%，同时检测到3箱物资已过期，2箱物资位置与登记不符。",
                    "key_points": [
                        "从库存系统查询账面数量：食品类80箱，医疗物资类40箱，合计120箱",
                        "通过RFID传感器读取实际数量：食品类77箱，医疗物资类38箱，合计115箱",
                        "计算差异：账面120箱 - 实际115箱 = 短缺5箱，差异率 = 5 ÷ 120 × 100% = 4.2%",
                        "验证差异合理性：差异率4.2%超出合理范围（±2%），需要进一步分析原因"
                    ],
                    "knowledge_trace": "库存系统数据查询 → 账面数量提取 → 传感器数据读取 → 实际数量统计 → 数据对比分析。"
                },
                "book_quantity_analysis": {
                    "title": "账面数量分析",
                    "summary": "从库存系统查询食品与医疗物资的账面数量：食品类80箱，医疗物资类40箱，合计120箱。",
                    "key_points": [
                        "查询食品类账面数量：从库存系统查询食品类物资账面数量为80箱",
                        "查询医疗物资类账面数量：从库存系统查询医疗物资类账面数量为40箱",
                        "汇总账面数量：食品类80箱 + 医疗物资类40箱 = 合计120箱",
                        "记录账面数据来源：数据来源于库存管理系统，最后更新时间2024年12月10日"
                    ],
                    "knowledge_trace": "库存系统查询 → 分类别数量提取 → 数量汇总 → 数据来源记录。"
                },
                "sensor_quantity_analysis": {
                    "title": "实际传感数量分析",
                    "summary": "通过RFID传感器读取实际库存数量：食品类77箱，医疗物资类38箱，合计115箱。",
                    "key_points": [
                        "读取食品类实际数量：通过RFID传感器扫描，食品类实际数量为77箱",
                        "读取医疗物资类实际数量：通过RFID传感器扫描，医疗物资类实际数量为38箱",
                        "汇总实际数量：食品类77箱 + 医疗物资类38箱 = 合计115箱",
                        "验证传感器数据准确性：RFID传感器数据与人工清点结果一致，数据可靠"
                    ],
                    "knowledge_trace": "RFID传感器扫描 → 分类别数量读取 → 数量汇总 → 数据准确性验证。"
                },
                "data_comparison": {
                    "title": "数据对比",
                    "summary": "计算差异：账面120箱 - 实际115箱 = 短缺5箱，差异率 = 5 ÷ 120 × 100% = 4.2%，超出合理范围（±2%）。",
                    "key_points": [
                        "计算总差异：账面120箱 - 实际115箱 = 短缺5箱",
                        "计算差异率：差异率 = 短缺数量 ÷ 账面数量 × 100% = 5 ÷ 120 × 100% = 4.2%",
                        "分类别差异：食品类差异3箱（80-77），医疗物资类差异2箱（40-38）",
                        "评估差异合理性：差异率4.2%超出合理范围（±2%），需要进一步分析原因"
                    ],
                    "knowledge_trace": "账面与实际数量对比 → 差异计算 → 差异率计算 → 合理性评估。"
                },
                "inventory_strategy_formulation": {
                    "title": "盘点策略制定",
                    "summary": "制定盘点策略：食品类消耗快、易过期，优先进行全面盘点；医疗物资类进行重点抽查，重点关注有效期和位置准确性。",
                    "key_points": [
                        "分析物资特性：食品类消耗快、易过期，需要优先盘点；医疗物资类相对稳定，可重点抽查",
                        "确定盘点优先级：食品类 > 医疗物资类，消耗快的品类优先",
                        "制定盘点方法：食品类进行全面盘点（100%），医疗物资类进行重点抽查（50%重点区域）",
                        "设定盘点重点：食品类重点关注数量和有效期，医疗物资类重点关注位置准确性和有效期"
                    ],
                    "knowledge_trace": "物资特性分析 → 消耗速度评估 → 盘点优先级排序 → 盘点方法制定。"
                },
                "difference_detection": {
                    "title": "差异检测",
                    "summary": "检测到三类差异：短缺5箱（账面120箱 - 实际115箱），过期3箱（有效期已过），误放2箱（位置与登记不符），总计差异10箱。",
                    "key_points": [
                        "短缺数量计算：账面120箱 - 实际115箱 = 短缺5箱，其中食品类短缺3箱，医疗物资类短缺2箱",
                        "过期物资检测：检测到3箱物资已过期，食品类2箱（有效期至2024年11月，已过期1个月），医疗物资类1箱（有效期至2024年10月，已过期2个月）",
                        "误放物资识别：发现2箱物资位置与登记不符，食品类1箱（登记在A区-1号货架，实际在A区-3号货架），医疗物资类1箱（登记在B区-2号货架，实际在B区-5号货架）",
                        "差异汇总：总计差异10箱（短缺5箱 + 过期3箱 + 误放2箱），需要进一步分析原因"
                    ],
                    "knowledge_trace": "库存数据对比 → 短缺检测 → 过期检测 → 误放检测 → 差异汇总。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "inventory_parsing", "label": "库存数据解析(账面120箱, 实际115箱)", "type": "input"},
                            {"id": "strategy_formulation", "label": "盘点策略制定(优先食品类)", "type": "process"},
                            {"id": "shortage_detection", "label": "短缺检测(5箱)", "type": "process"},
                            {"id": "expiry_detection", "label": "过期检测(3箱)", "type": "process"},
                            {"id": "misplacement_detection", "label": "误放检测(2箱)", "type": "process"},
                            {"id": "difference_summary", "label": "差异汇总(总计10箱)", "type": "output"}
                        ],
                        "edges": [
                            {"source": "inventory_parsing", "target": "strategy_formulation"},
                            {"source": "strategy_formulation", "target": "shortage_detection"},
                            {"source": "strategy_formulation", "target": "expiry_detection"},
                            {"source": "strategy_formulation", "target": "misplacement_detection"},
                            {"source": "shortage_detection", "target": "difference_summary"},
                            {"source": "expiry_detection", "target": "difference_summary"},
                            {"source": "misplacement_detection", "target": "difference_summary"}
                        ]
                    }
                },
                "shortage_detection": {
                    "title": "短缺检测",
                    "summary": "检测到短缺5箱：食品类短缺3箱（账面80箱 - 实际77箱），医疗物资类短缺2箱（账面40箱 - 实际38箱）。",
                    "key_points": [
                        "食品类短缺计算：账面80箱 - 实际77箱 = 短缺3箱，短缺率 = 3 ÷ 80 × 100% = 3.75%",
                        "医疗物资类短缺计算：账面40箱 - 实际38箱 = 短缺2箱，短缺率 = 2 ÷ 40 × 100% = 5.0%",
                        "短缺分布分析：食品类短缺主要集中在易消耗的快速消费品，医疗物资类短缺分布在常用急救药品",
                        "短缺影响评估：短缺5箱可能影响日常供应，需要及时补充并分析原因"
                    ],
                    "knowledge_trace": "分类别数量对比 → 短缺数量计算 → 短缺率计算 → 影响评估。"
                },
                "expiry_detection": {
                    "title": "过期检测",
                    "summary": "检测到3箱物资已过期：食品类2箱（有效期至2024年11月，已过期1个月），医疗物资类1箱（有效期至2024年10月，已过期2个月）。",
                    "key_points": [
                        "食品类过期检测：检测到2箱食品类物资有效期至2024年11月，已过期1个月，需要立即隔离处理",
                        "医疗物资类过期检测：检测到1箱医疗物资有效期至2024年10月，已过期2个月，需要隔离并评估是否可回收利用",
                        "过期原因分析：过期因未及时使用且未设置有效期预警，导致过期物资未及时发现",
                        "处理建议：立即隔离过期物资，设置有效期预警机制，优先使用临近过期物资"
                    ],
                    "knowledge_trace": "有效期信息查询 → 过期物资识别 → 过期原因分析 → 处理建议生成。"
                },
                "misplacement_detection": {
                    "title": "误放检测",
                    "summary": "检测到2箱物资位置与登记不符：食品类1箱（登记在A区-1号货架，实际在A区-3号货架），医疗物资类1箱（登记在B区-2号货架，实际在B区-5号货架）。",
                    "key_points": [
                        "食品类误放识别：发现1箱食品类物资登记在A区-1号货架，实际RFID扫描位置在A区-3号货架",
                        "医疗物资类误放识别：发现1箱医疗物资登记在B区-2号货架，实际RFID扫描位置在B区-5号货架",
                        "误放原因分析：误放可能因入库时登记错误、搬运过程中位置变更未及时更新、或人工操作失误",
                        "处理建议：更新库存系统位置信息，加强入库登记准确性，建立位置变更及时更新机制"
                    ],
                    "knowledge_trace": "登记位置查询 → 实际位置扫描 → 位置对比 → 误放原因分析。"
                },
                "anomaly_localization": {
                    "title": "异常定位",
                    "summary": "分析差异原因：短缺5箱可能因运输损耗2箱、登记错误2箱、未记录应急领取1箱；过期3箱因未及时使用且未设置预警；误放2箱因入库时登记错误。",
                    "key_points": [
                        "短缺原因分析：短缺5箱可能因运输损耗2箱（运输过程中损坏或丢失）、登记错误2箱（入库时多登记或出库时少登记）、未记录应急领取1箱（紧急情况下领取但未及时登记）",
                        "过期原因分析：过期3箱因未及时使用（消耗速度低于预期）且未设置有效期预警（系统未提前提醒），导致过期物资未及时发现和处理",
                        "误放原因分析：误放2箱因入库时登记错误（登记位置与实际放置位置不一致）或搬运过程中位置变更未及时更新系统",
                        "处理建议：加强运输管理减少损耗、完善登记流程减少错误、设置有效期预警机制、建立位置变更及时更新机制、加强应急领取登记管理"
                    ],
                    "knowledge_trace": "差异检测结果 → 原因分析（运输损耗/登记错误/应急领取/未设置预警） → 形成异常定位报告与处理建议。"
                }
            }
        },
    ),
    # 23. 资源出库
    Scenario(
        id="resource_outbound_processing",  # 23. 资源出库
        model_name="后勤物资管控",
        name="资源出库",
        example_input="为即将执行任务的医疗小组准备急救包和耗材。",
        reasoning_chain="任务需求解析（急救包、绷带、注射器等）→ 库存匹配（查询可用数量与批次）→ 出库策略（先进先出/保质期优先）→ 装载与交接（生成移交记录并推荐运输车辆）",
        prompt=(
            "【后勤物资管控-资源出库专项要求】\n"
            "\n"
            "=== 一、行为树结构要求 ===\n"
            "1. 行为树必须至少包含两层结构（根节点必须有子节点，且至少有一个子节点还有子节点）：\n"
            "   - task_analysis（任务分析与解析，根节点）：\n"
            "       * 明确出库任务需求、物资类型、数量、时间要求等基础信息；\n"
            "       * 至少拆分出\"任务需求提取\"和\"出库目标识别\"两个子层级节点；\n"
            "   - task_requirement_parsing（任务需求解析）：\n"
            "       * 至少包含 material_type_identification（物资类型识别）、quantity_requirement_analysis（数量需求分析）、priority_analysis（优先级分析）三个子节点；\n"
            "   - inventory_matching（库存匹配）：\n"
            "       * 查询可用数量与批次，匹配库存资源；\n"
            "   - outbound_strategy（出库策略，核心决策节点）：\n"
            "       * 下方必须细化出 fifo_strategy（先进先出策略）、expiry_priority_strategy（保质期优先策略）、batch_selection（批次选择）三个子节点；\n"
            "       * 该节点必须包含 knowledge_graph 字段。\n"
            "   - loading_and_handover（装载与交接）：\n"
            "       * 生成移交记录并推荐运输车辆。\n"
            "\n"
            "2. behavior_tree 中每个节点的格式要求：\n"
            "   - label 字段：必须包含具体数值结果，格式示例：\"📦 任务需求解析：急救包10个，绷带20卷\"、\"✅ 库存匹配：可用15个，批次3个\"、\"✅ 出库策略：保质期优先\"；\n"
            "   - summary 字段：必须包含具体数值、数量、批次等量化信息，不能使用空泛描述。\n"
            "\n"
            "=== 二、knowledge_graph 要求 ===\n"
            "outbound_strategy 节点的 knowledge_graph 必须体现完整因果链路：\n"
            "任务需求解析(requirement_parsing) → 库存匹配(inventory_matching) → 出库策略选择(strategy_selection) → 批次确定(batch_determination) → 出库方案生成(outbound_plan)\n"
            "\n"
            "具体要求：\n"
            "- nodes[].label 必须包含具体参数信息，格式：\"节点名称(具体参数1, 具体参数2, ...)\"\n"
            "- nodes[].type 必须明确标注：input（输入）、process（处理）、decision（决策）、output（输出）\n"
            "- edges 必须明确表示推理方向，连接所有相关节点\n"
            "\n"
            "=== 三、node_insights 详细要求 ===\n"
            "为 behavior_tree 中出现的每一个节点（包括所有子节点）提供详细的 node_insights，每个节点包含：\n"
            "1. title：节点标题（简洁明确）\n"
            "2. summary：必须包含具体数值、数量、批次等量化信息\n"
            "3. key_points：3-5条关键要点，每条必须包含具体数值或计算过程\n"
            "4. knowledge_trace：使用箭头（→）连接各个推理步骤，体现完整的推理链条\n"
            "\n"
            "=== 四、输出质量检查清单 ===\n"
            "生成内容后，请确保：\n"
            "□ 行为树至少包含两层结构（根节点有子节点，且至少一个子节点有子节点）\n"
            "□ 至少有一个 node_insights 内的节点包含 knowledge_graph\n"
            "□ 所有 label 包含具体数值\n"
            "□ 所有 summary 包含具体数值而非空泛描述\n"
            "□ 所有 key_points 包含分析过程或具体参数"
        ),
        example_output=None,
    ),
    # 24. 资源维护
    Scenario(
        id="resource_maintenance",  # 24. 资源维护
        model_name="后勤物资管控",
        name="资源维护",
        example_input="对现有无人机电池与医用设备进行例行维护。",
        reasoning_chain="资源状态解析（使用时长、损耗程度、有效期）→ 维护需求判断（需检测/需校准/易损件更换）→ 维护调度策略（优先级排序、资源替换方案）→ 维护记录更新（生成日志并同步至库存系统）",
        prompt=(
            "【后勤物资管控-资源维护专项要求】\n"
            "\n"
            "=== 一、行为树结构要求 ===\n"
            "1. 行为树必须至少包含两层结构（根节点必须有子节点，且至少有一个子节点还有子节点）：\n"
            "   - task_analysis（任务分析与解析，根节点）：\n"
            "       * 明确维护任务范围、资源类型、维护类型等基础信息；\n"
            "       * 至少拆分出\"维护范围识别\"和\"维护类型确定\"两个子层级节点；\n"
            "   - resource_status_parsing（资源状态解析）：\n"
            "       * 至少包含 usage_duration_analysis（使用时长分析）、wear_degree_analysis（损耗程度分析）、expiry_analysis（有效期分析）三个子节点；\n"
            "   - maintenance_requirement_judgment（维护需求判断）：\n"
            "       * 判断需检测/需校准/易损件更换等维护需求；\n"
            "   - maintenance_scheduling_strategy（维护调度策略，核心决策节点）：\n"
            "       * 下方必须细化出 priority_sorting（优先级排序）、resource_replacement_plan（资源替换方案）、schedule_arrangement（调度安排）三个子节点；\n"
            "       * 该节点必须包含 knowledge_graph 字段。\n"
            "   - maintenance_record_update（维护记录更新）：\n"
            "       * 生成日志并同步至库存系统。\n"
            "\n"
            "2. behavior_tree 中每个节点的格式要求：\n"
            "   - label 字段：必须包含具体数值结果，格式示例：\"🔧 资源状态解析：电池使用500小时，损耗30%\"、\"✅ 维护需求判断：需检测\"、\"✅ 维护调度策略：优先级高\"；\n"
            "   - summary 字段：必须包含具体数值、使用时长、损耗程度等量化信息，不能使用空泛描述。\n"
            "\n"
            "=== 二、knowledge_graph 要求 ===\n"
            "maintenance_scheduling_strategy 节点的 knowledge_graph 必须体现完整因果链路：\n"
            "资源状态解析(status_parsing) → 维护需求判断(requirement_judgment) → 优先级排序(priority_sorting) → 资源替换方案(replacement_plan) → 调度安排(schedule_arrangement) → 维护方案生成(maintenance_plan)\n"
            "\n"
            "具体要求：\n"
            "- nodes[].label 必须包含具体参数信息，格式：\"节点名称(具体参数1, 具体参数2, ...)\"\n"
            "- nodes[].type 必须明确标注：input（输入）、process（处理）、decision（决策）、output（输出）\n"
            "- edges 必须明确表示推理方向，连接所有相关节点\n"
            "\n"
            "=== 三、node_insights 详细要求 ===\n"
            "为 behavior_tree 中出现的每一个节点（包括所有子节点）提供详细的 node_insights，每个节点包含：\n"
            "1. title：节点标题（简洁明确）\n"
            "2. summary：必须包含具体数值、使用时长、损耗程度等量化信息\n"
            "3. key_points：3-5条关键要点，每条必须包含具体数值或计算过程\n"
            "4. knowledge_trace：使用箭头（→）连接各个推理步骤，体现完整的推理链条\n"
            "\n"
            "=== 四、输出质量检查清单 ===\n"
            "生成内容后，请确保：\n"
            "□ 行为树至少包含两层结构（根节点有子节点，且至少一个子节点有子节点）\n"
            "□ 至少有一个 node_insights 内的节点包含 knowledge_graph\n"
            "□ 所有 label 包含具体数值\n"
            "□ 所有 summary 包含具体数值而非空泛描述\n"
            "□ 所有 key_points 包含分析过程或具体参数"
        ),
        example_output=None,
    ),


]


def _similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def find_best_scenario(model_name: str, query: str) -> Tuple[Optional[Scenario], float]:
    """
    在给定模型下，根据用户任务描述找到最相近的预设场景。

    返回 (Scenario 或 None, 相似度 0~1)。
    """
    candidates: List[Scenario] = [s for s in SCENARIOS if s.model_name == model_name]
    if not candidates:
        return None, 0.0

    best: Optional[Scenario] = None
    best_score = 0.0
    for scenario in candidates:
        score = _similarity(query, scenario.example_input)
        if score > best_score:
            best = scenario
            best_score = score

    return best, best_score


__all__ = ["Scenario", "SCENARIOS", "find_best_scenario"]


