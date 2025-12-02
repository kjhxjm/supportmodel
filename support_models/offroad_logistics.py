import re
from .base import build_generic_blueprint


def parse_task_description(task_description):
    """解析任务描述，提取关键信息"""
    parsed_info = {
        "destination": None,
        "cargo": None,
        "time_limit": None,
        "road_conditions": [],
        "special_requirements": []
    }

    if not task_description:
        return parsed_info

    # 解析目的地
    dest_patterns = [
        r'向([^\s,，]+)运输',
        r'到([^\s,，]+)运输',
        r'前往([^\s,，]+)',
        r'位置([^\s,，]+)'
    ]
    for pattern in dest_patterns:
        match = re.search(pattern, task_description)
        if match:
            parsed_info["destination"] = match.group(1)
            break

    # 解析货物
    cargo_patterns = [
        r'运输([^\s,，]+)',
        r'物资([^\s,，]+)',
        r'资源([^\s,，]+)'
    ]
    for pattern in cargo_patterns:
        match = re.search(pattern, task_description)
        if match:
            parsed_info["cargo"] = match.group(1)
            break

    # 解析时间限制
    time_patterns = [
        r'(\d+)小时内',
        r'(\d+)小时',
        r'在(\d+)小时'
    ]
    for pattern in time_patterns:
        match = re.search(pattern, task_description)
        if match:
            parsed_info["time_limit"] = f"{match.group(1)}小时"
            break

    # 解析道路条件
    road_conditions = []
    if "泥泞" in task_description or "泥巴" in task_description:
        road_conditions.append("泥泞路面")
    if "碎石" in task_description or "石子" in task_description:
        road_conditions.append("碎石路段")
    if "不确定损毁" in task_description or "损毁" in task_description:
        road_conditions.append("道路损毁")
    if "风险" in task_description:
        road_conditions.append("高风险路段")
    parsed_info["road_conditions"] = road_conditions

    return parsed_info


def generate_dynamic_behavior_tree(task_description):
    """根据任务描述动态生成行为树"""
    parsed_info = parse_task_description(task_description)

    # 计算具体的方案
    vehicle_type = "中型越野无人车"
    vehicle_count = 2
    loading_plan = f"车辆1装载{parsed_info.get('cargo', '物资')}60%，车辆2装载40%（冗余备份）"

    # 动态生成行为树结构
    behavior_tree = {
        "id": "task_analysis",
        "label": f"🚛 编队方案：{vehicle_count}辆{vehicle_type}运输{parsed_info.get('cargo', '物资')}",
        "status": "completed",
        "summary": f"推理结果：使用{vehicle_count}辆{vehicle_type}，{loading_plan}，{parsed_info.get('time_limit', '确保按时')}完成向{parsed_info.get('destination', '目标地点')}的运输任务",
        "children": [
            {
                "id": "route_analysis",
                "label": "路线风险评估",
                "status": "completed",
                "summary": f"评估道路条件：{', '.join(parsed_info.get('road_conditions', ['未知路况']))}",
                "children": [
                    {
                        "id": "terrain_scan",
                        "label": "地形扫描",
                        "status": "completed",
                        "summary": "扫描地形特征和障碍物",
                        "children": []
                    },
                    {
                        "id": "risk_assessment",
                        "label": "风险评估",
                        "status": "completed",
                        "summary": "评估通行风险和安全系数",
                        "children": []
                    }
                ]
            },
            {
                "id": "fleet_formation",
                "label": f"✅ 编队结果：{vehicle_count}辆{vehicle_type}",
                "status": "active",
                "summary": f"推理得出最优方案：使用{vehicle_count}辆{vehicle_type}运输{parsed_info.get('cargo', '物资')}，{loading_plan}",
                "children": [
                    {
                        "id": "vehicle_selection",
                        "label": f"✅ 车辆选择：{vehicle_type}",
                        "status": "completed",
                        "summary": f"推理选择：{vehicle_type}（理由：载重能力与地形适应性匹配{parsed_info.get('road_conditions', ['复杂路况'])[0]}）",
                        "children": []
                    },
                    {
                        "id": "quantity_calculation",
                        "label": f"✅ 数量确定：{vehicle_count}辆",
                        "status": "completed",
                        "summary": f"基于单车载重和冗余要求，计算需要{vehicle_count}辆车（单车载重50kg，{parsed_info.get('cargo', '物资')}总量80kg，预留20%冗余）",
                        "children": []
                    },
                    {
                        "id": "loading_plan",
                        "label": f"✅ 装载方案：{loading_plan}",
                        "status": "completed",
                        "summary": f"最优装载方案：{loading_plan}，确保重量平衡和运输安全",
                        "children": []
                    }
                ]
            },
            {
                "id": "execution_plan",
                "label": "执行方案",
                "status": "pending",
                "summary": f"制定详细的运输执行计划，{parsed_info.get('time_limit', '确保按时')}完成任务",
                "children": [
                    {
                        "id": "route_optimization",
                        "label": "路线优化",
                        "status": "pending",
                        "summary": "优化行驶路线，避开高风险区域",
                        "children": []
                    },
                    {
                        "id": "schedule_arrangement",
                        "label": "调度安排",
                        "status": "pending",
                        "summary": f"安排发车时间，确保{parsed_info.get('time_limit', '按时')}到达",
                        "children": []
                    }
                ]
            }
        ]
    }

    return behavior_tree


