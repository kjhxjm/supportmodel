from typing import List
from .schema import Scenario

# 五、资源保障支援模型测试
SCENARIOS: List[Scenario] = [
     # 五、资源保障支援模型测试（18~21）
    Scenario(
        id="resource_tracking",  # 18. 资源评估 
        model_name="资源保障",
        name="资源评估",
        example_input="监控当前所有前线单位的物资状态，分配现有急救物资",
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
                "label": "📦 资源评估",
                "status": "completed",
                "summary": "将前线单位使用的物资按弹药、食物、燃料、备件等类别进行结构化建模。",
                "children": [
                    {
                        "id": "resource_evaluation",
                        "label": "资源类别解析",
                        "status": "completed",
                        "summary": "评估当前所有前线单位的物资状态，分配现有急救物资。",
                        "children": [
                            {
                                "id": "food",
                                "label": "食物",
                                "status": "completed",
                                "summary": "分类记录食物资源的种类、批次、保质期及分发情况。",
                                "children": []
                            },
                            {
                                "id": "fuel",
                                "label": "燃料",
                                "status": "completed",
                                "summary": "登记各类型燃料（汽油、柴油等）仓储与消耗状况，细化供应链节点。",
                                "children": []
                            },
                            {
                                "id": "spare_parts",
                                "label": "备件",
                                "status": "completed",
                                "summary": "建立备件库，明细备件用途、型号和配发情况，实现备品备件的可追溯性。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "tracking_method",
                        "label": "追踪方式匹配",
                        "status": "completed",
                        "summary": "为不同资源类别匹配合适的追踪手段，如RFID、二维码、GPS或无人机盘点。",
                        "children": [
                            {
                                "id": "rfid",
                                "label": "RFID",
                                "status": "completed",
                                "summary": "使用RFID技术对资源进行追踪。",
                                "children": []
                            },
                            {
                                "id": "qrcode",
                                "label": "二维码",
                                "status": "completed",
                                "summary": "使用二维码技术对资源进行追踪。",
                                "children": []
                            },
                            {
                                "id": "gps",
                                "label": "GPS",
                                "status": "completed",
                                "summary": "使用GPS技术对资源进行追踪。",
                                "children": []
                            },
                            {
                                "id": "drone",
                                "label": "无人机",
                                "status": "completed",
                                "summary": "使用无人机技术对资源进行追踪。",
                                "children": []
                            }
                        ]
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
                            {"id": "track",
                                "label": "追踪方式与读数(多节点)", "type": "process"},
                            {"id": "status",
                                "label": "资源状态更新(本地视角)", "type": "process"},
                            {"id": "local_anom", "label": "本地异常检测结果",
                                "type": "process"},
                            {"id": "consensus_anom",
                                "label": "分布式一致性异常聚合", "type": "process"},
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
    )
]