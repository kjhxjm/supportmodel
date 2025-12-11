from typing import List
from .schema import Scenario

SCENARIOS: List[Scenario] = [
    # 一、越野物流支援模型测试（1~6）
    Scenario(
        id="offroad_fleet_formation",  # 1. 任务编组
        model_name="越野物流",
        name="任务编组",
        example_input="（102,0）向位置X（190,100）运输2车冷链物资资源Y以及2车食物，要求尽快送达，给出对应的任务编组",
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
                            {"id": "task_parsing",
                                "label": "任务解析(位置X, 资源Y, 2小时, 道路损毁风险)", "type": "input"},
                            {"id": "vehicle_matching",
                                "label": "车辆匹配(中型越野无人车)", "type": "process"},
                            {"id": "quantity_calc",
                                "label": "数量计算(2辆, 含20%冗余)", "type": "process"},
                            {"id": "loading_scheme",
                                "label": "装载方案(1车60%,1车40%)", "type": "decision"},
                            {"id": "fleet_config",
                                "label": "最终配置(2辆中型越野无人车)", "type": "output"}
                        ],
                        "edges": [
                            {"source": "task_parsing", "target": "quantity_calc"},
                            {"source": "vehicle_matching",
                                "target": "quantity_calc"},
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
                            {"id": "anomaly_detection",
                                "label": "异常感知结果", "type": "input"},
                            {"id": "env_assessment",
                                "label": "环境评估与路网更新", "type": "process"},
                            {"id": "route_optimization",
                                "label": "路径优化决策", "type": "decision"},
                            {"id": "new_route", "label": "新路径生成", "type": "output"}
                        ],
                        "edges": [
                            {"source": "initial_route", "target": "env_assessment"},
                            {"source": "anomaly_detection",
                                "target": "env_assessment"},
                            {"source": "env_assessment",
                                "target": "route_optimization"},
                            {"source": "route_optimization", "target": "new_route"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="offroad_fleet_cargo_monitor",  # 3. 车队/货物状态监控
        model_name="越野物流",
        name="车队/货物状态监控",
        example_input="运输冷链物资Y至目的地X，需确保车辆与货物保持稳定状态。",
        reasoning_chain="监控需求解析（车辆状态、速度、温度、振动、能耗）→ 传感器数据融合（温度传感器、车载健康监测、GPS、IMU）→ 状态判别（检测异常升温、胎压异常、路线偏移、能量不足等）→ 异常处理策略（降速保温、切换备用车辆、调整路线、提升采样频率）→ 告警与记录（生成异常提示与任务执行日志，并同步至指挥端）",
        prompt=(
            "【越野物流-车队/货物状态监控专项要求】\n"
            "1. 行为树必须包含：\n"
            "   - task_analysis（任务解析）：解析冷链物资Y的温控要求、车辆稳定性需求与目的地X的运输约束；\n"
            "   - monitoring_requirement_analysis（监控需求解析）：明确车辆状态（健康、速度、能耗、位置）与货物状态（温度、振动、完整性）的监控维度；\n"
            "   - sensor_fusion（传感器数据融合）：整合温度传感器、车载健康监测、GPS、IMU、胎压传感器、能耗监测等多源数据；\n"
            "   - status_judgment（状态判别）：识别异常升温、胎压异常、路线偏移、能量不足、过度振动等多类异常；\n"
            "   - anomaly_response（异常处理与告警，核心决策节点）：\n"
            "       * 生成分级告警与应对策略（降速保温、切换备用车辆、调整路线、提升采样频率），并同步至指挥端，必须包含 knowledge_graph。\n"
            "2. anomaly_response 节点的 knowledge_graph 必须体现：\n"
            "   监控需求(monitoring_requirements) → 传感器融合(sensor_fusion) → 状态判别(status_judgment) → 异常策略(response_strategy) → 告警记录(alert_logging)。\n"
            "3. node_insights 要求：\n"
            "   - 详细说明车辆健康监测指标（胎压、能耗、速度、位置偏移）与货物监控指标（温度、振动）的阈值设计；\n"
            "   - 阐述多源传感器数据融合的逻辑与异常识别规则；\n"
            "   - 对异常处理策略（降速、改道、切换车辆、停车检查）进行条目化说明，包含触发条件与执行优先级；\n"
            "   - knowledge_trace 体现\"需求解析 → 数据融合 → 异常识别 → 策略执行 → 告警记录\"的完整闭环。"
        ),
        example_output={
            "default_focus": "anomaly_response",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "🚛 任务解析：冷链物资Y运至目的地X，确保车辆与货物稳定",
                "status": "completed",
                "summary": "解析\"运输冷链物资Y至目的地X，需确保车辆与货物保持稳定状态\"任务，明确冷链温控要求、车辆健康监测需求与运输稳定性约束。",
                "children": [
                    {
                        "id": "monitoring_requirement_analysis",
                        "label": "📊 监控需求解析",
                        "status": "completed",
                        "summary": "明确车辆监控维度（健康状态、速度、能耗、位置）与货物监控维度（温度、振动、完整性），形成全面监控需求清单。",
                        "children": []
                    },
                    {
                        "id": "sensor_fusion",
                        "label": "🛰️ 传感器数据融合",
                        "status": "completed",
                        "summary": "整合温度传感器（双探头，采样频率1Hz）、车载健康监测（胎压、电池电压、电机温度）、GPS（位置更新频率5Hz）、IMU（振动与姿态，采样频率50Hz）等多源数据。",
                        "children": []
                    },
                    {
                        "id": "status_judgment",
                        "label": "🔍 状态判别",
                        "status": "completed",
                        "summary": "识别多类异常：温度偏离冷链标准（-18±3°C）、胎压异常（偏离正常值>15%）、路线偏移（>50m）、能量不足（<20%）、过度振动（>2g持续5秒）。",
                        "children": []
                    },
                    {
                        "id": "anomaly_response",
                        "label": "⚠️ 异常处理与告警",
                        "status": "active",
                        "summary": "根据异常类型与严重程度执行分级响应：轻度（提升采样频率+预警）、中度（降速保温或调整路线+告警）、严重（切换备用车辆或停车检查+紧急告警），所有异常与处理动作同步至指挥端并生成执行日志。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务解析",
                    "summary": "将\"运输冷链物资Y至目的地X，需确保车辆与货物保持稳定状态\"细化为车辆健康监测、货物冷链保障与运输完整性三大监控目标。",
                    "key_points": [
                        "识别冷链物资Y需保持冷链温区（-18±3°C）并控制振动在安全范围内",
                        "明确车辆需全程监测健康状态（胎压、能耗、速度、位置）确保运输可靠性",
                        "确定目的地X的路线与时效约束，预留异常处置与路线调整缓冲",
                        "推断需要建立车辆-货物双重监控体系，支持实时告警与应对"
                    ],
                    "knowledge_trace": "任务文本解析 → 车辆/货物/路线约束提取 → 形成双重监控需求输入。"
                },
                "monitoring_requirement_analysis": {
                    "title": "监控需求解析",
                    "summary": "细化车辆监控维度（健康状态、速度、能耗、位置偏移）与货物监控维度（温度、振动、完整性），形成全面监控指标体系。",
                    "key_points": [
                        "车辆健康监测：胎压（正常范围±15%）、电池电压/能量（告警阈值20%）、电机温度（过热阈值85°C）、传动系统状态",
                        "车辆运行监测：速度（限速与实际速度对比）、GPS位置（偏离路线阈值50m）、行驶里程累计",
                        "货物状态监测：温度（冷链标准-18±3°C）、振动加速度（告警阈值2g持续5秒）、货舱完整性（门锁状态、密封性）",
                        "环境监测：外部温度、湿度、路面状况（通过IMU推断）",
                        "通信状态：数据链路质量、上报延迟、指挥端连接状态"
                    ],
                    "knowledge_trace": "任务约束 → 车辆/货物/环境维度拆解 → 形成多维监控需求清单与阈值配置。"
                },
                "sensor_fusion": {
                    "title": "传感器数据融合",
                    "summary": "整合温度传感器、车载健康监测、GPS、IMU等多源传感器数据，形成统一的车辆-货物状态评估数据流。",
                    "key_points": [
                        "温度传感器：双探头配置（货舱前部+后部），采样频率1Hz，精度±0.5°C，异常时提升至5Hz",
                        "车载健康监测：胎压传感器（4轮独立监测，更新频率0.2Hz）、电池管理系统（电压、电流、SOC、温度，1Hz）、电机控制器（温度、转速、扭矩，5Hz）",
                        "GPS定位：位置更新频率5Hz，精度<5m，支持差分增强，持续记录轨迹与偏离计算",
                        "IMU传感器：6轴加速度与陀螺仪，采样频率50Hz，用于振动监测、姿态评估与路况推断",
                        "数据融合策略：时间戳对齐、异常值过滤（3σ原则）、多传感器交叉验证（如胎压与振动关联分析）、状态估计（卡尔曼滤波）"
                    ],
                    "knowledge_trace": "监控需求 → 传感器选型与配置 → 数据采集与预处理 → 时间对齐与融合 → 输出统一状态数据流。"
                },
                "status_judgment": {
                    "title": "状态判别",
                    "summary": "基于融合后的传感器数据，识别车辆与货物的多类异常情况并进行严重程度分级。",
                    "key_points": [
                        "温度异常：偏离-18°C超过±3°C持续30秒→轻度预警；超过±5°C持续60秒→中度告警；超过±8°C或制冷系统故障→严重告警",
                        "振动异常：加速度>1.5g持续3秒→轻度预警（提示减速）；>2g持续5秒→中度告警（强制减速）；>3g或检测到货物移位→严重告警（停车检查）",
                        "胎压异常：单轮偏离正常值10-15%→轻度预警；>15%或压力快速下降→中度告警；>25%或检测到漏气→严重告警（停车更换）",
                        "路线偏移：偏离计划路线20-50m→轻度预警（自动纠偏）；>50m持续30秒→中度告警（重新规划）；进入禁行区或危险区域→严重告警（立即停车）",
                        "能量不足：剩余电量20-30%→轻度预警（规划补能）；10-20%→中度告警（寻找最近补能点）；<10%→严重告警（就近停车等待救援）",
                        "通信异常：数据延迟>5秒→轻度预警；连接中断30秒→中度告警（启用离线模式）；中断>3分钟→严重告警（任务暂停）"
                    ],
                    "knowledge_trace": "融合数据流 → 阈值与规则判断 → 异常类型识别 → 严重程度分级（轻度/中度/严重） → 输出异常事件列表。"
                },
                "anomaly_response": {
                    "title": "异常处理与告警",
                    "summary": "根据异常类型与严重程度，执行分级响应策略并生成告警记录，确保车辆与货物安全，所有处理动作同步至指挥端。",
                    "key_points": [
                        "轻度预警响应：提升相关传感器采样频率（如温度异常时从1Hz提升至5Hz）、增加数据上报频率（从30秒/次缩短至5秒/次）、生成预警消息发送至指挥端、记录预警事件与时间戳",
                        "中度告警响应：执行主动干预措施（温度异常→增强制冷功率；振动异常→降速至安全速度；胎压异常→调整行驶模式；路线偏移→重新规划路径；能量不足→导航至最近补能点）、生成告警消息并要求指挥端确认、持续监测异常指标变化趋势",
                        "严重告警响应：执行紧急措施（停车检查、切换至备用车辆、请求人工干预）、生成紧急告警并实时推送至指挥端、启动应急预案（如货物转移、现场维修、等待救援）、锁定现场状态数据用于事故分析",
                        "多异常协同处理：同时出现多类异常时，按优先级排序（生命安全>货物安全>任务效率），优先处理高优先级异常，记录所有异常的时序关系",
                        "闭环验证与记录：每次处理动作执行后，验证异常是否消除或缓解，记录\"异常类型-检测时间-处理动作-执行时间-恢复时间-最终状态\"完整链路，生成任务执行日志并归档"
                    ],
                    "knowledge_trace": "监控需求解析 → 传感器数据融合 → 状态判别与分级 → 异常响应策略选择 → 执行处理动作 → 告警与日志生成 → 同步至指挥端 → 闭环验证。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "monitoring_requirements",
                                "label": "监控需求(车辆健康,货物状态,位置能耗)", "type": "input"},
                            {"id": "sensor_fusion",
                                "label": "传感器融合(温度,GPS,IMU,胎压,能耗)", "type": "process"},
                            {"id": "status_judgment",
                                "label": "状态判别(温度,振动,胎压,路线,能量)", "type": "process"},
                            {"id": "anomaly_classification",
                                "label": "异常分级(轻度/中度/严重)", "type": "process"},
                            {"id": "response_strategy",
                                "label": "响应策略(提频/降速/改道/切换/停车)", "type": "decision"},
                            {"id": "alert_logging",
                                "label": "告警与记录(实时推送,执行日志)", "type": "output"},
                            {"id": "command_sync",
                                "label": "指挥端同步(状态+告警+日志)", "type": "output"}
                        ],
                        "edges": [
                            {"source": "monitoring_requirements",
                                "target": "sensor_fusion"},
                            {"source": "sensor_fusion",
                                "target": "status_judgment"},
                            {"source": "status_judgment",
                                "target": "anomaly_classification"},
                            {"source": "anomaly_classification",
                                "target": "response_strategy"},
                            {"source": "response_strategy",
                                "target": "alert_logging"},
                            {"source": "alert_logging", "target": "command_sync"},
                            {"source": "response_strategy",
                                "target": "sensor_fusion"}
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
                "summary": "解析4车食品与水运往X的任务，明确需要在越野环境下保持编队稳定、按时抵达并兼顾效率。",
                "children": [
                    {
                        "id": "formation_planning",
                        "label": "🛤️ 行进编队规划：单列/并行自适应",
                        "status": "completed",
                        "summary": "基于道路宽度、安全距离与通行风险，选择单列或局部并行队列，输出车序与间距，为后续协同动作提供约束。",
                        "children": []
                    },
                    {
                        "id": "coordination_management",
                        "label": "🤝 协同动作管理：动态调整队形与顺序",
                        "status": "active",
                        "summary": "针对掉头、避障、狭窄路段等场景，动态调整队形与行进顺序，规划通信同步与执行顺序以优化整体效率。",
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
                    "summary": "将“向X位置运输4车食品和水”解析为多车协同行进任务，需平衡安全距离、通过效率与实时路况适应。",
                    "key_points": [
                        "识别车队规模为4车，货物类型为食品与水",
                        "结合路况推断狭窄路段/会车/障碍等场景，形成编队约束",
                        "提出“保障安全距离 + 动态调整队形 + 控制整体用时”的调度目标"
                    ],
                    "knowledge_trace": "任务文本解析 → 车队规模与货物属性识别 → 协同与效率目标定义。"
                },
                "formation_planning": {
                    "title": "行进编队规划",
                    "summary": "根据道路宽度、安全间距与风险等级，选择单列或局部并行，生成初始车序与间距，供执行阶段动态调整。",
                    "key_points": [
                        "估算道路宽度与会车可能性，判断是否允许并行队列",
                        "设计纵向间距以兼顾制动距离与通信链路稳定性",
                        "初始车序可倾向将侦察/较轻载车辆置前，便于探路与避障",
                        "为“掉头/整体倒置/让行”动作预留可重排的编号与槽位"
                    ],
                    "knowledge_trace": "道路与安全约束 → 编队方式筛选 → 车序与间距配置。"
                },
                "coordination_management": {
                    "title": "协同动作管理",
                    "summary": "点击后展示推理图谱：在掉头、通过狭窄路段或需要整体倒置时，动态调整队形与行进顺序，定义通信同步与执行顺序以优化效率。",
                    "key_points": [
                        "识别协同行为：依序掉头、整体倒置、让行/避障、通过狭窄路段",
                        "动态队形：依据道路宽度/障碍实时选择单列或并行，必要时整体倒置车序",
                        "通信同步：各车共享局部感知与关键状态，保持一致的动作顺序与速度指令",
                        "执行顺序：按“感知→决策→广播→协同行动→状态同步”闭环运行，保证平滑过渡",
                        "效率目标：在安全约束下最小化通行时间与停顿次数"
                    ],
                    "knowledge_trace": "编队规划结果 → 感知道路宽度/障碍 → 选择单列或并行队形 → 生成协同行动顺序（掉头/倒置/让行） → 执行与状态同步。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "formation_planning",
                                "label": "编队规划结果", "type": "input"},
                            {"id": "local_policy_agents",
                                "label": "各车本地策略 π_i / Q_i", "type": "process"},
                            {"id": "local_experience",
                                "label": "本地轨迹与经验回放 D_i", "type": "process"},
                            {"id": "consensus_weight",
                                "label": "分布式一致性权重估计 ω(τ)", "type": "process"},
                            {"id": "decentralized_update",
                                "label": "去中心化策略更新(Actor–Critic)", "type": "process"},
                            {"id": "coordination_strategy",
                                "label": "协同动作策略", "type": "process"},
                            {"id": "execution_sequence",
                                "label": "协同行动执行顺序", "type": "decision"},
                            {"id": "status_sync",
                                "label": "车队状态同步与反馈", "type": "output"}
                        ],
                        "edges": [
                            {"source": "formation_planning",
                                "target": "local_policy_agents"},
                            {"source": "local_policy_agents",
                                "target": "local_experience"},
                            {"source": "local_experience",
                                "target": "consensus_weight"},
                            {"source": "consensus_weight",
                                "target": "decentralized_update"},
                            {"source": "decentralized_update",
                                "target": "coordination_strategy"},
                            {"source": "coordination_strategy",
                                "target": "execution_sequence"},
                            {"source": "execution_sequence",
                                "target": "status_sync"},
                            {"source": "status_sync",
                                "target": "local_policy_agents"}
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
                            {"id": "terrain_obstacle",
                                "label": "地形与障碍抽取结果", "type": "input"},
                            {"id": "risk_level",
                                "label": "通行风险判定(等级+系数)", "type": "process"},
                            {"id": "vehicle_capability",
                                "label": "车辆能力匹配", "type": "process"},
                            {"id": "pass_strategy", "label": "通行/绕行策略生成",
                                "type": "decision"},
                            {"id": "feasibility_conclusion",
                                "label": "任务可行性结论", "type": "output"}
                        ],
                        "edges": [
                            {"source": "terrain_obstacle", "target": "risk_level"},
                            {"source": "risk_level", "target": "vehicle_capability"},
                            {"source": "vehicle_capability",
                                "target": "pass_strategy"},
                            {"source": "pass_strategy",
                                "target": "feasibility_conclusion"}
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
                            {"id": "load_slope_profile",
                                "label": "载重与坡度解析结果", "type": "input"},
                            {"id": "unit_energy", "label": "单位距离能耗估计",
                                "type": "process"},
                            {"id": "travel_time", "label": "行程时间预测",
                                "type": "process"},
                            {"id": "total_energy", "label": "总能耗推理",
                                "type": "process"},
                            {"id": "resupply_plan",
                                "label": "补能与补给建议", "type": "output"}
                        ],
                        "edges": [
                            {"source": "load_slope_profile",
                                "target": "unit_energy"},
                            {"source": "unit_energy", "target": "total_energy"},
                            {"source": "load_slope_profile",
                                "target": "travel_time"},
                            {"source": "total_energy", "target": "resupply_plan"},
                            {"source": "travel_time", "target": "resupply_plan"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="offroad_logistics_strategy",  # 越野物流策略
        model_name="越野物流",
        name="越野物流策略",
        example_input="（102,0）向位置X（190,100）运输2车冷链物资资源Y以及2车5kg食物与水，道路存在不确定损毁风险，要求2小时内送达。",
        reasoning_chain="任务解析（距离、地形、载重、道路损毁程度）→ 车辆匹配（履带式/六轮越野无人车，理由：通过性与稳定性）→ 装车方案（装载顺序、固定方式、重心配平、装载量分配）→ 行进策略推理（选择低速稳态模式、坡度敏感控制、涉水绕行策略、路径重规划）→ 风险规避与冗余方案（使用前置侦察无人机、设置备用路线、补能策略）→ 物流执行计划（运输批次、行进间隔、车队协同方式、车队/货物监控）→ 卸货操作（卸载方式、顺序安排、安全确认、交接流程）",
        prompt=(
            "【越野物流-越野物流策略专项要求】\n"
            "1. 行为树必须至少包含以下核心节点，严格按照推理链条自上而下展开：\n"
            "   - task_analysis（任务解析）：解析运输距离（从(102,0)到(190,100)）、地形类型、载重需求（冷链物资+食物与水）、道路损毁程度、时间约束（2小时）；\n"
            "   - vehicle_matching（车辆匹配）：基于地形与载重特点，选择履带式或六轮越野无人车，说明通过性与稳定性的选择理由；\n"
            "   - loading_plan（装车方案）：规划装载顺序、固定方式、重心配平与装载量分配，确保运输安全；\n"
            "   - movement_strategy（行进策略推理，二级节点）：必须包含以下四个三级子节点：\n"
            "       * low_speed_stable_mode（低速稳态模式）：坡度敏感的速度控制策略；\n"
            "       * slope_sensitive_control（坡度敏感控制）：动力分配与制动策略；\n"
            "       * water_crossing_bypass（涉水绕行策略）：水深检测与绕行决策；\n"
            "       * path_replanning（路径重规划）：必须包含children以支持进一步展开，包含路径规划、异常感知与处理、重规划逻辑；\n"
            "   - risk_mitigation（风险规避与冗余方案）：包含前置侦察无人机配置、备用路线设置、补能策略规划；\n"
            "   - logistics_execution_plan（物流执行计划，核心决策节点）：必须包含以下子节点：\n"
            "       * transport_batches（运输批次）：批次划分与调度；\n"
            "       * convoy_interval（行进间隔）：车间距与跟随策略；\n"
            "       * fleet_coordination（车队协同方式）：必须包含children以支持进一步展开，包含编队规划与协同动作管理；\n"
            "       * fleet_cargo_monitoring（车队/货物状态监控）：必须包含children以支持进一步展开，包含监控、传感器融合、状态判别、异常处理、告警记录；\n"
            "       必须包含 knowledge_graph 字段。\n"
            "   - unloading_operation（卸货操作）：规划卸载方式、顺序安排、安全确认与交接流程。\n"
            "2. logistics_execution_plan 节点的 knowledge_graph 必须体现完整因果链路：\n"
            "   任务解析 → 车辆匹配 → 装车方案 → 行进策略推理 → 风险规避 → 物流执行计划 → 卸货操作。\n"
            "3. 在 node_insights 中：\n"
            "   - movement_strategy 节点必须包含 knowledge_graph，体现四个子策略的关系；\n"
            "   - path_replanning 节点必须包含 knowledge_graph，体现路径规划→异常感知→重规划的链路；\n"
            "   - fleet_coordination 节点必须包含 knowledge_graph，体现编队规划→协同动作管理的链路；\n"
            "   - fleet_cargo_monitoring 节点必须包含 knowledge_graph，体现监控→融合→判别→处理→告警的链路；\n"
            "   - 所有节点的 knowledge_trace 体现完整推理路径。"
        ),
        example_output={
            "default_focus": "logistics_execution_plan",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "🚛 任务解析：越野物流运输任务",
                "status": "completed",
                "summary": "解析从(102,0)向位置X(190,100)运输2车冷链物资资源Y及2车5kg食物与水的任务，道路存在不确定损毁风险，要求2小时内送达。运输距离约110km，需考虑冷链温控与道路风险。",
                "children": [
                    {
                        "id": "vehicle_matching",
                        "label": "🚗 车辆匹配：4辆六轮越野无人车",
                        "status": "completed",
                        "summary": "基于110km运输距离、2小时时限与道路损毁风险，选择4辆六轮越野无人车（2辆配备冷链设备运输冷链物资，2辆运输食物与水），理由：六轮设计具备良好通过性与稳定性，最高时速60km/h可满足时限要求。",
                        "children": []
                    },
                    {
                        "id": "loading_plan",
                        "label": "📦 装车方案",
                        "status": "completed",
                        "summary": "规划装载顺序（冷链物资优先装载并启动制冷，食物与水按重量分配）、固定方式（绑扎带+防滑垫+限位挡板）、重心配平（前后6:4，左右对称）、装载量分配（冷链车各50kg，普通车各5kg食物与水）。",
                        "children": [
                            {
                                "id": "loading_sequence",
                                "label": "装载顺序",
                                "status": "completed",
                                "summary": "重物在下轻物在上，冷链物资需优先装载并预冷，食物与水按密封防潮要求装载。",
                                "children": []
                            },
                            {
                                "id": "fixing_method",
                                "label": "固定方式",
                                "status": "completed",
                                "summary": "采用高强度绑扎带（承载力>500kg）+防滑垫（摩擦系数>0.6）+限位挡板组合固定。",
                                "children": []
                            },
                            {
                                "id": "weight_balance",
                                "label": "重心配平",
                                "status": "completed",
                                "summary": "前后重量比6:4提升爬坡稳定性，左右严格对称（偏差<5%）。",
                                "children": []
                            },
                            {
                                "id": "load_distribution",
                                "label": "装载量分配",
                                "status": "completed",
                                "summary": "2辆冷链车各装载冷链物资约50kg，2辆普通车各装载5kg食物与水。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "movement_strategy",
                        "label": "🛤️ 行进策略推理",
                        "status": "completed",
                        "summary": "生成包含低速稳态模式、坡度敏感控制、涉水绕行策略与路径重规划的多层次行进策略，确保在道路损毁风险下安全高效完成运输。",
                        "children": [
                            {
                                "id": "low_speed_stable_mode",
                                "label": "🐢 低速稳态模式",
                                "status": "completed",
                                "summary": "当坡度>15°或路面附着系数<0.4时，自动切换至低速档（10km/h），增加牵引力与稳定性，保护冷链货物免受剧烈颠簸。",
                                "children": []
                            },
                            {
                                "id": "slope_sensitive_control",
                                "label": "⛰️ 坡度敏感控制",
                                "status": "completed",
                                "summary": "实时监测坡度传感器，动态调整六轮动力分配比例：上坡时后轮驱动力增加30%，下坡时启用制动能量回收并限速至15km/h。",
                                "children": []
                            },
                            {
                                "id": "water_crossing_bypass",
                                "label": "💧 涉水绕行策略",
                                "status": "completed",
                                "summary": "当检测到水深>40cm或水流速度>1.5m/s时，自动触发绕行规划，优先选择上游浅滩或桥梁通道，避免涉水导致货物受损或车辆故障。",
                                "children": []
                            },
                            {
                                "id": "path_replanning",
                                "label": "🔄 路径重规划",
                                "status": "completed",
                                "summary": "基于实时感知的障碍信息，综合车队状态、地图与异常信息生成新的可行路径。支持进一步展开查看详细规划逻辑。",
                                "children": [
                                    {
                                        "id": "path_planning_base",
                                        "label": "📍 路径规划",
                                        "status": "completed",
                                        "summary": "基于高精度地图与实时路况信息，规划从(102,0)到(190,100)的最优路径，预计行驶距离110km，预估耗时1.5小时（含安全余量）。",
                                        "children": [
                                            {
                                                "id": "map_data",
                                                "label": "🗺️ 地图数据",
                                                "status": "completed",
                                                "summary": "加载1:10000高精度地图，包含道路等级、坡度信息、路面类型、历史损毁记录、桥梁涵洞位置等关键地理要素。",
                                                "children": []
                                            },
                                            {
                                                "id": "road_condition_data",
                                                "label": "🛣️ 实时路况",
                                                "status": "completed",
                                                "summary": "实时获取卫星影像与历史通行数据，标注高风险区域（塌方、积水、施工），更新频率5分钟/次，路况置信度>85%。",
                                                "children": []
                                            }
                                        ]
                                    },
                                    {
                                        "id": "anomaly_perception",
                                        "label": "👁️ 异常感知与处理",
                                        "status": "completed",
                                        "summary": "当感知数据出现异常（如前方道路塌方、积水、障碍物）时，派遣机器狗抵近观察，获取精确障碍信息与可通行性评估。",
                                        "children": [
                                            {
                                                "id": "anomaly_detection",
                                                "label": "⚠️ 感知数据异常",
                                                "status": "completed",
                                                "summary": "车载传感器检测到异常：前方道路影像与地图不符、障碍物体积超出通行空间、路面反射异常（可能积水）、激光雷达回波异常等。",
                                                "children": []
                                            },
                                            {
                                                "id": "robot_dog_scout",
                                                "label": "🐕 派遣机器狗抵近观察",
                                                "status": "completed",
                                                "summary": "从队尾释放机器狗，行进至异常点前方20m进行抵近观察，采集障碍物尺寸与材质、路面承载能力、积水深度、可通行宽度等数据，实时回传（延迟<500ms）。",
                                                "children": []
                                            }
                                        ]
                                    },
                                    {
                                        "id": "dynamic_replanning",
                                        "label": "🔀 动态重规划",
                                        "status": "completed",
                                        "summary": "综合车队当前位置、剩余电量、货物状态、地图信息与异常感知结果，实时计算最优替代路径，重规划决策时间<30秒。",
                                        "children": [
                                            {
                                                "id": "fleet_status_input",
                                                "label": "🚛 车队状态",
                                                "status": "completed",
                                                "summary": "获取车队当前位置（GPS精度<1m）、各车剩余电量、货物状态（冷链温度、振动水平）、车辆健康状态等实时数据。",
                                                "children": []
                                            },
                                            {
                                                "id": "map_anomaly_fusion",
                                                "label": "🔗 地图与异常信息融合",
                                                "status": "completed",
                                                "summary": "将异常感知结果叠加至高精度地图，标注障碍区域与可通行边界，结合备选路线库，基于A*算法快速搜索最优替代路径，计算时间<30秒。",
                                                "children": []
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": "risk_mitigation",
                        "label": "⚠️ 风险规避与冗余方案",
                        "status": "completed",
                        "summary": "配置2架前置侦察无人机（提前1km探测路况）、设置3条备用路线（主路线+2条备选）、规划中途补能点（每30km设置一个快速充电站）。",
                        "children": [
                            {
                                "id": "scout_uav",
                                "label": "🚁 前置侦察无人机",
                                "status": "completed",
                                "summary": "2架小型旋翼无人机提前1km探测路况，飞行高度80m，可识别塌方、积水、倾倒树木等障碍，实时回传视频与地形数据。",
                                "children": []
                            },
                            {
                                "id": "backup_routes",
                                "label": "🗺️ 备用路线设置",
                                "status": "completed",
                                "summary": "主路线（最短距离110km）+备选路线A（绕行增加15km但避开高风险区域）+备选路线B（应急路线，适合单车通过），路线切换决策时间<2分钟。",
                                "children": []
                            },
                            {
                                "id": "energy_strategy",
                                "label": "🔋 补能策略",
                                "status": "completed",
                                "summary": "每30km设置快速充电站，单次补能时间10分钟可恢复50%电量，确保车辆在2小时内完成往返任务。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "logistics_execution_plan",
                        "label": "✅ 物流执行计划",
                        "status": "active",
                        "summary": "制定运输方案：4辆车编队出发，车间距保持150m，采用梯队协同模式，实时监控车队与货物状态，预计1.5小时完成运输，满足2小时时限要求。",
                        "children": [
                            {
                                "id": "transport_batches",
                                "label": "📋 运输批次",
                                "status": "completed",
                                "summary": "本次任务为单批次运输：4辆车同时出发，2辆冷链车+2辆普通车编队行进，单批次总载重约110kg。",
                                "children": []
                            },
                            {
                                "id": "convoy_interval",
                                "label": "📏 行进间隔",
                                "status": "completed",
                                "summary": "车队内车间距保持150m（约15秒行进时间差），避免连环事故，便于单车机动与故障处置，同时保持通信稳定。",
                                "children": []
                            },
                            {
                                "id": "fleet_coordination",
                                "label": "🤝 车队协同方式",
                                "status": "completed",
                                "summary": "采用梯队协同模式，支持进一步展开查看编队规划与协同动作管理详情。",
                                "children": [
                                    {
                                        "id": "formation_planning",
                                        "label": "📐 行进编队规划",
                                        "status": "completed",
                                        "summary": "依据道路宽度选择队形：宽路段（>6m）采用双列并行（冷链车在内侧），窄路段（<6m）切换为单列纵队，前车负责探路与障碍标记。",
                                        "children": []
                                    },
                                    {
                                        "id": "coordination_actions",
                                        "label": "🔄 协同动作管理",
                                        "status": "completed",
                                        "summary": "依据道路宽度与障碍情况，组织依序掉头（窄路）或队列整体倒置（宽路），支持动态队形调整与紧急避让协同。",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "id": "fleet_cargo_monitoring",
                                "label": "📊 车队/货物状态监控",
                                "status": "completed",
                                "summary": "实时监控车队运行情况与货物状态，自动识别异常并生成告警与应对策略。支持进一步展开查看监控详情。",
                                "children": [
                                    {
                                        "id": "monitoring_requirements",
                                        "label": "📋 监控需求解析",
                                        "status": "completed",
                                        "summary": "监控项目包括：车辆状态（位置、速度、电量）、冷链温度（目标-18°C±2°C）、振动水平（加速度<2g）、能耗率（kWh/km）。",
                                        "children": []
                                    },
                                    {
                                        "id": "sensor_data_fusion",
                                        "label": "📡 传感器数据融合",
                                        "status": "completed",
                                        "summary": "融合温度传感器、车载健康监测系统、GPS定位、IMU惯性测量单元数据，采样频率10Hz，数据融合延迟<100ms。",
                                        "children": []
                                    },
                                    {
                                        "id": "status_determination",
                                        "label": "🔍 状态判别",
                                        "status": "completed",
                                        "summary": "实时检测异常状态：温度偏离（冷链温度>-16°C或<-20°C）、电量不足（<20%）、路线偏移（>50m）、振动异常（>3g持续5秒）。",
                                        "children": []
                                    },
                                    {
                                        "id": "anomaly_handling",
                                        "label": "🛠️ 异常处理策略",
                                        "status": "completed",
                                        "summary": "针对不同异常采取对应措施：温度异常→启动备用制冷/降速保温；电量不足→导航至最近补能点；路线偏移→自动纠偏/重规划；振动异常→降速并检查货物固定。",
                                        "children": []
                                    },
                                    {
                                        "id": "alert_logging",
                                        "label": "🚨 告警与记录",
                                        "status": "completed",
                                        "summary": "生成异常提示与任务执行日志，实时同步至指挥端。告警分级：一般（黄色）、紧急（橙色）、严重（红色），日志包含时间戳、位置、异常类型、处理措施。",
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": "unloading_operation",
                        "label": "📤 卸货操作",
                        "status": "pending",
                        "summary": "到达位置X(190,100)后，采用逐车卸载方式（冷链车优先），自动卸载装置配合人工辅助，进行货物清点与完整性确认，完成交接签收并记录。",
                        "children": [
                            {
                                "id": "unloading_method",
                                "label": "卸载方式",
                                "status": "pending",
                                "summary": "采用自动液压尾板+人工辅助的方式，单车卸载时间约3分钟，冷链物资需在制冷环境下快速转移。",
                                "children": []
                            },
                            {
                                "id": "unloading_sequence",
                                "label": "顺序安排",
                                "status": "pending",
                                "summary": "优先卸载冷链物资（保持冷链不断），其次卸载食物与水，确保货物品质不受影响。",
                                "children": []
                            },
                            {
                                "id": "safety_confirmation",
                                "label": "安全确认",
                                "status": "pending",
                                "summary": "卸载过程中检查货物外包装完整性、冷链温度记录（确认全程-18°C±2°C）、食物密封状态，发现异常立即记录。",
                                "children": []
                            },
                            {
                                "id": "handover_process",
                                "label": "交接流程",
                                "status": "pending",
                                "summary": "按货物清单逐项清点，使用扫码设备核对，与接收人员完成电子签名交接，生成完整运输记录回传指挥端。",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务解析",
                    "summary": "从任务文本中提取起点(102,0)、终点(190,100)、运输距离约110km、货物类型（冷链物资+食物与水）、时间约束（2小时）以及道路损毁风险。",
                    "key_points": [
                        "起点坐标(102,0)，终点位置X坐标(190,100)，直线距离约110km",
                        "货物组成：2车冷链物资资源Y（需温控-18°C）+ 2车5kg食物与水（常温运输）",
                        "时间约束：2小时内送达，平均速度需>55km/h",
                        "风险因素：道路存在不确定损毁风险，需预留备用路线与应急方案"
                    ],
                    "knowledge_trace": "任务文本 → 坐标/距离/货物/时限/风险要素提取 → 形成任务约束条件 → 为后续车辆匹配与策略生成提供输入。"
                },
                "vehicle_matching": {
                    "title": "车辆匹配",
                    "summary": "基于110km运输距离、2小时时限与冷链+常温混合货物需求，选择4辆六轮越野无人车的编队方案。",
                    "key_points": [
                        "六轮越野无人车：最高时速60km/h，续航150km，具备良好通过性（爬坡能力30°，涉水深度50cm）",
                        "冷链配置：2辆车配备车载制冷系统（制冷能力-25°C~5°C可调），满足冷链物资温控需求",
                        "载重能力：单车载重能力80kg，4车总载重320kg，满足110kg货物运输需求并保留190kg冗余",
                        "选择理由：六轮设计比履带式速度快40%，可满足2小时时限；比四轮稳定性更好，适应道路损毁风险"
                    ],
                    "knowledge_trace": "运输距离+时限约束 → 速度需求推算 → 货物类型分析 → 选择六轮越野无人车 → 配置冷链设备 → 验证载重与续航能力。"
                },
                "loading_plan": {
                    "title": "装车方案",
                    "summary": "基于4辆六轮越野无人车的载重能力与冷链/常温混合货物特性，制定科学的装载方案。",
                    "key_points": [
                        "装载顺序原则：冷链物资优先装载并启动预冷（提前30分钟），食物与水按密封防潮要求后装",
                        "固定方式：高强度绑扎带（承载力>500kg）+ 防滑垫（摩擦系数>0.6）+ 限位挡板，冷链货物增加保温层固定",
                        "重心配平：前后重量比6:4（提升爬坡稳定性），左右对称（偏差<5%），冷链车制冷设备重量纳入配平计算",
                        "装载量分配：2辆冷链车各装载约50kg冷链物资，2辆普通车各装载2.5kg食物与2.5kg水，总载重约110kg",
                        "装载时间：单车装载时间约10分钟，4车并行装载+检查共计20分钟"
                    ],
                    "knowledge_trace": "车辆载重能力 + 货物类型与重量 → 装载顺序设计 → 固定方式选择 → 重心配平计算 → 装载量分配 → 时间规划。"
                },
                "movement_strategy": {
                    "title": "行进策略推理",
                    "summary": "针对道路损毁风险与冷链运输要求，设计包含低速稳态模式、坡度敏感控制、涉水绕行策略与路径重规划的多层次行进策略。",
                    "key_points": [
                        "低速稳态模式：坡度>15°或路面附着系数<0.4时自动降速至10km/h，保护冷链货物",
                        "坡度敏感控制：实时调整六轮动力分配，上坡后轮增加30%驱动力，下坡限速15km/h并启用能量回收",
                        "涉水绕行策略：水深>40cm或流速>1.5m/s时触发绕行，避免货物受损",
                        "路径重规划：支持实时感知障碍并动态重规划，重规划决策时间<30秒"
                    ],
                    "knowledge_trace": "道路损毁风险 + 冷链保护需求 → 分析各类地形场景 → 设计四类应对策略 → 形成自适应行进方案。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "terrain_input",
                                "label": "地形感知输入", "type": "input"},
                            {"id": "low_speed_mode",
                                "label": "低速稳态模式", "type": "process"},
                            {"id": "slope_control",
                                "label": "坡度敏感控制", "type": "process"},
                            {"id": "water_bypass", "label": "涉水绕行策略",
                                "type": "process"},
                            {"id": "path_replan", "label": "路径重规划",
                                "type": "decision"},
                            {"id": "strategy_output",
                                "label": "行进策略输出", "type": "output"}
                        ],
                        "edges": [
                            {"source": "terrain_input", "target": "low_speed_mode"},
                            {"source": "terrain_input", "target": "slope_control"},
                            {"source": "terrain_input", "target": "water_bypass"},
                            {"source": "low_speed_mode",
                                "target": "strategy_output"},
                            {"source": "slope_control",
                                "target": "strategy_output"},
                            {"source": "water_bypass", "target": "path_replan"},
                            {"source": "path_replan", "target": "strategy_output"}
                        ]
                    }
                },
                "low_speed_stable_mode": {
                    "title": "低速稳态模式",
                    "summary": "当检测到恶劣路况时自动切换至低速稳态行驶，保护货物并提升通过性。",
                    "key_points": [
                        "触发条件：坡度>15°、路面附着系数<0.4、颠簸加速度>2g",
                        "执行动作：速度限制至10km/h，悬挂系统切换至软模式，增强减震效果",
                        "冷链保护：低速模式下制冷系统功率提升10%，补偿颠簸导致的密封性能下降",
                        "退出条件：连续5秒路况恢复正常后，逐步恢复至正常速度（每秒增加5km/h）"
                    ],
                    "knowledge_trace": "路况传感器数据 → 触发条件判断 → 速度与悬挂调整 → 冷链补偿 → 条件恢复后逐步退出。"
                },
                "slope_sensitive_control": {
                    "title": "坡度敏感控制",
                    "summary": "根据实时坡度数据动态调整六轮动力分配与制动策略。",
                    "key_points": [
                        "坡度检测：IMU实时测量，精度±0.5°，采样频率100Hz",
                        "上坡策略：坡度>10°时后轮驱动力增加30%，坡度>20°时前后轮驱动力比调整为4:6",
                        "下坡策略：坡度>10°时自动限速至15km/h，启用制动能量回收（回收效率约25%）",
                        "极限保护：坡度>30°时触发停车警告，等待人工确认或自动规划绕行路线"
                    ],
                    "knowledge_trace": "IMU坡度测量 → 坡度区间判断 → 动力分配调整/制动策略切换 → 极限保护触发。"
                },
                "water_crossing_bypass": {
                    "title": "涉水绕行策略",
                    "summary": "基于水深与流速检测，自动决策涉水通过或绕行。",
                    "key_points": [
                        "检测手段：超声波水深传感器（精度±5cm）+ 视觉流速估计（精度±0.3m/s）",
                        "安全阈值：涉水深度<40cm且流速<1.5m/s可通过，否则触发绕行",
                        "绕行决策：优先选择上游浅滩（通常水深较浅），次选桥梁通道，最后选择远距离绕行",
                        "涉水保护：若必须涉水，速度限制至5km/h，启用防水密封，涉水后自动检测车辆状态"
                    ],
                    "knowledge_trace": "水深/流速检测 → 安全阈值比较 → 绕行决策/涉水通过 → 执行保护措施。"
                },
                "path_replanning": {
                    "title": "路径重规划",
                    "summary": "基于实时感知的障碍信息，综合车队状态与地图数据生成新的可行路径。",
                    "key_points": [
                        "路径规划：基于高精度地图（道路等级、坡度、路面类型）与实时路况（塌方、积水、施工标注）生成初始最优路径",
                        "异常感知与处理：车载传感器检测到异常后，派遣机器狗抵近观察获取精确障碍信息",
                        "动态重规划：综合车队状态（位置、电量、货物）、地图与异常信息，基于A*算法生成最优替代路径",
                        "决策效率：从异常检测到新路径输出<30秒，结果同步至所有车辆导航系统"
                    ],
                    "knowledge_trace": "路径规划（地图+路况）→ 异常感知与处理（感知异常→机器狗抵近）→ 动态重规划（车队状态+地图+异常融合）→ 新路径输出。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "path_planning", "label": "路径规划", "type": "input"},
                            {"id": "map_data", "label": "地图数据", "type": "input"},
                            {"id": "road_condition",
                                "label": "实时路况", "type": "input"},
                            {"id": "anomaly_perception",
                                "label": "异常感知与处理", "type": "process"},
                            {"id": "anomaly_detection",
                                "label": "感知数据异常", "type": "process"},
                            {"id": "robot_dog", "label": "机器狗抵近观察", "type": "process"},
                            {"id": "dynamic_replan",
                                "label": "动态重规划", "type": "decision"},
                            {"id": "fleet_status", "label": "车队状态", "type": "input"},
                            {"id": "info_fusion", "label": "地图与异常融合",
                                "type": "process"},
                            {"id": "new_path", "label": "新路径输出", "type": "output"}
                        ],
                        "edges": [
                            {"source": "map_data", "target": "path_planning"},
                            {"source": "road_condition",
                                "target": "path_planning"},
                            {"source": "path_planning",
                                "target": "anomaly_perception"},
                            {"source": "anomaly_detection",
                                "target": "anomaly_perception"},
                            {"source": "robot_dog", "target": "anomaly_perception"},
                            {"source": "anomaly_perception",
                                "target": "dynamic_replan"},
                            {"source": "fleet_status", "target": "dynamic_replan"},
                            {"source": "info_fusion", "target": "dynamic_replan"},
                            {"source": "dynamic_replan", "target": "new_path"}
                        ]
                    }
                },
                "path_planning_base": {
                    "title": "路径规划（基础）",
                    "summary": "基于高精度地图与实时路况，规划从起点到终点的最优路径。",
                    "key_points": [
                        "地图数据：使用1:10000高精度地图，包含道路等级、坡度、路面类型、历史损毁记录",
                        "路况信息：实时获取卫星影像与历史通行数据，标注高风险区域",
                        "路径计算：综合距离、时间、安全性三维权重，生成主路径与2条备选路径",
                        "预估参数：主路径110km，预计1.5小时，平均速度约73km/h，安全系数0.85"
                    ],
                    "knowledge_trace": "高精度地图 + 实时路况 → 多维权重计算 → 主路径+备选路径生成 → 预估时间与安全系数。"
                },
                "anomaly_perception": {
                    "title": "异常感知与处理",
                    "summary": "当感知数据出现异常时，派遣机器狗抵近观察获取精确信息。",
                    "key_points": [
                        "异常检测：前方道路影像与地图不符、障碍物体积超出通行空间、路面反射异常（可能积水）",
                        "机器狗派遣：从队尾释放机器狗，行进至异常点前方20m进行抵近观察",
                        "观察内容：障碍物尺寸与材质、路面承载能力、积水深度、可通行宽度",
                        "信息回传：机器狗采集数据实时回传（延迟<500ms），供重规划决策使用"
                    ],
                    "knowledge_trace": "车载传感器异常检测 → 机器狗派遣 → 抵近观察与数据采集 → 信息回传至车队。"
                },
                "dynamic_replanning": {
                    "title": "动态重规划",
                    "summary": "综合车队状态、地图与异常信息，实时计算最优替代路径。",
                    "key_points": [
                        "输入信息：车队当前位置（GPS精度<1m）、剩余电量（4车平均值）、货物状态（温度、振动）、障碍详情",
                        "约束条件：新路径必须满足2小时时限、不超过车辆续航能力、避开所有已知障碍",
                        "算法执行：基于A*的增量式路径搜索，复用已通过路段，仅重算前方路径，计算时间<30秒",
                        "输出结果：新路径坐标序列、预估到达时间、风险评级，同步至所有车辆导航系统"
                    ],
                    "knowledge_trace": "多源信息输入 → 约束条件设定 → A*增量搜索 → 新路径验证 → 车队同步。"
                },
                "map_data": {
                    "title": "地图数据",
                    "summary": "加载高精度地图数据，提供路径规划的基础地理信息。",
                    "key_points": [
                        "地图精度：1:10000高精度地图，水平精度<1m，高程精度<0.5m",
                        "道路信息：道路等级（高速/省道/县道/乡道）、车道数、路面宽度、限速信息",
                        "地形数据：坡度信息（精度±0.5°）、路面类型（沥青/水泥/碎石/土路）、弯道曲率",
                        "历史记录：历史损毁记录、维修状态、季节性风险（雨季易涝区、冬季结冰区）",
                        "设施信息：桥梁涵洞位置与限高限重、充电站、应急停车区"
                    ],
                    "knowledge_trace": "地图数据库加载 → 道路网络解析 → 地形与设施信息提取 → 为路径规划提供基础数据。"
                },
                "road_condition_data": {
                    "title": "实时路况",
                    "summary": "获取并分析实时路况信息，标注高风险区域。",
                    "key_points": [
                        "数据来源：卫星影像（分辨率<1m）、历史通行数据、气象数据、交通管制信息",
                        "更新频率：路况数据每5分钟更新一次，紧急事件实时推送",
                        "风险标注：塌方区域（红色）、积水区域（蓝色）、施工区域（黄色）、拥堵区域（橙色）",
                        "置信度评估：路况信息置信度>85%方可采信，低置信度区域触发主动探测",
                        "预测能力：基于历史数据预测未来2小时路况变化趋势"
                    ],
                    "knowledge_trace": "多源路况数据采集 → 数据融合与验证 → 风险区域标注 → 置信度评估 → 路况预测。"
                },
                "anomaly_detection": {
                    "title": "感知数据异常",
                    "summary": "车载传感器实时检测前方道路异常情况。",
                    "key_points": [
                        "视觉异常：前方道路影像与地图不符、障碍物识别（车辆/落石/倒树）、路面破损检测",
                        "雷达异常：激光雷达回波异常（可能有积水或坑洞）、障碍物体积超出通行空间",
                        "路面异常：路面反射率异常（可能积水或结冰）、颠簸加速度超出阈值",
                        "检测距离：视觉检测距离200m，激光雷达检测距离150m，超声波检测距离10m",
                        "响应时间：异常检测到告警生成<100ms，为车辆预留充足反应时间"
                    ],
                    "knowledge_trace": "多传感器数据采集 → 异常特征提取 → 阈值判断 → 异常告警生成 → 触发后续处理。"
                },
                "robot_dog_scout": {
                    "title": "派遣机器狗抵近观察",
                    "summary": "当车载传感器无法准确判断时，派遣机器狗进行抵近侦察。",
                    "key_points": [
                        "派遣条件：车载传感器检测到异常但置信度<80%、障碍物性质不明、需要精确测量",
                        "机器狗能力：四足行走（最高速度3m/s）、配备高清摄像头与激光测距仪、IP67防水",
                        "观察距离：行进至异常点前方20m进行抵近观察，避免自身陷入危险",
                        "采集内容：障碍物尺寸（精度±5cm）、材质识别、路面承载能力测试、积水深度测量、可通行宽度",
                        "数据回传：采集数据实时回传至车队（延迟<500ms），支持远程操控与自主巡检两种模式"
                    ],
                    "knowledge_trace": "异常触发派遣 → 机器狗行进至观察点 → 多维度数据采集 → 实时数据回传 → 供重规划决策。"
                },
                "fleet_status_input": {
                    "title": "车队状态",
                    "summary": "获取车队实时状态数据，作为路径重规划的重要输入。",
                    "key_points": [
                        "位置信息：各车GPS位置（精度<1m）、行驶方向、当前速度",
                        "能源状态：各车剩余电量百分比、预估剩余续航里程、能耗率",
                        "货物状态：冷链温度（目标-18°C±2°C）、振动水平、货物完整性",
                        "车辆健康：电机状态、电池健康度、传感器工作状态、轮胎气压",
                        "约束计算：基于当前状态计算可行驶最大距离、允许的最大坡度、可通过的最大水深"
                    ],
                    "knowledge_trace": "各车状态数据采集 → 数据汇总至领航车 → 约束条件计算 → 为重规划提供边界条件。"
                },
                "map_anomaly_fusion": {
                    "title": "地图与异常信息融合",
                    "summary": "将异常感知结果与高精度地图融合，生成最优替代路径。",
                    "key_points": [
                        "信息叠加：将机器狗观察结果、车载传感器数据叠加至高精度地图，标注障碍区域边界",
                        "可通行性分析：计算障碍区域的可通行边界，评估绕行代价（距离、时间、风险）",
                        "备选路线评估：从备选路线库中筛选可行路线，按综合代价排序",
                        "A*算法搜索：基于更新后的地图进行A*路径搜索，考虑距离、坡度、路况权重",
                        "决策输出：计算时间<30秒，输出最优路径坐标序列、预估到达时间、风险评级"
                    ],
                    "knowledge_trace": "异常信息叠加至地图 → 可通行边界计算 → 备选路线筛选 → A*路径搜索 → 最优路径输出。"
                },
                "risk_mitigation": {
                    "title": "风险规避与冗余方案",
                    "summary": "通过前置侦察、多路径规划与补能保障，构建多层次的风险防控体系。",
                    "key_points": [
                        "前置侦察无人机：2架小型旋翼无人机提前1km探测，识别塌方/积水/障碍，实时回传",
                        "备用路线：主路线+2条备选，路线切换决策时间<2分钟",
                        "补能策略：每30km设置快速充电站，10分钟恢复50%电量",
                        "通信冗余：4G/5G+卫星通信双备份，确保指挥端持续监控"
                    ],
                    "knowledge_trace": "风险源识别 → 侦察手段部署 → 备选方案配置 → 补能与通信保障 → 形成多层防控体系。"
                },
                "logistics_execution_plan": {
                    "title": "物流执行计划",
                    "summary": "整合车辆配置、装车方案、行进策略与风险规避措施，生成完整的物流执行方案。",
                    "key_points": [
                        "编队配置：4辆六轮越野无人车（2冷链+2常温），单次运输110kg货物",
                        "行进间隔：车间距150m，梯队协同模式，前车探路/中车主运/后车应急",
                        "车队协同：支持动态队形切换（双列↔单列），协同避障与紧急制动",
                        "状态监控：实时监控车辆状态与冷链温度，异常自动告警并同步指挥端",
                        "时间规划：装车20分钟+行进90分钟+卸货20分钟=130分钟，满足2小时时限"
                    ],
                    "knowledge_trace": "车辆配置 + 装车方案 + 行进策略 + 风险措施 → 编队与间隔设计 → 协同与监控方案 → 时间规划验证 → 形成可执行物流方案。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "task_parsing", "label": "任务解析", "type": "input"},
                            {"id": "vehicle_match",
                                "label": "车辆匹配", "type": "process"},
                            {"id": "loading", "label": "装车方案", "type": "process"},
                            {"id": "movement", "label": "行进策略推理", "type": "process"},
                            {"id": "risk", "label": "风险规避", "type": "process"},
                            {"id": "execution", "label": "物流执行计划",
                                "type": "decision"},
                            {"id": "unloading", "label": "卸货操作", "type": "output"}
                        ],
                        "edges": [
                            {"source": "task_parsing", "target": "vehicle_match"},
                            {"source": "vehicle_match", "target": "loading"},
                            {"source": "loading", "target": "movement"},
                            {"source": "movement", "target": "risk"},
                            {"source": "risk", "target": "execution"},
                            {"source": "execution", "target": "unloading"},
                            {"source": "task_parsing", "target": "execution"}
                        ]
                    }
                },
                "transport_batches": {
                    "title": "运输批次",
                    "summary": "根据任务需求与车辆配置，确定本次为单批次运输任务。",
                    "key_points": [
                        "批次数量：单批次（4辆车同时出发，无需分批）",
                        "车辆分配：2辆冷链车运输冷链物资Y，2辆普通车运输食物与水",
                        "总载重：约110kg（冷链物资100kg + 食物与水10kg）",
                        "时间节点：装车完成后统一发车，预计1.5小时后同时到达"
                    ],
                    "knowledge_trace": "任务载重需求 → 车辆数量匹配 → 批次划分决策 → 时间节点规划。"
                },
                "convoy_interval": {
                    "title": "行进间隔",
                    "summary": "设定车队内部的安全间距与跟随策略。",
                    "key_points": [
                        "标准间距：150m（约15秒行进时间差，正常速度60km/h）",
                        "安全考量：避免连环事故，单车故障不影响后车通行",
                        "通信要求：间距内保持稳定的V2V（车对车）通信，延迟<50ms",
                        "动态调整：恶劣路况时间距增至200m，紧急情况允许缩短至100m"
                    ],
                    "knowledge_trace": "安全距离计算 → 通信能力评估 → 标准间距设定 → 动态调整规则。"
                },
                "fleet_coordination": {
                    "title": "车队协同方式",
                    "summary": "采用梯队协同模式，支持动态队形调整与协同动作管理。",
                    "key_points": [
                        "编队模式：梯队协同（前车探路+中车主运+后车应急）",
                        "队形切换：宽路双列并行，窄路单列纵队，切换时间<30秒",
                        "协同动作：依序掉头、队列倒置、紧急避让、故障车辆绕行",
                        "通信协议：基于V2V的实时位置与状态共享，决策同步延迟<100ms"
                    ],
                    "knowledge_trace": "道路条件评估 → 编队模式选择 → 队形切换规则 → 协同动作库 → 通信协议保障。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "road_condition",
                                "label": "道路条件", "type": "input"},
                            {"id": "formation_plan",
                                "label": "行进编队规划", "type": "process"},
                            {"id": "coord_actions",
                                "label": "协同动作管理", "type": "process"},
                            {"id": "v2v_comm", "label": "V2V通信", "type": "process"},
                            {"id": "formation_output",
                                "label": "编队执行", "type": "output"}
                        ],
                        "edges": [
                            {"source": "road_condition",
                                "target": "formation_plan"},
                            {"source": "formation_plan",
                                "target": "coord_actions"},
                            {"source": "coord_actions",
                                "target": "formation_output"},
                            {"source": "v2v_comm", "target": "formation_plan"},
                            {"source": "v2v_comm", "target": "coord_actions"}
                        ]
                    }
                },
                "formation_planning": {
                    "title": "行进编队规划",
                    "summary": "依据道路宽度与路况，动态选择最优队形。",
                    "key_points": [
                        "宽路队形（>6m）：双列并行，冷链车在内侧（更安全），普通车在外侧",
                        "窄路队形（<6m）：单列纵队，顺序为探路车→冷链车1→冷链车2→应急车",
                        "队形切换：前车检测到道路变窄时提前500m发出切换指令，后车依次并入",
                        "特殊队形：通过障碍区时可临时拉大间距至300m，通过后恢复标准间距"
                    ],
                    "knowledge_trace": "道路宽度检测 → 队形选择 → 切换指令发送 → 各车位置调整 → 新队形形成。"
                },
                "coordination_actions": {
                    "title": "协同动作管理",
                    "summary": "管理车队在特殊场景下的协同动作执行。",
                    "key_points": [
                        "依序掉头：窄路掉头时，从队尾开始依次掉头，前车等待后车完成后再掉头",
                        "队列倒置：宽路掉头时，队列整体倒置（原队尾变队头），减少掉头时间",
                        "紧急避让：前车检测到突发障碍时，广播紧急制动指令，各车同步减速避让",
                        "故障绕行：某车故障时，后续车辆自动绕行并重新编队，故障车等待救援"
                    ],
                    "knowledge_trace": "场景识别 → 协同动作选择 → 指令广播 → 各车执行 → 队形恢复确认。"
                },
                "fleet_cargo_monitoring": {
                    "title": "车队/货物状态监控",
                    "summary": "实时监控车队运行情况与货物状态，自动识别异常并生成告警与应对策略。",
                    "key_points": [
                        "监控维度：车辆（位置/速度/电量/健康）、货物（温度/振动/完整性）",
                        "数据采集：多传感器融合，采样频率10Hz，数据融合延迟<100ms",
                        "异常检测：基于阈值与机器学习的双重检测机制",
                        "告警机制：分级告警（一般/紧急/严重），实时同步指挥端",
                        "应对策略：针对不同异常类型预设处理方案，自动执行或人工确认后执行"
                    ],
                    "knowledge_trace": "传感器数据采集 → 数据融合与分析 → 状态判别 → 异常检测 → 告警与处理。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "monitor_req", "label": "监控需求解析", "type": "input"},
                            {"id": "sensor_fusion",
                                "label": "传感器数据融合", "type": "process"},
                            {"id": "status_judge", "label": "状态判别", "type": "process"},
                            {"id": "anomaly_handle",
                                "label": "异常处理策略", "type": "decision"},
                            {"id": "alert_log", "label": "告警与记录", "type": "output"}
                        ],
                        "edges": [
                            {"source": "monitor_req", "target": "sensor_fusion"},
                            {"source": "sensor_fusion", "target": "status_judge"},
                            {"source": "status_judge", "target": "anomaly_handle"},
                            {"source": "anomaly_handle", "target": "alert_log"},
                            {"source": "status_judge", "target": "alert_log"}
                        ]
                    }
                },
                "monitoring_requirements": {
                    "title": "监控需求解析",
                    "summary": "明确车队与货物状态监控的具体项目与指标。",
                    "key_points": [
                        "车辆状态：实时位置（GPS）、行驶速度、剩余电量、系统健康状态（电机/电池/传感器）",
                        "冷链温度：目标-18°C±2°C，每30秒记录一次，超出范围立即告警",
                        "振动监测：三轴加速度，阈值<2g（正常）/<3g（警告）/<5g（危险）",
                        "能耗监测：实时功率与累计能耗，预测剩余续航里程"
                    ],
                    "knowledge_trace": "任务需求分析 → 监控项目确定 → 指标阈值设定 → 监控方案形成。"
                },
                "sensor_data_fusion": {
                    "title": "传感器数据融合",
                    "summary": "融合多种传感器数据，构建车队与货物状态的完整画像。",
                    "key_points": [
                        "传感器类型：温度传感器（精度±0.5°C）、GPS（精度<1m）、IMU（6轴）、车载健康监测OBD",
                        "采样频率：位置与速度10Hz，温度0.03Hz，振动100Hz，健康状态1Hz",
                        "融合算法：扩展卡尔曼滤波（EKF）融合多源数据，提升估计精度与鲁棒性",
                        "输出格式：统一时间戳的车队状态向量，每100ms更新一次"
                    ],
                    "knowledge_trace": "多传感器数据采集 → 时间同步 → 卡尔曼滤波融合 → 状态向量输出。"
                },
                "status_determination": {
                    "title": "状态判别",
                    "summary": "基于融合数据实时判别车队与货物的运行状态。",
                    "key_points": [
                        "温度状态：正常（-20°C~-16°C）、警告（-22°C~-20°C或-16°C~-14°C）、异常（其他）",
                        "电量状态：充足（>50%）、注意（20%~50%）、不足（<20%）",
                        "路线状态：正常（偏移<10m）、偏离（10m~50m）、严重偏离（>50m）",
                        "振动状态：正常（<2g）、警告（2g~3g）、危险（>3g持续5秒）"
                    ],
                    "knowledge_trace": "融合数据输入 → 各维度阈值判断 → 状态分类 → 综合状态评估。"
                },
                "anomaly_handling": {
                    "title": "异常处理策略",
                    "summary": "针对不同异常类型执行预设的应对策略。",
                    "key_points": [
                        "温度异常：升温→增加制冷功率/降速减少热量产生；降温过度→降低制冷功率",
                        "电量不足：导航至最近补能点，同时降速节能（限速40km/h）",
                        "路线偏移：自动纠偏返回规划路线，若无法纠偏则触发路径重规划",
                        "振动异常：立即降速至10km/h，停车检查货物固定状态，确认安全后继续"
                    ],
                    "knowledge_trace": "异常类型识别 → 策略库匹配 → 执行方案生成 → 自动/人工确认执行。"
                },
                "alert_logging": {
                    "title": "告警与记录",
                    "summary": "生成分级告警并记录完整的任务执行日志。",
                    "key_points": [
                        "告警分级：一般（黄色，提示性）、紧急（橙色，需关注）、严重（红色，需立即处理）",
                        "告警内容：时间戳、车辆ID、位置坐标、异常类型、当前值、阈值、建议措施",
                        "日志记录：全程记录车队状态变化，异常事件详细记录，支持事后回溯分析",
                        "指挥端同步：告警实时推送至指挥端（延迟<1秒），支持远程干预指令下发"
                    ],
                    "knowledge_trace": "异常检测 → 告警分级 → 告警生成与推送 → 日志记录 → 指挥端同步。"
                },
                "unloading_operation": {
                    "title": "卸货操作",
                    "summary": "在位置X(190,100)安全高效地完成货物卸载、清点确认与交接签收流程。",
                    "key_points": [
                        "卸载方式：自动液压尾板+人工辅助，单车卸载时间约3分钟",
                        "卸载顺序：冷链物资优先（保持冷链不断），其次食物与水",
                        "安全确认：检查外包装完整性、冷链温度记录、密封状态",
                        "交接流程：扫码清点、电子签名、时间戳记录、数据回传指挥端"
                    ],
                    "knowledge_trace": "到达目的地 → 卸载方式选择 → 顺序执行卸载 → 状态检查 → 交接确认 → 记录回传。"
                },
                "unloading_method": {
                    "title": "卸载方式",
                    "summary": "采用自动化与人工辅助相结合的卸载方式。",
                    "key_points": [
                        "设备配置：每车配备自动液压尾板（承载能力100kg，升降行程1.2m）",
                        "操作流程：车辆停稳→尾板展开→货物推出→尾板降至地面→人工接收",
                        "冷链特殊处理：冷链车卸载时启动便携制冷设备，确保货物在转移过程中温度不超-15°C",
                        "时间效率：单车卸载时间约3分钟，4车并行卸载+整理共计10分钟"
                    ],
                    "knowledge_trace": "卸载设备准备 → 尾板展开 → 货物转移 → 冷链保护 → 卸载完成确认。"
                },
                "unloading_sequence": {
                    "title": "顺序安排",
                    "summary": "根据货物特性安排合理的卸载顺序。",
                    "key_points": [
                        "优先级排序：冷链物资（时间敏感）> 食物（易腐） > 水（稳定）",
                        "冷链优先原因：冷链物资脱离制冷环境后温度上升较快，需优先转移至接收方冷库",
                        "并行策略：2辆冷链车同时卸载，完成后2辆普通车同时卸载",
                        "异常处理：若某车卸载设备故障，优先处理冷链车，普通车可等待人工辅助"
                    ],
                    "knowledge_trace": "货物优先级评估 → 卸载顺序确定 → 并行策略制定 → 异常预案准备。"
                },
                "safety_confirmation": {
                    "title": "安全确认",
                    "summary": "在卸载过程中检查货物状态，确保运输质量。",
                    "key_points": [
                        "外观检查：货物外包装完整性，无破损、变形、渗漏",
                        "冷链验证：核对温度记录曲线，确认全程-18°C±2°C，无断链情况",
                        "密封检查：食物与水的密封包装完好，无进水或污染迹象",
                        "异常记录：发现任何异常立即拍照存档，记录具体情况，通知接收方"
                    ],
                    "knowledge_trace": "外观检查 → 温度验证 → 密封检查 → 异常记录 → 检查结果汇总。"
                },
                "handover_process": {
                    "title": "交接流程",
                    "summary": "与接收方完成正式的货物交接手续。",
                    "key_points": [
                        "清点核对：使用扫码设备核对货物条码与清单，逐项确认数量与类型",
                        "签收确认：接收方通过移动终端进行电子签名，系统自动记录时间戳",
                        "文档生成：自动生成交接单（货物明细、状态、时间、签收人），双方各留存一份",
                        "数据回传：交接完成后，完整运输记录（含温度曲线、行驶轨迹、异常事件）回传指挥端"
                    ],
                    "knowledge_trace": "货物清点 → 电子签收 → 文档生成 → 数据回传 → 任务闭环。"
                }
            }
        },
    )
]