import copy


DEFAULT_NODE_INSIGHT = {
    "title": "策略节点",
    "summary": "该节点暂未配置专属描述，使用通用支援逻辑展示。",
    "key_points": [
        "调用支援模型的标准推理路径",
        "沿知识图谱回溯证据链路",
        "输出可视化行为节点"
    ],
    "knowledge_trace": "默认知识链路：任务节点 → 功能节点 → 结果节点。",
    "knowledge_graph": {
        "nodes": [
            {"id": "task_node", "label": "任务节点", "type": "input"},
            {"id": "logic_node", "label": "推理逻辑", "type": "process"},
            {"id": "result_node", "label": "结果节点", "type": "output"}
        ],
        "edges": [
            {"source": "task_node", "target": "logic_node"},
            {"source": "logic_node", "target": "result_node"}
        ]
    }
}


def _build_default_behavior_tree():
    return {
        "id": "task_ingest",
        "label": "任务描述解析",
        "status": "completed",
        "summary": "解析输入内容，提炼任务地点、风险与关键目标。",
        "children": [
            {
                "id": "environment_scan",
                "label": "环境与威胁识别",
                "status": "active",
                "summary": "结合多源数据识别地形、天气与潜在威胁。",
                "children": [
                    {
                        "id": "terrain_analysis",
                        "label": "地形与通路分析",
                        "status": "active",
                        "summary": "分析地形起伏、道路等级和关键通路节点。",
                        "children": [
                            {
                                "id": "risk_corridor_left",
                                "label": "左侧通路风险评估",
                                "status": "pending",
                                "summary": "评估左侧候选通路的障碍和暴露风险。",
                                "children": []
                            },
                            {
                                "id": "risk_corridor_right",
                                "label": "右侧通路风险评估",
                                "status": "pending",
                                "summary": "评估右侧候选通路的障碍和暴露风险。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "threat_monitor",
                        "label": "威胁与干扰监测",
                        "status": "pending",
                        "summary": "识别敌情、天气和其它对任务的干扰源。",
                        "children": [
                            {
                                "id": "threat_near",
                                "label": "近距威胁识别",
                                "status": "pending",
                                "summary": "识别任务区域附近的直接威胁。",
                                "children": []
                            },
                            {
                                "id": "threat_far",
                                "label": "远距威胁识别",
                                "status": "pending",
                                "summary": "识别外围区域的潜在威胁与预警信号。",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            {
                "id": "resource_match",
                "label": "资源能力匹配",
                "status": "pending",
                "summary": "根据任务需求选配可用装备与队伍。",
                "children": [
                    {
                        "id": "inventory_check",
                        "label": "库存与状态核查",
                        "status": "pending",
                        "summary": "检查可用资源数量、健康状态与位置分布。",
                        "children": [
                            {
                                "id": "inventory_front",
                                "label": "前沿资源检查",
                                "status": "pending",
                                "summary": "核查前沿节点可立即调用的资源。",
                                "children": []
                            },
                            {
                                "id": "inventory_rear",
                                "label": "后方资源检查",
                                "status": "pending",
                                "summary": "统计后方仓库和补给线上的资源余量。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "capability_binding",
                        "label": "能力与任务绑定",
                        "status": "pending",
                        "summary": "将不同资源能力映射到任务步骤。",
                        "children": [
                            {
                                "id": "capability_primary",
                                "label": "主能力匹配",
                                "status": "pending",
                                "summary": "优先为关键任务节点分配核心能力资源。",
                                "children": []
                            },
                            {
                                "id": "capability_backup",
                                "label": "备份能力匹配",
                                "status": "pending",
                                "summary": "为关键节点准备备份资源和兜底方案。",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            {
                "id": "plan_output",
                "label": "策略输出与校验",
                "status": "pending",
                "summary": "生成行为树节点并输出执行指令。",
                "children": [
                    {
                        "id": "plan_simulation",
                        "label": "方案仿真校验",
                        "status": "pending",
                        "summary": "对生成的方案进行时间、资源和风险仿真。",
                        "children": [
                            {
                                "id": "plan_fast",
                                "label": "快速执行路径评估",
                                "status": "pending",
                                "summary": "评估以时间最优为目标的方案。",
                                "children": []
                            },
                            {
                                "id": "plan_safe",
                                "label": "安全优先路径评估",
                                "status": "pending",
                                "summary": "评估以安全性为目标的备选方案。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "plan_publish",
                        "label": "指令发布与反馈绑定",
                        "status": "pending",
                        "summary": "将方案下发到执行单元并绑定反馈通道。",
                        "children": [
                            {
                                "id": "publish_order",
                                "label": "发布执行指令",
                                "status": "pending",
                                "summary": "生成面向一线单位的具体操作指令。",
                                "children": []
                            },
                            {
                                "id": "feedback_loop",
                                "label": "建立反馈闭环",
                                "status": "pending",
                                "summary": "收集执行过程中的状态反馈并用于后续修正。",
                                "children": []
                            }
                        ]
                    }
                ]
            }
        ]
    }


def _build_default_node_insights():
    return {
        "task_ingest": {
            "title": "任务描述解析",
            "summary": "从自然语言输入中抽取关键任务要素，标注时间、地点与约束条件。",
            "key_points": [
                "启动语义解析与事件抽取模型",
                "映射至支援模型任务模板库",
                "输出结构化指令供后续节点使用"
            ],
            "knowledge_trace": "任务输入与支援模型模板进行语义对齐，确保推理入口正确。"
        },
        "environment_scan": {
            "title": "环境与威胁识别",
            "summary": "融合遥感、战场感知与地形库数据，判定路径可行性与风险。",
            "key_points": [
                "调用环境态势子图识别地形/天气标签",
                "比对历史风险节点输出威胁标签",
                "为资源匹配节点提供约束"
            ],
            "knowledge_trace": "“地形标签→通行能力→策略库”链路驱动该节点输出。"
        },
        "resource_match": {
            "title": "资源能力匹配",
            "summary": "根据任务约束自动匹配平台、装备与班组，输出可执行组合。",
            "key_points": [
                "检索资源库可用度与状态",
                "对接环境约束过滤不合规资源",
                "生成候选组合供策略节点调用"
            ],
            "knowledge_trace": "资源节点沿装备规格→能力指标→任务适配度链路与任务对齐。",
            "knowledge_graph": {
                "nodes": [
                    {"id": "task_requirements", "label": "任务需求", "type": "input"},
                    {"id": "resource_inventory", "label": "资源库存", "type": "input"},
                    {"id": "environment_constraints", "label": "环境约束", "type": "input"},
                    {"id": "capability_filtering", "label": "能力筛选", "type": "process"},
                    {"id": "combination_generation", "label": "组合生成", "type": "decision"},
                    {"id": "execution_plan", "label": "执行方案", "type": "output"}
                ],
                "edges": [
                    {"source": "task_requirements", "target": "capability_filtering"},
                    {"source": "resource_inventory", "target": "capability_filtering"},
                    {"source": "environment_constraints", "target": "capability_filtering"},
                    {"source": "capability_filtering", "target": "combination_generation"},
                    {"source": "combination_generation", "target": "execution_plan"}
                ]
            }
        },
        "plan_output": {
            "title": "策略输出与校验",
            "summary": "将行为树节点序列化为执行指令，联动仿真/实装系统进行校验。",
            "key_points": [
                "收敛上游节点的条件与动作",
                "对接仿真校验接口验证可行性",
                "输出结构化策略树供展示"
            ],
            "knowledge_trace": "“行为节点→动作模板→执行接口”链路标注清晰，可供回溯。"
        },
        "terrain_analysis": {
            "title": "地形与通路分析",
            "summary": "分析地形起伏、道路等级和关键通路节点。",
            "key_points": [
                "地形数据解析与建模",
                "通路可行性评估",
                "关键节点识别"
            ],
            "knowledge_trace": "地形分析为路径规划提供基础数据。"
        },
        "threat_monitor": {
            "title": "威胁与干扰监测",
            "summary": "识别敌情、天气和其它对任务的干扰源。",
            "key_points": [
                "威胁源识别",
                "干扰因素分析",
                "风险评估"
            ],
            "knowledge_trace": "威胁监测确保任务安全执行。"
        },
        "threat_near": {
            "title": "近距威胁识别",
            "summary": "识别任务区域附近的直接威胁。",
            "key_points": [
                "近距离威胁检测",
                "即时风险评估",
                "应对措施制定"
            ],
            "knowledge_trace": "近距威胁直接影响任务执行。"
        },
        "threat_far": {
            "title": "远距威胁识别",
            "summary": "识别外围区域的潜在威胁与预警信号。",
            "key_points": [
                "外围威胁监控",
                "预警信号识别",
                "潜在风险评估"
            ],
            "knowledge_trace": "远距威胁需提前预警。"
        },
        "risk_corridor_left": {
            "title": "左侧通路风险评估",
            "summary": "评估左侧候选通路的障碍和暴露风险。",
            "key_points": [
                "左侧路径分析",
                "障碍物识别",
                "暴露风险评估"
            ],
            "knowledge_trace": "路径风险评估确保选择最安全路线。"
        },
        "risk_corridor_right": {
            "title": "右侧通路风险评估",
            "summary": "评估右侧候选通路的障碍和暴露风险。",
            "key_points": [
                "右侧路径分析",
                "障碍物识别",
                "暴露风险评估"
            ],
            "knowledge_trace": "路径风险评估确保选择最安全路线。"
        },
        "inventory_check": {
            "title": "库存与状态核查",
            "summary": "检查可用资源数量、健康状态与位置分布。",
            "key_points": [
                "库存数量统计",
                "资源状态评估",
                "位置分布分析"
            ],
            "knowledge_trace": "库存核查确保资源可用性。"
        },
        "inventory_front": {
            "title": "前沿资源检查",
            "summary": "核查前沿节点可立即调用的资源。",
            "key_points": [
                "前沿资源清点",
                "即时可用性验证",
                "快速响应资源评估"
            ],
            "knowledge_trace": "前沿资源是第一响应能力。"
        },
        "inventory_rear": {
            "title": "后方资源检查",
            "summary": "统计后方仓库和补给线上的资源余量。",
            "key_points": [
                "后方库存统计",
                "补给线资源评估",
                "后备资源分析"
            ],
            "knowledge_trace": "后方资源支持持续作战。"
        },
        "capability_binding": {
            "title": "能力与任务绑定",
            "summary": "将不同资源能力映射到任务步骤。",
            "key_points": [
                "能力任务匹配",
                "资源分配优化",
                "执行步骤规划"
            ],
            "knowledge_trace": "能力绑定确保任务执行效率。"
        },
        "capability_primary": {
            "title": "主能力匹配",
            "summary": "优先为关键任务节点分配核心能力资源。",
            "key_points": [
                "核心能力识别",
                "关键节点匹配",
                "优先资源分配"
            ],
            "knowledge_trace": "主能力匹配保证关键任务完成。"
        },
        "capability_backup": {
            "title": "备份能力匹配",
            "summary": "为关键节点准备备份资源和兜底方案。",
            "key_points": [
                "备份资源准备",
                "冗余能力配置",
                "应急方案制定"
            ],
            "knowledge_trace": "备份能力确保任务可靠性。"
        },
        "plan_simulation": {
            "title": "方案仿真校验",
            "summary": "对生成的方案进行时间、资源和风险仿真。",
            "key_points": [
                "方案仿真模拟",
                "时间资源评估",
                "风险分析验证"
            ],
            "knowledge_trace": "仿真校验确保方案可行性。"
        },
        "plan_fast": {
            "title": "快速执行路径评估",
            "summary": "评估以时间最优为目标的方案。",
            "key_points": [
                "时间优化分析",
                "快速响应路径",
                "效率优先评估"
            ],
            "knowledge_trace": "快速路径适用于紧急情况。"
        },
        "plan_safe": {
            "title": "安全优先路径评估",
            "summary": "评估以安全性为目标的备选方案。",
            "key_points": [
                "安全性评估",
                "风险最小化路径",
                "安全优先策略"
            ],
            "knowledge_trace": "安全路径确保人员和装备安全。"
        },
        "plan_publish": {
            "title": "指令发布与反馈绑定",
            "summary": "将方案下发到执行单元并绑定反馈通道。",
            "key_points": [
                "指令下发机制",
                "执行单元对接",
                "反馈通道建立"
            ],
            "knowledge_trace": "指令发布启动执行流程。"
        },
        "publish_order": {
            "title": "发布执行指令",
            "summary": "生成面向一线单位的具体操作指令。",
            "key_points": [
                "具体指令生成",
                "一线单位对接",
                "操作指导制定"
            ],
            "knowledge_trace": "执行指令指导实际操作。"
        },
        "feedback_loop": {
            "title": "建立反馈闭环",
            "summary": "收集执行过程中的状态反馈并用于后续修正。",
            "key_points": [
                "状态反馈收集",
                "执行过程监控",
                "动态修正机制"
            ],
            "knowledge_trace": "反馈闭环确保执行效果。"
        }
    }


DEFAULT_BLUEPRINT = {
    "default_focus": "environment_scan",
    "behavior_tree": _build_default_behavior_tree(),
    "node_insights": _build_default_node_insights()
}


def build_generic_blueprint(root_label, root_summary=None, node_insight_overrides=None):
    """基于默认模板构造通用支援模型蓝图"""
    blueprint = copy.deepcopy(DEFAULT_BLUEPRINT)
    if root_label:
        blueprint["behavior_tree"]["label"] = root_label
    if root_summary:
        blueprint["behavior_tree"]["summary"] = root_summary

    if node_insight_overrides:
        for node_id, overrides in node_insight_overrides.items():
            node = blueprint["node_insights"].setdefault(node_id, {})
            node.update(overrides)

    return blueprint


__all__ = [
    "DEFAULT_BLUEPRINT",
    "DEFAULT_NODE_INSIGHT",
    "build_generic_blueprint",
    "SUPPORT_MODEL_INTERFACE"
]


# ============================================================================
# 🚀 支援模型开发接口规范
# ============================================================================

SUPPORT_MODEL_INTERFACE = """
支援模型开发接口规范 v1.0
========================

📋 概述
--------
本框架提供统一的支援模型开发接口，开发者只需实现特定的数据结构即可快速集成新模型。

🎯 核心接口
-----------

1. 模型蓝图 (BLUEPRINT)
   数据结构: dict
   必需字段:
   - default_focus: str        # 默认聚焦的节点ID
   - behavior_tree: dict       # 行为树结构
   - node_insights: dict       # 节点洞察信息

2. 行为树节点结构
   {
     "id": "node_id",           # 唯一标识符
     "label": "显示名称",       # UI显示的标签
     "status": "pending",       # 状态: pending/active/completed
     "summary": "节点描述",     # 简要说明
     "children": [...]          # 子节点列表
   }

3. 节点洞察结构
   {
     "title": "洞察标题",
     "summary": "详细描述",
     "key_points": ["要点1", "要点2"],
     "knowledge_trace": "推理过程",
     "knowledge_graph": {       # 可选: 知识图谱
       "nodes": [...],
       "edges": [...]
     }
   }

🔧 开发步骤
-----------

步骤1: 创建模型文件
   support_models/your_model.py

步骤2: 实现模型蓝图
   YOUR_BLUEPRINT = {
       "default_focus": "your_main_node",
       "behavior_tree": build_your_behavior_tree(),
       "node_insights": build_your_insights()
   }

步骤3: 注册模型
   在 __init__.py 中:
   from .your_model import YOUR_BLUEPRINT
   SUPPORT_MODELS.append("你的模型名称")
   _BLUEPRINTS["你的模型名称"] = YOUR_BLUEPRINT

🌟 高级功能
-----------

1. 动态生成 (Dynamic Generation)
   支持根据任务描述动态生成蓝图:
   def generate_dynamic_blueprint(task_description):
       # 解析任务
       parsed_info = parse_task_description(task_description)
       # 生成自定义蓝图
       return customized_blueprint

2. 知识图谱 (Knowledge Graph)
   支持可视化推理过程:
   "knowledge_graph": {
       "nodes": [
           {"id": "input_node", "label": "输入", "type": "input"},
           {"id": "process_node", "label": "处理", "type": "process"},
           {"id": "output_node", "label": "输出", "type": "output"}
       ],
       "edges": [
           {"source": "input_node", "target": "process_node"},
           {"source": "process_node", "target": "output_node"}
       ]
   }

📚 示例代码
-----------

# 简单模型示例
SIMPLE_BLUEPRINT = {
    "default_focus": "main_task",
    "behavior_tree": {
        "id": "main_task",
        "label": "主要任务",
        "status": "active",
        "summary": "执行主要任务逻辑",
        "children": []
    },
    "node_insights": {
        "main_task": {
            "title": "主要任务",
            "summary": "任务执行逻辑",
            "key_points": ["步骤1", "步骤2"],
            "knowledge_trace": "推理过程"
        }
    }
}

🔌 API接口
-----------

GET  /api/models          # 获取所有可用模型
POST /api/update          # 生成行为树和洞察
POST /api/node_insight    # 获取节点详细洞察

📞 开发支持
-----------
如需帮助，请参考现有模型的实现：
- offroad_logistics.py    (动态生成示例)
- casualty_rescue.py      (静态蓝图示例)
- base.py                 (基础工具函数)
"""