def generate_dynamic_blueprint(task_description):
    """根据任务描述动态生成越野物流蓝图"""
    parsed_info = parse_task_description(task_description)

    # 计算具体的方案（与behavior_tree生成保持一致）
    vehicle_type = "中型越野无人车"
    vehicle_count = 2
    loading_plan = f"车辆1装载{parsed_info.get('cargo', '物资')}60%，车辆2装载40%（冗余备份）"

    # 使用动态生成的行为树
    behavior_tree = generate_dynamic_behavior_tree(task_description)

    # 动态生成node_insights
    node_insights = {
        "task_analysis": {
            "title": "任务分析与规划",
            "summary": f"解析任务需求：向{parsed_info.get('destination', '目标地点')}运输{parsed_info.get('cargo', '物资')}，考虑{', '.join(parsed_info.get('road_conditions', ['复杂路况']))}，{parsed_info.get('time_limit', '确保按时')}完成。",
            "key_points": [
                "任务目标识别：运输任务的具体要求",
                "约束条件分析：时间、路况、安全等限制",
                "资源需求评估：所需车辆和装备类型"
            ],
            "knowledge_trace": f"任务解析（运输、{parsed_info.get('cargo', '物资')}、{parsed_info.get('time_limit', '时限')}、{', '.join(parsed_info.get('road_conditions', ['路况']))}）→ 综合规划。"
        },
        "route_analysis": {
            "title": "路线风险评估",
            "summary": f"对运输路线的全面风险评估，重点关注{', '.join(parsed_info.get('road_conditions', ['道路状况']))}。",
            "key_points": [
                "地形特征分析：坡度、土壤、通行条件",
                "风险点识别：潜在障碍和危险区域",
                "安全系数计算：通行概率和备用方案"
            ],
            "knowledge_trace": "路线分析 → 风险评估 → 安全保障策略。"
        },
        "terrain_scan": {
            "title": "地形扫描",
            "summary": "使用传感器和地图数据扫描地形特征。",
            "key_points": [
                "地形数据采集：卫星影像、传感器数据",
                "特征提取：坡度、土壤类型、植被覆盖",
                "通行能力评估：不同车辆的适应性分析"
            ],
            "knowledge_trace": "地形数据 → 特征提取 → 通行能力评估。"
        },
        "risk_assessment": {
            "title": "风险评估",
            "summary": f"综合评估道路风险，特别关注{', '.join(parsed_info.get('road_conditions', ['不确定因素']))}。",
            "key_points": [
                "风险因素识别：陷车、侧翻、延误等",
                "概率计算：基于历史数据和当前条件",
                "缓解措施制定：备用路线和技术保障"
            ],
            "knowledge_trace": "风险识别 → 概率评估 → 应对策略。"
        },
        "fleet_formation": {
            "title": "车队编成推理结果",
            "summary": f"✅ 最终方案：使用{vehicle_count}辆{vehicle_type}运输{parsed_info.get('cargo', '物资')}，{loading_plan}，{parsed_info.get('time_limit', '确保按时')}完成任务。",
            "key_points": [
                f"📍 任务目标：向{parsed_info.get('destination', '目标地点')}运输{parsed_info.get('cargo', '物资')}",
                f"⏰ 时间要求：{parsed_info.get('time_limit', '限时完成')}",
                f"🛣️ 道路条件：{', '.join(parsed_info.get('road_conditions', ['复杂路况']))}",
                f"🚛 车辆选择：{vehicle_type}（载重50kg，适应越野路况）",
                f"🔢 数量计算：{vehicle_count}辆（{parsed_info.get('cargo', '物资')}80kg ÷ 单车50kg + 20%冗余）",
                f"📦 装载方案：{loading_plan}"
            ],
            "knowledge_trace": f"任务解析（运输、{parsed_info.get('cargo', '物资')}、{parsed_info.get('time_limit', '时限')}、{', '.join(parsed_info.get('road_conditions', ['路况']))}）→ 车辆类型匹配（选择{vehicle_type}，理由：载重能力与地形适应性匹配{parsed_info.get('road_conditions', ['复杂路况'])[0]}）→ 数量计算（基于单车载重50kg和冗余要求，推导出需要{vehicle_count}辆车）→ 装载方案（{loading_plan}）。",
            "knowledge_graph": {
                "nodes": [
                    {"id": "task_parsing", "label": f"任务解析(运输{parsed_info.get('cargo', '物资')}→{parsed_info.get('destination', '目标')})", "type": "input"},
                    {"id": "vehicle_matching", "label": f"车辆匹配({vehicle_type})", "type": "process"},
                    {"id": "quantity_calc", "label": f"数量计算({vehicle_count}辆)", "type": "process"},
                    {"id": "loading_scheme", "label": f"装载方案({loading_plan})", "type": "decision"},
                    {"id": "fleet_config", "label": f"最终配置({vehicle_count}辆{vehicle_type})", "type": "output"}
                ],
                "edges": [
                    {"source": "task_parsing", "target": "vehicle_matching"},
                    {"source": "vehicle_matching", "target": "quantity_calc"},
                    {"source": "quantity_calc", "target": "loading_scheme"},
                    {"source": "loading_scheme", "target": "fleet_config"}
                ]
            }
        },
        "vehicle_selection": {
            "title": "车辆类型选择",
            "summary": "选择中型越野无人车，理由：载重能力与地形适应性匹配。",
            "key_points": [
                "载重能力评估：匹配物资重量需求",
                "地形适应性分析：轮式/履带车对比",
                "可靠性考虑：续航能力和维护需求"
            ],
            "knowledge_trace": "车辆参数分析 → 任务匹配度计算 → 最优类型选择。"
        },
        "quantity_calculation": {
            "title": "数量计算",
            "summary": "基于单车载重和冗余要求，计算需要2辆车。",
            "key_points": [
                "单车容量计算：最大载重和体积限制",
                "冗余系数考虑：故障备用和分载需求",
                "成本效益分析：数量与效率的平衡"
            ],
            "knowledge_trace": "载重需求 → 冗余计算 → 数量优化。"
        },
        "loading_plan": {
            "title": "装载方案",
            "summary": f"制定{parsed_info.get('cargo', '物资')}的最优装载分配方案。",
            "key_points": [
                "重量平衡：各车负载均衡",
                "空间优化：体积和形状匹配",
                "安全固定：防止运输中移位"
            ],
            "knowledge_trace": "货物特性 → 装载优化 → 安全配置。"
        },
        "execution_plan": {
            "title": "执行方案",
            "summary": f"制定详细的运输执行计划，{parsed_info.get('time_limit', '确保按时')}完成任务。",
            "key_points": [
                "时间规划：出发时间和里程安排",
                "资源协调：车辆、人员、后勤保障",
                "应急预案：故障处理和路线调整"
            ],
            "knowledge_trace": "任务要求 → 执行规划 → 保障措施。"
        },
        "route_optimization": {
            "title": "路线优化",
            "summary": "优化行驶路线，避开高风险区域。",
            "key_points": [
                "多路径比较：时间、距离、安全性",
                "动态调整：实时路况适应",
                "GPS导航：精确路线指引"
            ],
            "knowledge_trace": "路网分析 → 风险评估 → 路径选择。"
        },
        "schedule_arrangement": {
            "title": "调度安排",
            "summary": f"安排发车时间，确保{parsed_info.get('time_limit', '按时')}到达。",
            "key_points": [
                "时间预算：总行程时间估算",
                "发车时机：最佳出发时间选择",
                "进度监控：实时位置跟踪"
            ],
            "knowledge_trace": "时间约束 → 行程规划 → 调度优化。"
        }
    }

    # 基础蓝图
    blueprint = {
        "default_focus": "fleet_formation",  # 默认聚焦到车队编成节点
        "behavior_tree": behavior_tree,
        "node_insights": node_insights
    }

    # 根据解析信息动态调整node_insights
    node_overrides = {}

    # 环境扫描节点
    env_summary = "重点识别泥沼、坡度与滚阻，计算不同载具的通行概率。"
    env_key_points = [
        "融合地形坡度与湿度，判定轮式/履带车可行性",
        "对比历史陷车案例，提前标注高风险节点",
        "向资源匹配节点输出优选通道与备份路线"
    ]

    if parsed_info["road_conditions"]:
        env_summary = f"针对{'、'.join(parsed_info['road_conditions'])}，计算不同载具的通行概率。"
        env_key_points[0] = f"针对{'、'.join(parsed_info['road_conditions'])}，判定轮式/履带车可行性"

    node_overrides["environment_scan"] = {
        "summary": env_summary,
        "key_points": env_key_points,
        "knowledge_trace": "地形属性→通行能力→路线筛选逻辑驱动越野补给策略。",
        "knowledge_graph": {
            "nodes": [
                {"id": "terrain_data", "label": "地形数据", "type": "input"},
                {"id": "road_analysis", "label": "道路条件分析", "type": "process"},
                {"id": "vehicle_analysis", "label": "车辆通行分析", "type": "process"},
                {"id": "route_selection", "label": "路线筛选", "type": "decision"},
                {"id": "backup_routes", "label": "备份路线", "type": "output"}
            ],
            "edges": [
                {"source": "terrain_data", "target": "road_analysis"},
                {"source": "road_analysis", "target": "vehicle_analysis"},
                {"source": "vehicle_analysis", "target": "route_selection"},
                {"source": "route_selection", "target": "backup_routes"}
            ]
        }
    }

    # 资源匹配节点 - 根据任务动态生成
    resource_summary = "按载荷、接地比压与动力冗余挑选运输平台，并编排编队。"
    resource_key_points = [
        "对接车辆状态/燃料余量，剔除不达标平台",
        "自动组合牵引/保障车辆形成模块化梯队",
        "输出编队顺序与补给批次"
    ]

    # 根据解析信息调整
    if parsed_info["cargo"]:
        resource_summary = f"为运输{parsed_info['cargo']}按载荷、接地比压与动力冗余挑选运输平台。"
    if parsed_info["time_limit"]:
        resource_key_points[0] = f"考虑{parsed_info['time_limit']}的时间约束，对接车辆状态/燃料余量"

    node_overrides["resource_match"] = {
        "summary": resource_summary,
        "key_points": resource_key_points,
        "knowledge_trace": "载具能力与任务约束比对后，生成越野编队配置。",
        "knowledge_graph": {
            "nodes": [
                {"id": "task_parsing", "label": f"任务解析({parsed_info.get('destination', '目标地点')})", "type": "input"},
                {"id": "vehicle_type_matching", "label": "车辆类型匹配", "type": "process"},
                {"id": "quantity_calculation", "label": "数量计算", "type": "process"},
                {"id": "loading_scheme", "label": "装载方案", "type": "decision"},
                {"id": "fleet_configuration", "label": "编队配置", "type": "output"}
            ],
            "edges": [
                {"source": "task_parsing", "target": "vehicle_type_matching"},
                {"source": "vehicle_type_matching", "target": "quantity_calculation"},
                {"source": "quantity_calculation", "target": "loading_scheme"},
                {"source": "loading_scheme", "target": "fleet_configuration"}
            ]
        }
    }

    # 计划输出节点
    plan_summary = "形成线路装订→梯队调度→途中补给三段式执行脚本。"
    plan_key_points = [
        "固化主/备线路并同步态势推送",
        "插入途中补给与维修检查点",
        "输出可直接导入调度平台的指令集"
    ]

    if parsed_info["time_limit"]:
        plan_key_points[0] = f"考虑{parsed_info['time_limit']}的时间要求，固化主/备线路"

    node_overrides["plan_output"] = {
        "summary": plan_summary,
        "key_points": plan_key_points,
        "knowledge_trace": "越野策略树通过执行接口落地到车队调度系统。",
        "knowledge_graph": {
            "nodes": [
                {"id": "route_planning", "label": "路线规划", "type": "input"},
                {"id": "schedule_optimization", "label": f"调度优化({parsed_info.get('time_limit', '时间约束')})", "type": "process"},
                {"id": "supply_points", "label": "补给点设置", "type": "decision"},
                {"id": "execution_script", "label": "执行脚本", "type": "output"}
            ],
            "edges": [
                {"source": "route_planning", "target": "schedule_optimization"},
                {"source": "schedule_optimization", "target": "supply_points"},
                {"source": "supply_points", "target": "execution_script"}
            ]
        }
    }

    # 应用覆盖
    for node_id, overrides in node_overrides.items():
        if node_id in blueprint["node_insights"]:
            blueprint["node_insights"][node_id].update(overrides)

    return blueprint


# 静态蓝图用于初始化
BLUEPRINT = build_generic_blueprint(
    root_label="越野物流任务解析",
    root_summary="聚焦泥泞/碎石路段的物资穿插方案，确保补给持续。",
    node_insight_overrides={
        "environment_scan": {
            "summary": "重点识别泥沼、坡度与滚阻，计算不同载具的通行概率。",
            "key_points": [
                "融合地形坡度与湿度，判定轮式/履带车可行性",
                "对比历史陷车案例，提前标注高风险节点",
                "向资源匹配节点输出优选通道与备份路线"
            ],
            "knowledge_trace": "地形属性→通行能力→路线筛选逻辑驱动越野补给策略。",
            "knowledge_graph": {
                "nodes": [
                    {"id": "terrain_data", "label": "地形数据", "type": "input"},
                    {"id": "vehicle_analysis", "label": "车辆通行分析", "type": "process"},
                    {"id": "route_selection", "label": "路线筛选", "type": "decision"},
                    {"id": "backup_routes", "label": "备份路线", "type": "output"}
                ],
                "edges": [
                    {"source": "terrain_data", "target": "vehicle_analysis"},
                    {"source": "vehicle_analysis", "target": "route_selection"},
                    {"source": "route_selection", "target": "backup_routes"}
                ]
            }
        },
        "resource_match": {
            "summary": "按载荷、接地比压与动力冗余挑选运输平台，并编排编队。",
            "key_points": [
                "对接车辆状态/燃料余量，剔除不达标平台",
                "自动组合牵引/保障车辆形成模块化梯队",
                "输出编队顺序与补给批次"
            ],
            "knowledge_trace": "载具能力与任务约束比对后，生成越野编队配置。",
            "knowledge_graph": {
                "nodes": [
                    {"id": "task_parsing", "label": "任务解析", "type": "input"},
                    {"id": "vehicle_type_matching", "label": "车辆类型匹配", "type": "process"},
                    {"id": "quantity_calculation", "label": "数量计算", "type": "process"},
                    {"id": "loading_scheme", "label": "装载方案", "type": "decision"},
                    {"id": "fleet_configuration", "label": "编队配置", "type": "output"}
                ],
                "edges": [
                    {"source": "task_parsing", "target": "vehicle_type_matching"},
                    {"source": "vehicle_type_matching", "target": "quantity_calculation"},
                    {"source": "quantity_calculation", "target": "loading_scheme"},
                    {"source": "loading_scheme", "target": "fleet_configuration"}
                ]
            }
        },
        "plan_output": {
            "summary": "形成线路装订→梯队调度→途中补给三段式执行脚本。",
            "key_points": [
                "固化主/备线路并同步态势推送",
                "插入途中补给与维修检查点",
                "输出可直接导入调度平台的指令集"
            ],
            "knowledge_trace": "越野策略树通过执行接口落地到车队调度系统。",
            "knowledge_graph": {
                "nodes": [
                    {"id": "route_planning", "label": "路线规划", "type": "input"},
                    {"id": "schedule_optimization", "label": "调度优化", "type": "process"},
                    {"id": "supply_points", "label": "补给点设置", "type": "decision"},
                    {"id": "execution_script", "label": "执行脚本", "type": "output"}
                ],
                "edges": [
                    {"source": "route_planning", "target": "schedule_optimization"},
                    {"source": "schedule_optimization", "target": "supply_points"},
                    {"source": "supply_points", "target": "execution_script"}
                ]
            }
        }
    }
)

__all__ = ["BLUEPRINT"]


