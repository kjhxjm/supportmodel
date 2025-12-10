from typing import List
from .schema import Scenario

# 四、人员输送支援模型测试
SCENARIOS: List[Scenario] = [
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
                            {"id": "task",
                                "label": "任务解析(8名乘员,X区域)", "type": "input"},
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
        id="personnel_transport_strategy",  # 14. 人员输送策略
        model_name="人员输送",
        name="人员输送策略",
        example_input="从位置（85,20）向区域X（210,145）输送8名人员，运输过程中需确保行程安全、乘员舒适与到达的稳定可靠性。",
        reasoning_chain="任务解析（人数、身份类型、舒适性需求、到达时限、环境风险）→ 车辆匹配（选择具备减震系统、隔振座椅或密闭舱体的无人运输车）→ 乘员装载方案（座位分布、重心平衡、随车装备配置）→ 舒适性导向路径规划（避开颠簸路段、选择平稳路线、速度限制）→ 行程安全监控（振动监测、环境感知、乘员状态反馈）→ 异常处理（路线重规划、速度调整、临时停车检查）→ 全程信息同步与到达确认",
        prompt=(
            "【人员输送-人员输送策略专项要求】\n"
            "1. 行为树必须至少包含以下核心节点，严格按照推理链条自上而下展开：\n"
            "   - task_analysis（任务解析）：解析输送起点（85,20）到终点（210,145）的距离、人数（8名）、身份类型、舒适性需求、到达时限、环境风险；\n"
            "   - vehicle_matching（车辆匹配）：选择具备减震系统、隔振座椅或密闭舱体的无人运输车，说明选择理由；\n"
            "   - passenger_loading_plan（乘员装载方案）：规划座位分布、重心平衡与随车装备配置；\n"
            "   - comfort_routing（舒适性导向路径规划，二级节点）：必须包含以下子节点：\n"
            "       * road_analysis（路况综合解析）：分析坡度、崎岖度、障碍密度；\n"
            "       * comfort_evaluation（舒适度模型评估）：振动预测、加速度变化分析；\n"
            "       * route_selection（路径优选）：选择起伏小、加减速稳定的路线；\n"
            "       * dynamic_comfort_adjust（动态舒适性调整）：必须包含children以支持进一步展开，根据实时振动/颠簸感知进行微调；\n"
            "   - safety_monitoring（行程安全监控，二级节点）：必须包含以下子节点：\n"
            "       * passenger_status（乘员状态监控）：监控安全带状态、姿态监测、体征波动；\n"
            "       * environment_perception（环境风险感知）：感知落石、积水、滑坡风险、车辆周界异常；\n"
            "       * anomaly_response（异常识别与处理）：必须包含children以支持进一步展开，包含减速避让、停车保护、告警回传；\n"
            "       * safety_policy_update（安全策略更新）：必须包含children以支持进一步展开，基于实时风险调整行驶参数；\n"
            "   - transport_execution_plan（人员输送执行计划，核心决策节点）：必须包含以下子节点：\n"
            "       * vehicle_dispatch（车辆调度）：调度方案与编队配置；\n"
            "       * route_coordination（路径协同）：车队路径规划与协同；\n"
            "       * real_time_monitoring（全程监控与信息同步）：必须包含children以支持进一步展开，包含乘员状态监控、环境监控、信息同步；\n"
            "       必须包含 knowledge_graph 字段。\n"
            "   - arrival_confirmation（到达确认）：到达位置确认、乘员交接与任务闭环。\n"
            "2. transport_execution_plan 节点的 knowledge_graph 必须体现完整因果链路：\n"
            "   任务解析 → 车辆匹配 → 乘员装载 → 舒适性路径规划 → 行程安全监控 → 人员输送执行计划 → 到达确认。\n"
            "3. 在 node_insights 中：\n"
            "   - comfort_routing 节点必须包含 knowledge_graph，体现路况解析→舒适度评估→路径优选→动态调整的链路；\n"
            "   - safety_monitoring 节点必须包含 knowledge_graph，体现乘员监控→环境感知→异常处理→策略更新的链路；\n"
            "   - real_time_monitoring 节点必须包含 knowledge_graph，体现监控→融合→判别→处理→同步的链路；\n"
            "   - 所有节点的 knowledge_trace 体现完整推理路径。"
        ),
        example_output={
            "default_focus": "transport_execution_plan",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "任务解析：人员输送任务",
                "status": "completed",
                "summary": "解析从位置（85,20）向区域X（210,145）输送8名人员的任务，运输距离约165km，需确保行程安全与乘员舒适。",
                "children": [
                    {
                        "id": "vehicle_matching",
                        "label": "🚐 车辆匹配：3辆人员运输无人车",
                        "status": "completed",
                        "summary": "基于165km运输距离、8名乘员与舒适性要求，选择3辆配备减震系统与隔振座椅的人员运输无人车（单车载员4名，冗余设计），理由：专用座椅与悬挂系统可有效保护乘员舒适度。",
                        "children": []
                    },
                    {
                        "id": "passenger_loading_plan",
                        "label": "👥 乘员装载方案",
                        "status": "completed",
                        "summary": "规划座位分布（前车3人、中车3人、后车2人+随车装备）、重心平衡（人员与装备左右对称分布）、随车装备配置（医疗包、通信设备、应急补给）与多目的地协同调度（任务拆解、路径代价计算、停靠顺序规划、多车协同）。",
                        "children": [
                            {
                                "id": "seat_allocation",
                                "label": "座位分配",
                                "status": "completed",
                                "summary": "按人员身份与任务需求分配座位：指挥人员在前车便于协调，保障人员分散布置以降低风险。",
                                "children": []
                            },
                            {
                                "id": "balance_optimization",
                                "label": "重心平衡优化",
                                "status": "completed",
                                "summary": "人员与随车装备左右对称分布（偏差<3%），前后重量比5:5确保稳定性。",
                                "children": []
                            },
                            {
                                "id": "equipment_config",
                                "label": "随车装备配置",
                                "status": "completed",
                                "summary": "每车配备急救包、通信终端、应急食品与水（3天量）、防护用品。",
                                "children": []
                            },
                            {
                                "id": "multi_destination_coordination",
                                "label": "多目的地协同调度",
                                "status": "completed",
                                "summary": "针对多个目的地的任务场景，进行人员与目的地映射、路径代价计算、停靠顺序规划与多车协同，实现总体效率最优。",
                                "children": [
                                    {
                                        "id": "task_decomposition",
                                        "label": "任务拆解",
                                        "status": "completed",
                                        "summary": "建立人员与目的地的映射关系，明确每个目的地需要哪些人员到达，以及每个人员的目标位置。",
                                        "children": []
                                    },
                                    {
                                        "id": "path_cost_calculation",
                                        "label": "路径代价计算",
                                        "status": "completed",
                                        "summary": "综合评估各路径的距离、预计时间与实时路况（拥堵、施工等），计算各停靠点间的行驶代价。",
                                        "children": []
                                    },
                                    {
                                        "id": "stop_sequence_planning",
                                        "label": "停靠顺序规划",
                                        "status": "completed",
                                        "summary": "基于总体效率最优原则，规划车辆在多个目的地的停靠顺序，最小化总行驶时间和等待时间。",
                                        "children": []
                                    },
                                    {
                                        "id": "multi_vehicle_coordination",
                                        "label": "多车协同",
                                        "status": "completed",
                                        "summary": "协调多辆车的分工与任务分配，实现同步与交叉任务处理，提升整体调度效率。",
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": "comfort_routing",
                        "label": "🛣️ 舒适性导向路径规划",
                        "status": "completed",
                        "summary": "生成优先保障乘员舒适度的路径，避开颠簸路段，选择平稳路线并限制速度。",
                        "children": [
                            {
                                "id": "road_analysis",
                                "label": "🗺️ 路况综合解析",
                                "status": "completed",
                                "summary": "分析从（85,20）到（210,145）的候选路段坡度、崎岖度与障碍密度，识别颠簸区段。",
                                "children": []
                            },
                            {
                                "id": "comfort_evaluation",
                                "label": "📊 舒适度模型评估",
                                "status": "completed",
                                "summary": "基于振动预测和加速度变化对候选路线进行舒适度量化评估，构建舒适度评分函数。",
                                "children": []
                            },
                            {
                                "id": "route_selection",
                                "label": "✅ 路径优选",
                                "status": "completed",
                                "summary": "在满足安全和效率约束下选择起伏小、加减速平顺的路线，舒适度评分>0.85。",
                                "children": []
                            },
                            {
                                "id": "dynamic_comfort_adjust",
                                "label": "🔄 动态舒适性调整",
                                "status": "completed",
                                "summary": "根据实时振动/颠簸感知对行驶速度与局部路径进行微调。支持进一步展开查看调整策略。",
                                "children": [
                                    {
                                        "id": "vibration_monitoring",
                                        "label": "📡 实时振动监测",
                                        "status": "completed",
                                        "summary": "监测车辆纵向与垂向加速度，采样频率100Hz，识别超出舒适阈值（>1.5g）的路段。",
                                        "children": []
                                    },
                                    {
                                        "id": "speed_adjustment",
                                        "label": "🎚️ 速度自适应调整",
                                        "status": "completed",
                                        "summary": "当检测到颠簸路段时自动降速（从60km/h降至30km/h），通过平顺路段后逐步恢复。",
                                        "children": []
                                    },
                                    {
                                        "id": "micro_path_optimization",
                                        "label": "🔀 微路径优化",
                                        "status": "completed",
                                        "summary": "在车道内调整横向位置避开坑洼，或在允许范围内做小范围绕行，减少颠簸冲击。",
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": "safety_monitoring",
                        "label": "🛡️ 行程安全监控",
                        "status": "completed",
                        "summary": "实时监控乘员状态与外部环境，识别异常并执行保护措施，确保全程安全。",
                        "children": [
                            {
                                "id": "passenger_status",
                                "label": "👤 乘员状态监控",
                                "status": "completed",
                                "summary": "监控安全带系紧情况、乘员姿态（防跌倒晃动）与体征波动（心率、呼吸），识别不适征兆。",
                                "children": []
                            },
                            {
                                "id": "environment_perception",
                                "label": "🌍 环境风险感知",
                                "status": "completed",
                                "summary": "感知落石、积水、滑坡风险与车辆周界异常目标，构建环境风险地图。",
                                "children": []
                            },
                            {
                                "id": "anomaly_response",
                                "label": "⚠️ 异常识别与处理",
                                "status": "completed",
                                "summary": "对乘员或环境异常进行识别并执行应对措施。支持进一步展开查看处理流程。",
                                "children": [
                                    {
                                        "id": "risk_classification",
                                        "label": "🔍 风险分级识别",
                                        "status": "completed",
                                        "summary": "将异常分为三级：一般（黄色，轻微颠簸或偏离）、紧急（橙色，乘员不适或障碍接近）、严重（红色，生命危险或碰撞风险）。",
                                        "children": []
                                    },
                                    {
                                        "id": "emergency_braking",
                                        "label": "🛑 紧急制动避让",
                                        "status": "completed",
                                        "summary": "当检测到严重风险（碰撞预警<2秒）时立即执行紧急制动，减速度限制在4m/s²保护乘员。",
                                        "children": []
                                    },
                                    {
                                        "id": "route_replanning",
                                        "label": "🔄 路线重规划",
                                        "status": "completed",
                                        "summary": "当前方存在不可通行障碍时触发路径重规划，重规划决策时间<30秒，选择备用路线。",
                                        "children": []
                                    },
                                    {
                                        "id": "emergency_stop",
                                        "label": "🅿️ 临时停车检查",
                                        "status": "completed",
                                        "summary": "当乘员出现严重不适或车辆故障时，在安全位置停车检查，同时上报指挥端请求支援。",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "id": "safety_policy_update",
                                "label": "🔧 安全策略更新",
                                "status": "completed",
                                "summary": "基于实时风险自动调整行驶参数与告警策略。支持进一步展开查看更新机制。",
                                "children": [
                                    {
                                        "id": "speed_limit_update",
                                        "label": "🚦 速度限制动态更新",
                                        "status": "completed",
                                        "summary": "根据路况与乘员状态动态调整速度上限：正常路段60km/h，风险路段30km/h，乘员不适时15km/h。",
                                        "children": []
                                    },
                                    {
                                        "id": "safety_distance_adjustment",
                                        "label": "📏 安全距离调整",
                                        "status": "completed",
                                        "summary": "在风险路段增大车间距至200m，避免连环事故；平稳路段保持标准间距150m。",
                                        "children": []
                                    },
                                    {
                                        "id": "alert_threshold_tuning",
                                        "label": "🔔 告警阈值调优",
                                        "status": "completed",
                                        "summary": "根据历史异常记录动态调整告警阈值，降低误报率（目标<5%）同时确保关键风险不漏报。",
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": "transport_execution_plan",
                        "label": "✅ 人员输送执行计划",
                        "status": "active",
                        "summary": "制定完整输送方案：3辆人员运输车编队出发，车间距保持150m，采用舒适优先路径，实时监控乘员与环境状态，预计2.5小时完成165km运输任务。",
                        "children": [
                            {
                                "id": "vehicle_dispatch",
                                "label": "🚐 车辆调度",
                                "status": "completed",
                                "summary": "本次任务调度3辆人员运输无人车（编号PT-01/02/03），分别搭载3/3/2名乘员，配备应急装备与通信系统。",
                                "children": []
                            },
                            {
                                "id": "route_coordination",
                                "label": "🗺️ 路径协同",
                                "status": "completed",
                                "summary": "3车采用同路径编队行进，保持150m车间距，遇障碍时依序避让，通过舒适优先路线（主路线165km+备选路线180km）。",
                                "children": []
                            },
                            {
                                "id": "real_time_monitoring",
                                "label": "📊 全程监控与信息同步",
                                "status": "completed",
                                "summary": "实时监控乘员健康状态、车辆位置与环境风险，自动识别异常并同步至指挥端。支持进一步展开查看监控详情。",
                                "children": [
                                    {
                                        "id": "monitoring_requirements",
                                        "label": "📋 监控需求定义",
                                        "status": "completed",
                                        "summary": "监控项目：乘员状态（安全带、姿态、体征）、车辆状态（位置、速度、电量）、环境状态（障碍、气象、路况）。",
                                        "children": []
                                    },
                                    {
                                        "id": "sensor_fusion",
                                        "label": "📡 多源数据融合",
                                        "status": "completed",
                                        "summary": "融合车内摄像头、体征传感器、GPS、IMU、雷达与环境传感器数据，采样频率10Hz，数据融合延迟<100ms。",
                                        "children": []
                                    },
                                    {
                                        "id": "status_judgment",
                                        "label": "🔍 状态综合判别",
                                        "status": "completed",
                                        "summary": "实时检测异常状态：乘员不适（体征异常、安全带未系）、环境风险（障碍接近、恶劣天气）、车辆异常（偏航>50m、电量<20%）。",
                                        "children": []
                                    },
                                    {
                                        "id": "response_execution",
                                        "label": "🛠️ 响应措施执行",
                                        "status": "completed",
                                        "summary": "针对不同异常执行对应措施：乘员不适→减速/停车；环境风险→避让/重规划；车辆异常→导航至补给点/呼叫支援。",
                                        "children": []
                                    },
                                    {
                                        "id": "info_sync",
                                        "label": "🔄 信息实时同步",
                                        "status": "completed",
                                        "summary": "生成异常告警与任务执行日志，实时同步至指挥端（延迟<1秒），包含位置、乘员状态、异常类型与处理措施。",
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": "arrival_confirmation",
                        "label": "🎯 到达确认",
                        "status": "pending",
                        "summary": "到达区域X（210,145）后，确认位置、完成乘员交接、记录任务数据并回传指挥端，实现任务闭环。",
                        "children": [
                            {
                                "id": "location_verification",
                                "label": "📍 位置确认",
                                "status": "pending",
                                "summary": "通过GPS与视觉定位确认到达目标区域X（GPS精度<1m），验证坐标（210,145）±5m误差范围内。",
                                "children": []
                            },
                            {
                                "id": "passenger_handover",
                                "label": "👥 乘员交接",
                                "status": "pending",
                                "summary": "按乘员名单逐一确认下车人员身份与健康状态，与接收方完成电子签名交接，生成交接记录。",
                                "children": []
                            },
                            {
                                "id": "mission_closure",
                                "label": "✅ 任务闭环",
                                "status": "pending",
                                "summary": "自动生成完整任务记录（含行驶轨迹、乘员状态曲线、异常事件日志），回传指挥端并归档。",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务解析",
                    "summary": "从任务文本中提取起点（85,20）、终点（210,145）、运输距离约165km、乘员数量（8名）、舒适性与安全性要求。",
                    "key_points": [
                        "起点坐标（85,20），终点位置X坐标（210,145），直线距离约165km",
                        "乘员组成：8名人员，需识别身份类型（指挥、保障、技术等）与特殊需求",
                        "舒适性约束：运输过程需确保乘员舒适，避免剧烈颠簸与长时间疲劳",
                        "安全性约束：全程确保人员安全，监控健康状态与环境风险",
                        "时限约束：无明确时限但需兼顾效率，预估行程时间约2.5小时"
                    ],
                    "knowledge_trace": "任务文本 → 坐标/距离/人数/舒适性/安全性要素提取 → 形成任务约束条件 → 为后续车辆匹配与策略生成提供输入。"
                },
                "vehicle_matching": {
                    "title": "车辆匹配",
                    "summary": "基于165km运输距离、8名乘员与高舒适性要求，选择3辆配备减震与隔振系统的人员运输无人车。",
                    "key_points": [
                        "人员运输无人车：最高时速70km/h，续航200km，单车标准载员4名（最大6名）",
                        "舒适性配置：配备隔振座椅（减振效率>70%）、自适应悬挂系统、车内空调与降噪系统",
                        "安全配置：多点安全带、侧面气囊、防滚架、乘员状态监测系统",
                        "选择理由：专用人员运输车比越野车舒适度提升40%，减震系统可有效降低颠簸对乘员的影响",
                        "冗余设计：3车共12个座位运输8人，预留4个冗余座位，单车故障不影响全员运输"
                    ],
                    "knowledge_trace": "运输距离+乘员数量+舒适性约束 → 车辆类型筛选 → 选择人员运输无人车 → 配置舒适与安全系统 → 验证载员能力与续航。"
                },
                "passenger_loading_plan": {
                    "title": "乘员装载方案",
                    "summary": "基于3辆人员运输车的载员能力与舒适性要求，制定科学的乘员与装备分配方案。",
                    "key_points": [
                        "座位分配原则：指挥人员在前车（便于协调指挥）、保障人员分散布置（降低集中风险）",
                        "重心平衡：人员与装备左右对称分布（偏差<3%），前后重量比5:5确保行驶稳定性",
                        "装备配置：每车配备急救包（含AED、止血带）、卫星通信终端、应急食品与水（3天量）",
                        "舒适性考虑：关键岗位人员优先安排在振动较小的中部座位，避免轮上位置",
                        "协同便利：同任务小组成员安排在同一车辆或相邻车辆，便于沟通协调"
                    ],
                    "knowledge_trace": "车辆载员能力 + 乘员身份与需求 → 座位分配设计 → 重心平衡计算 → 装备配置规划 → 舒适性优化。"
                },
                "multi_destination_coordination": {
                    "title": "多目的地协同调度",
                    "summary": "针对8名人员需前往3个不同目的地的复杂调度场景，综合考虑人员与目的地映射、路径代价、停靠顺序与多车协同，实现总体效率最优的运输方案。",
                    "key_points": [
                        "任务拆解：建立人员到目的地的映射关系（A点4人、B点2人、C点2人），明确每个停靠点的需求",
                        "路径代价计算：综合评估各停靠点间的距离（A-B 15km、B-C 8km、A-C 20km）、预计时间与实时路况",
                        "停靠顺序规划：基于总行驶时间最小化原则，采用动态规划算法确定最优访问序列（如：起点→A→B→C）",
                        "多车协同：3辆车分工协作，1号车负责A+B点、2号车负责C点、3号车作为机动备份，实现并行任务处理",
                        "效率优化：通过合理路径规划使总行驶里程减少18%，总耗时缩短至1.8小时（相比顺序访问节省25分钟）"
                    ],
                    "knowledge_trace": "多目的地任务需求 + 人员分布 → 任务拆解与映射 → 路径代价计算 → 停靠顺序优化 → 多车协同分工 → 高效调度方案。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "task_demand", "label": "多目的地任务需求", "type": "input"},
                            {"id": "task_decomposition", "label": "任务拆解", "type": "process"},
                            {"id": "path_cost", "label": "路径代价计算", "type": "process"},
                            {"id": "stop_sequence", "label": "停靠顺序规划", "type": "decision"},
                            {"id": "multi_vehicle_coord", "label": "多车协同", "type": "process"},
                            {"id": "coordination_plan", "label": "协同调度方案", "type": "output"}
                        ],
                        "edges": [
                            {"source": "task_demand", "target": "task_decomposition"},
                            {"source": "task_decomposition", "target": "path_cost"},
                            {"source": "path_cost", "target": "stop_sequence"},
                            {"source": "stop_sequence", "target": "multi_vehicle_coord"},
                            {"source": "multi_vehicle_coord", "target": "coordination_plan"}
                        ]
                    }
                },
                "comfort_routing": {
                    "title": "舒适性导向路径规划",
                    "summary": "针对人员运输的高舒适性要求，设计包含路况解析、舒适度评估、路径优选与动态调整的多层次规划策略。",
                    "key_points": [
                        "路况综合解析：分析坡度、崎岖度、障碍密度，识别颠簸路段与平稳区域",
                        "舒适度模型评估：基于振动预测与加速度变化构建舒适度评分函数",
                        "路径优选：在安全前提下优先选择起伏小、加减速平顺的路线，舒适度评分>0.85",
                        "动态舒适性调整：实时监测振动，当超出阈值（>1.5g）时自动降速或微调路径"
                    ],
                    "knowledge_trace": "舒适性需求 + 路网数据 → 路况特征分析 → 舒适度量化评估 → 路径多目标优化 → 实时动态调整。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "road_input", "label": "路网与路况数据", "type": "input"},
                            {"id": "road_analysis", "label": "路况综合解析", "type": "process"},
                            {"id": "comfort_eval", "label": "舒适度模型评估", "type": "process"},
                            {"id": "route_sel", "label": "路径优选", "type": "decision"},
                            {"id": "realtime_data", "label": "实时振动/姿态感知", "type": "input"},
                            {"id": "dynamic_adj", "label": "动态舒适性调整", "type": "process"},
                            {"id": "comfort_path", "label": "舒适路径输出", "type": "output"}
                        ],
                        "edges": [
                            {"source": "road_input", "target": "road_analysis"},
                            {"source": "road_analysis", "target": "comfort_eval"},
                            {"source": "comfort_eval", "target": "route_sel"},
                            {"source": "route_sel", "target": "comfort_path"},
                            {"source": "realtime_data", "target": "dynamic_adj"},
                            {"source": "route_sel", "target": "dynamic_adj"},
                            {"source": "dynamic_adj", "target": "comfort_path"}
                        ]
                    }
                },
                "road_analysis": {
                    "title": "路况综合解析",
                    "summary": "结合高精地图与在线感知信息，识别从（85,20）到（210,145）路径中的颠簸路段。",
                    "key_points": [
                        "坡度分析：识别纵坡>10°与横坡>8°的路段，标注为颠簸风险区",
                        "崎岖度检测：基于路面点云与历史振动数据计算路面粗糙度指数（IRI）",
                        "障碍密度统计：统计单位里程内坑洼、减速带、碎石路段数量",
                        "地形分类：将候选路段分为高舒适（平整沥青路）、中舒适（水泥路）、低舒适（碎石土路）"
                    ],
                    "knowledge_trace": "高精地图 + 传感器数据 → 路面特征提取 → 舒适度标签分类 → 为路径评估提供输入。"
                },
                "comfort_evaluation": {
                    "title": "舒适度模型评估",
                    "summary": "根据车辆动力学模型与乘员敏感度，对候选路线的舒适度进行量化预测。",
                    "key_points": [
                        "振动预测：基于悬挂系统参数与路面特征预测垂向加速度（ISO 2631标准）",
                        "加速度分析：计算纵向与横向加速度变化率，识别急加速、急转弯路段",
                        "乘员敏感度建模：人体对4-8Hz振动最敏感，构建加权舒适度评分函数",
                        "综合评分：每条候选路径计算舒适度指数（0-1），>0.85为高舒适路线"
                    ],
                    "knowledge_trace": "路段特征 + 车辆模型 + 乘员敏感度 → 振动与加速度预测 → 舒适度量化评分。"
                },
                "route_selection": {
                    "title": "路径优选",
                    "summary": "在安全、时间与舒适度三者之间做权衡，选择综合最优路线。",
                    "key_points": [
                        "安全过滤：排除塌方、滑坡等高风险路段，安全系数<0.7的路线不予考虑",
                        "多目标优化：以舒适度为主目标（权重0.6）、时间为次目标（权重0.3）、距离为辅助（权重0.1）",
                        "路径生成：主路线165km（舒适度0.88，预计2.5小时）+备选路线180km（舒适度0.92，预计2.8小时）",
                        "偏好调整：可根据任务紧急程度调整「舒适度优先」或「效率优先」权重"
                    ],
                    "knowledge_trace": "候选路径 + 舒适度评分 + 安全性 → 多目标加权优化 → 选定主路径与备选路径。"
                },
                "dynamic_comfort_adjust": {
                    "title": "动态舒适性调整",
                    "summary": "运行过程中利用实时振动/姿态数据对速度和局部路线进行在线微调，确保全程舒适。",
                    "key_points": [
                        "实时振动监测：车载IMU采样频率100Hz，实时计算三轴加速度有效值",
                        "速度自适应：当垂向加速度>1.5g时自动降速（60→30km/h），平稳路段逐步恢复",
                        "微路径优化：在车道宽度允许范围内调整横向位置避开坑洼，或小范围绕行",
                        "数据记录：记录颠簸热点区域（GPS坐标+振动强度），更新路况数据库供后续任务使用"
                    ],
                    "knowledge_trace": "实时传感数据 → 与舒适度阈值对比 → 触发速度/路径微调 → 控制指令执行 → 数据记录与模型更新。"
                },
                "vibration_monitoring": {
                    "title": "实时振动监测",
                    "summary": "通过车载IMU实时监测车辆振动状况，为速度与路径调整提供数据支持。",
                    "key_points": [
                        "传感器配置：6轴IMU（3轴加速度+3轴陀螺仪），采样频率100Hz，精度0.01g",
                        "监测维度：纵向加速度（前后）、横向加速度（左右）、垂向加速度（上下）",
                        "阈值设定：舒适阈值1.5g（ISO 2631标准），警告阈值2.5g，危险阈值3.5g",
                        "滤波处理：采用低通滤波（截止频率20Hz）消除高频噪声，保留真实振动信号"
                    ],
                    "knowledge_trace": "IMU数据采集 → 滤波与特征提取 → 与舒适阈值对比 → 触发调整决策。"
                },
                "speed_adjustment": {
                    "title": "速度自适应调整",
                    "summary": "根据实时振动强度动态调整行驶速度，保护乘员舒适度。",
                    "key_points": [
                        "降速策略：检测到颠簸路段（振动>1.5g）时线性降速，每0.5g超出降低10km/h",
                        "恢复策略：进入平稳路段后，每5秒评估一次，振动<1.0g持续10秒后以5km/h/s的加速度恢复",
                        "速度范围：最高60km/h（平稳路段），最低15km/h（极端颠簸），停车保护阈值>3.5g",
                        "预瞄控制：结合前视摄像头识别前方100m路况，提前预判并平滑调速"
                    ],
                    "knowledge_trace": "振动强度检测 → 降速/恢复决策 → 速度指令生成 → 平滑执行控制。"
                },
                "micro_path_optimization": {
                    "title": "微路径优化",
                    "summary": "在车道内或允许范围内对行驶轨迹进行微小调整，避开局部颠簸点。",
                    "key_points": [
                        "横向避让：在车道宽度（3.5m）内调整横向位置±0.5m，避开坑洼与碎石",
                        "小范围绕行：在视距良好且无对向车辆时，可越线绕行障碍（绕行距离<10m）",
                        "安全约束：绕行前检查对向与侧方安全距离（>20m），确保无碰撞风险",
                        "轨迹平滑：采用三次样条插值生成平滑轨迹，避免急打方向盘引起横向加速度过大"
                    ],
                    "knowledge_trace": "前方障碍识别 → 可绕行空间评估 → 安全性检查 → 轨迹规划与执行。"
                },
                "task_decomposition": {
                    "title": "任务拆解",
                    "summary": "将多目的地运输任务细化为人员与目的地的映射关系，明确每个停靠点的需求与约束。",
                    "key_points": [
                        "人员映射：建立8名人员到3个目的地的分配关系（A点：指挥组4人，B点：保障组2人，C点：技术组2人）",
                        "需求分析：识别各目的地的人员需求、到达时间要求与特殊装备需求",
                        "约束识别：考虑车辆载员能力（每车3人）、人员协作要求（同组人员优先同车）与目的地距离分布",
                        "任务分组：将8人按目的地分为3个子任务组，为后续路径规划提供清晰输入"
                    ],
                    "knowledge_trace": "多目的地任务 + 人员信息 → 人员与目的地映射 → 需求与约束提取 → 任务分组输出。"
                },
                "path_cost_calculation": {
                    "title": "路径代价计算",
                    "summary": "综合评估各停靠点之间的距离、预计时间与实时路况，为停靠顺序规划提供定量依据。",
                    "key_points": [
                        "距离矩阵：计算起点与各目的地间的实际路网距离（起点-A 25km，起点-B 32km，起点-C 28km，A-B 15km，B-C 8km，A-C 20km）",
                        "时间估算：基于道路等级、限速与历史数据预测行驶时间（高速路段60km/h，城区30km/h）",
                        "路况权重：引入实时路况系数（畅通1.0，缓行1.3，拥堵1.8），动态调整路径代价",
                        "综合代价：构建时间-距离加权代价函数（时间权重0.7，距离权重0.3），生成代价矩阵"
                    ],
                    "knowledge_trace": "路网数据 + 实时路况 → 距离与时间计算 → 代价函数加权 → 代价矩阵输出。"
                },
                "stop_sequence_planning": {
                    "title": "停靠顺序规划",
                    "summary": "基于路径代价矩阵，采用优化算法确定访问各目的地的最优顺序，最小化总行驶时间和里程。",
                    "key_points": [
                        "问题建模：转化为旅行商问题（TSP）变体，目标函数为总代价最小化",
                        "算法选择：采用动态规划算法（目的地≤5时）或遗传算法（目的地>5时）求解最优顺序",
                        "约束处理：考虑时间窗口约束（A点需10:00前到达）、优先级约束（指挥组优先）与车辆返回需求",
                        "顺序输出：生成最优访问序列（起点→A→B→C，总里程68km，预计耗时1.8小时），相比随机顺序节省25分钟"
                    ],
                    "knowledge_trace": "代价矩阵 + 约束条件 → TSP建模 → 优化算法求解 → 最优停靠序列 → 效率评估。"
                },
                "multi_vehicle_coordination": {
                    "title": "多车协同",
                    "summary": "协调3辆运输车的任务分工与执行同步，通过并行处理与动态调度提升整体效率。",
                    "key_points": [
                        "任务分配：1号车负责A+B点（6人），2号车负责C点（2人），3号车作为机动备份并运输额外装备",
                        "并行策略：1号车执行主线路（起点→A→B），2号车执行支线（起点→C），两车并行出发节省等待时间",
                        "同步机制：关键时间点（如A点集结）设置同步等待，车辆间通过卫星通信实时共享位置与进度",
                        "动态调整：当1号车延误时，3号车可接管部分任务（如直接前往B点），确保整体计划不受影响",
                        "效率提升：通过多车并行使总耗时从2.3小时缩短至1.8小时，车辆利用率从67%提升至85%"
                    ],
                    "knowledge_trace": "任务分组 + 车辆资源 → 任务分配与路径规划 → 并行执行与同步控制 → 异常响应与动态调整 → 协同执行方案。"
                },
                "safety_monitoring": {
                    "title": "行程安全监控",
                    "summary": "针对人员运输的高安全性要求，设计包含乘员监控、环境感知、异常处理与策略更新的全方位安全保障体系。",
                    "key_points": [
                        "乘员状态监控：实时监控安全带、姿态与体征，识别不适与风险征兆",
                        "环境风险感知：感知落石、积水、滑坡等外部危险，构建环境风险地图",
                        "异常识别与处理：对乘员/环境异常进行分级，执行减速、避让、停车等措施",
                        "安全策略更新：根据实时风险动态调整速度限制、安全距离与告警阈值"
                    ],
                    "knowledge_trace": "安全需求 + 监控数据 → 乘员与环境状态评估 → 异常识别与分级 → 处理措施执行 → 策略参数更新。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "pax_mon", "label": "乘员状态监控", "type": "input"},
                            {"id": "env_per", "label": "环境风险感知", "type": "input"},
                            {"id": "anom_res", "label": "异常识别与处理", "type": "process"},
                            {"id": "policy_upd", "label": "安全策略更新", "type": "decision"},
                            {"id": "safe_exec", "label": "安全执行控制", "type": "output"}
                        ],
                        "edges": [
                            {"source": "pax_mon", "target": "anom_res"},
                            {"source": "env_per", "target": "anom_res"},
                            {"source": "anom_res", "target": "policy_upd"},
                            {"source": "policy_upd", "target": "safe_exec"},
                            {"source": "safe_exec", "target": "pax_mon"},
                            {"source": "safe_exec", "target": "env_per"}
                        ]
                    }
                },
                "passenger_status": {
                    "title": "乘员状态监控",
                    "summary": "通过车内摄像头与体征传感器全面监控乘员安全与健康状况。",
                    "key_points": [
                        "安全带检测：每个座位配备压力传感器与视觉检测，实时确认安全带系紧状态",
                        "姿态监测：车内摄像头（帧率30fps）检测乘员姿态，识别异常晃动、跌倒或头部撞击",
                        "体征监测：座椅集成心率与呼吸传感器（非接触式），检测应激反应或健康异常",
                        "不适识别：通过面部表情识别（准确率>90%）检测恶心、疼痛等不适征兆",
                        "告警机制：异常状态持续>5秒触发告警，严重异常（心率>120或<50）立即告警"
                    ],
                    "knowledge_trace": "多源传感数据采集 → 安全与舒适指标计算 → 异常模式识别 → 输出乘员风险等级。"
                },
                "environment_perception": {
                    "title": "环境风险感知",
                    "summary": "利用多传感器融合技术识别道路与周边环境中的潜在危险。",
                    "key_points": [
                        "障碍检测：激光雷达（检测距离150m）+摄像头融合，识别落石、倾倒树木、积水区域",
                        "地形识别：识别悬崖、陡坡（>30°）、塌方等高危地形，距离车辆<50m时触发警告",
                        "气象感知：雨量传感器+能见度检测，大雨（>50mm/h）或低能见度（<100m）时降速",
                        "周界监测：360°环视雷达监测车辆周围20m范围，识别突然闯入的行人、动物或车辆",
                        "风险地图：将感知结果叠加至地图，构建动态环境风险地图，更新频率1Hz"
                    ],
                    "knowledge_trace": "多传感器数据采集 → 危险目标与地形识别 → 风险等级评估 → 环境风险地图生成。"
                },
                "anomaly_response": {
                    "title": "异常识别与处理",
                    "summary": "对乘员和环境的综合异常进行识别与分级，并触发相应的应对策略，确保人员安全。",
                    "key_points": [
                        "风险分级：一般（黄色）-轻微颠簸或偏离；紧急（橙色）-乘员不适或障碍接近；严重（红色）-生命危险或碰撞风险",
                        "紧急制动：碰撞预警<2秒时立即制动，减速度限制4m/s²（防止乘员受伤）",
                        "路线重规划：不可通行障碍触发重规划，决策时间<30秒，切换至备选路线",
                        "临时停车：乘员严重不适或车辆故障时，在安全位置（路肩/停车区）停车并上报",
                        "多车协同：某车异常时通知其他车辆调整速度/间距，避免连环影响"
                    ],
                    "knowledge_trace": "乘员风险 + 环境风险 → 异常级别评估 → 处置策略选择 → 执行控制指令 → 结果反馈与记录。"
                },
                "risk_classification": {
                    "title": "风险分级识别",
                    "summary": "将检测到的异常按严重程度分为三级，采取不同响应策略。",
                    "key_points": [
                        "一般风险（黄色）：轻微颠簸（1.5g<振动<2.0g）、路线偏离<30m、单个乘员轻微不适",
                        "紧急风险（橙色）：中度颠簸（2.0g<振动<3.0g）、障碍距离<30m、多名乘员不适",
                        "严重风险（红色）：剧烈颠簸（振动>3.0g）、碰撞预警<2秒、乘员生命体征异常（心率<50或>150）",
                        "响应策略：一般→减速监控；紧急→避让或停车检查；严重→立即制动并呼叫救援"
                    ],
                    "knowledge_trace": "异常特征提取 → 严重程度量化 → 风险等级分类 → 匹配响应策略。"
                },
                "emergency_braking": {
                    "title": "紧急制动避让",
                    "summary": "当检测到严重碰撞风险时立即执行紧急制动，最大限度保护乘员安全。",
                    "key_points": [
                        "触发条件：TTC（碰撞时间）<2秒、障碍物无法绕行、前车急刹（减速度>6m/s²）",
                        "制动策略：全力制动但限制减速度≤4m/s²（保护乘员），ABS防抱死系统启动",
                        "乘员保护：制动前0.5秒预紧安全带、调整座椅姿态（后仰5°减少前冲）",
                        "后车通知：通过V2V通信广播紧急制动信号，后车同步减速避免追尾",
                        "制动后处理：停车后检查乘员状态、车辆损伤，确认安全后重新起步或呼叫支援"
                    ],
                    "knowledge_trace": "碰撞风险检测 → 紧急制动决策 → 预保护措施 → 制动执行 → 后续处理。"
                },
                "route_replanning": {
                    "title": "路线重规划",
                    "summary": "当前方存在不可通行障碍时触发路径重规划，快速切换至备选路线。",
                    "key_points": [
                        "触发条件：道路塌方、桥梁损毁、积水过深（>50cm）、交通管制等不可通行情况",
                        "重规划算法：基于A*的增量式搜索，复用已行驶路段，仅重算前方路径",
                        "备选路线：主路线165km+备选路线A（180km，绕行山区）+备选路线B（195km，平原路线）",
                        "决策时间：<30秒完成重规划，新路径同步至车队所有车辆",
                        "舒适度保证：重规划后的路径仍需满足舒适度>0.80的约束"
                    ],
                    "knowledge_trace": "障碍识别 → 可通行性评估 → 触发重规划 → 备选路径评估 → 最优路径选择 → 车队同步。"
                },
                "emergency_stop": {
                    "title": "临时停车检查",
                    "summary": "当乘员出现严重不适或车辆故障时，在安全位置停车进行检查与处理。",
                    "key_points": [
                        "停车触发：乘员严重不适（持续呕吐、胸痛、昏迷）、车辆故障（动力丧失、轮胎爆裂）",
                        "安全选址：寻找路肩宽度>2m、视距>100m、无落石风险的位置停车",
                        "应急处理：开启双闪灯、放置警告标志（车后50m）、检查乘员/车辆状态",
                        "支援呼叫：通过卫星通信上报指挥端，说明位置、人员状况、所需支援类型",
                        "继续判断：问题解决后可继续行驶，否则等待救援并将其他乘员转移至正常车辆"
                    ],
                    "knowledge_trace": "异常严重性评估 → 停车决策 → 安全位置选择 → 应急处理 → 支援呼叫 → 后续方案确定。"
                },
                "safety_policy_update": {
                    "title": "安全策略更新",
                    "summary": "根据实时监测结果动态调整行驶参数与安全策略，实现闭环优化，持续降低风险。",
                    "key_points": [
                        "速度限制更新：根据路况与乘员状态动态调整速度上限（正常60/风险30/不适15km/h）",
                        "安全距离调整：风险路段增大车间距至200m，平稳路段保持150m",
                        "告警阈值调优：根据历史数据降低误报率（目标<5%）同时确保关键风险不漏报",
                        "策略学习：记录异常事件与处理效果，基于强化学习优化未来决策参数"
                    ],
                    "knowledge_trace": "异常处理结果 → 策略效果评估 → 参数调整决策 → 更新速度/距离/阈值 → 持续优化。"
                },
                "speed_limit_update": {
                    "title": "速度限制动态更新",
                    "summary": "根据路况与乘员状态实时调整车辆速度上限，兼顾安全与舒适。",
                    "key_points": [
                        "正常模式：路况良好+乘员状态正常，速度上限60km/h",
                        "风险模式：路况复杂（崎岖、窄路、能见度低），速度上限30km/h",
                        "保护模式：乘员不适或车辆异常，速度上限15km/h",
                        "自适应调整：根据实时振动、环境风险评分动态插值计算速度上限",
                        "平滑过渡：模式切换时加减速度限制≤2m/s²，避免突变引起不适"
                    ],
                    "knowledge_trace": "路况评分 + 乘员状态 → 模式选择 → 速度上限计算 → 平滑过渡控制。"
                },
                "safety_distance_adjustment": {
                    "title": "安全距离调整",
                    "summary": "根据路况与车辆状态动态调整车间距，降低追尾与连环事故风险。",
                    "key_points": [
                        "标准间距：平稳路段保持150m（约9秒行进时间差，车速60km/h）",
                        "加大间距：风险路段增至200m（能见度低、路面湿滑、坡度大）",
                        "缩短间距：紧急情况允许缩至100m（保持车队紧凑，便于协同）",
                        "动态调整：基于前车速度、路面附着系数、制动距离模型实时计算最优间距",
                        "通信保障：间距内保持V2V通信稳定（延迟<50ms），确保协同控制有效"
                    ],
                    "knowledge_trace": "前车状态 + 路况 + 制动模型 → 最优间距计算 → 跟车控制执行。"
                },
                "alert_threshold_tuning": {
                    "title": "告警阈值调优",
                    "summary": "根据历史异常记录与误报分析，动态调整告警阈值，平衡灵敏度与误报率。",
                    "key_points": [
                        "误报分析：统计过去100次告警中误报次数，计算误报率（目标<5%）",
                        "漏报分析：统计未被告警但事后确认为异常的事件，计算漏报率（目标<2%）",
                        "阈值调整策略：误报率高→提高阈值（如振动告警从1.5g→1.8g）；漏报率高→降低阈值",
                        "多维度优化：不同类型异常（振动、体征、环境）独立调优阈值",
                        "人工干预：允许操作员根据任务特点手动调整告警灵敏度（保守/标准/宽松）"
                    ],
                    "knowledge_trace": "历史告警数据 → 误报/漏报率统计 → 阈值优化方向 → 新阈值计算 → 部署与验证。"
                },
                "transport_execution_plan": {
                    "title": "人员输送执行计划",
                    "summary": "整合车辆配置、乘员装载、舒适路径、安全监控与异常处理措施，生成完整的人员输送执行方案。",
                    "key_points": [
                        "车辆编队：3辆人员运输无人车（PT-01/02/03），分别搭载3/3/2名乘员",
                        "路径方案：采用舒适优先路径（主路线165km，舒适度0.88，预计2.5小时）",
                        "车队协同：车间距150m，编队行进，前车探路/中车主运/后车保障",
                        "全程监控：实时监控乘员健康、车辆状态与环境风险，异常自动告警",
                        "应急预案：路线重规划、临时停车、紧急制动、呼叫支援等多层次保障"
                    ],
                    "knowledge_trace": "车辆配置 + 乘员装载 + 舒适路径 + 安全监控 + 异常处理 → 编队与间隔设计 → 协同与监控方案 → 时间规划验证 → 形成可执行输送方案。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "task_parse", "label": "任务解析", "type": "input"},
                            {"id": "vehicle_match", "label": "车辆匹配", "type": "process"},
                            {"id": "loading", "label": "乘员装载方案", "type": "process"},
                            {"id": "comfort_path", "label": "舒适性路径规划", "type": "process"},
                            {"id": "safety_mon", "label": "行程安全监控", "type": "process"},
                            {"id": "execution", "label": "人员输送执行计划", "type": "decision"},
                            {"id": "arrival", "label": "到达确认", "type": "output"}
                        ],
                        "edges": [
                            {"source": "task_parse", "target": "vehicle_match"},
                            {"source": "vehicle_match", "target": "loading"},
                            {"source": "loading", "target": "comfort_path"},
                            {"source": "comfort_path", "target": "safety_mon"},
                            {"source": "safety_mon", "target": "execution"},
                            {"source": "execution", "target": "arrival"},
                            {"source": "task_parse", "target": "execution"}
                        ]
                    }
                },
                "vehicle_dispatch": {
                    "title": "车辆调度",
                    "summary": "根据任务需求调度合适数量与类型的车辆，并进行编号与装备配置。",
                    "key_points": [
                        "调度方案：3辆人员运输无人车（编号PT-01/PT-02/PT-03）",
                        "乘员分配：PT-01搭载3人（含1名指挥）、PT-02搭载3人（保障人员）、PT-03搭载2人+应急装备",
                        "装备配置：每车配备卫星通信终端、急救包、灭火器、应急食品与水",
                        "出发准备：车辆检查（电量>90%、传感器正常、安全带完好）、乘员登车、装备清点",
                        "编队顺序：PT-01领航（探路）→ PT-02主力（中间）→ PT-03殿后（保障）"
                    ],
                    "knowledge_trace": "任务需求 → 车辆数量与类型确定 → 乘员与装备分配 → 编队顺序规划 → 出发前检查。"
                },
                "route_coordination": {
                    "title": "路径协同",
                    "summary": "制定车队路径规划与协同策略，确保多车安全高效协同行进。",
                    "key_points": [
                        "路径方案：3车采用同路径编队行进，主路线165km+备选路线180km",
                        "车间距管理：标准间距150m，风险路段200m，紧急情况100m",
                        "协同策略：前车探路并标记障碍、中车主运、后车准备应急支援",
                        "避让协同：遇障碍时依序避让（前车先行、后车跟随），窄路段切换为单列纵队",
                        "通信保障：V2V实时通信（延迟<50ms），车队状态与路况信息共享"
                    ],
                    "knowledge_trace": "路径方案 + 车辆数量 → 编队模式设计 → 车间距规则 → 协同策略 → 通信机制保障。"
                },
                "real_time_monitoring": {
                    "title": "全程监控与信息同步",
                    "summary": "实时监控车队运行情况与乘员状态，自动识别异常并同步至指挥端，确保全程可控。",
                    "key_points": [
                        "监控维度：乘员（安全带/姿态/体征）、车辆（位置/速度/电量/健康）、环境（障碍/气象/路况）",
                        "数据采集：多传感器融合，采样频率10Hz，数据融合延迟<100ms",
                        "异常检测：基于阈值与机器学习的双重检测机制，异常识别准确率>95%",
                        "告警机制：分级告警（一般/紧急/严重），实时推送指挥端（延迟<1秒）",
                        "应对执行：针对不同异常类型预设处理方案，自动执行或人工确认后执行"
                    ],
                    "knowledge_trace": "传感器数据采集 → 多源数据融合 → 状态综合判别 → 异常检测与分级 → 处理措施执行 → 信息同步指挥端。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "mon_req", "label": "监控需求定义", "type": "input"},
                            {"id": "sens_fusion", "label": "多源数据融合", "type": "process"},
                            {"id": "status_judge", "label": "状态综合判别", "type": "process"},
                            {"id": "response_exec", "label": "响应措施执行", "type": "decision"},
                            {"id": "info_sync", "label": "信息实时同步", "type": "output"}
                        ],
                        "edges": [
                            {"source": "mon_req", "target": "sens_fusion"},
                            {"source": "sens_fusion", "target": "status_judge"},
                            {"source": "status_judge", "target": "response_exec"},
                            {"source": "response_exec", "target": "info_sync"},
                            {"source": "status_judge", "target": "info_sync"}
                        ]
                    }
                },
                "monitoring_requirements": {
                    "title": "监控需求定义",
                    "summary": "明确人员输送全程监控的具体项目、指标与阈值。",
                    "key_points": [
                        "乘员监控：安全带状态（系紧/松弛）、姿态（正常/异常晃动）、体征（心率60-100、呼吸12-20次/分）",
                        "车辆监控：实时位置（GPS精度<1m）、行驶速度、剩余电量、系统健康状态",
                        "环境监控：前方障碍（检测距离150m）、侧方风险（周界20m）、气象条件（雨量/能见度）",
                        "采样频率：位置与速度10Hz、乘员体征1Hz、环境感知20Hz",
                        "存储策略：全量数据实时传输+本地存储（保留7天），关键事件永久归档"
                    ],
                    "knowledge_trace": "任务安全需求 → 监控项目确定 → 指标阈值设定 → 采样与存储策略 → 监控方案形成。"
                },
                "sensor_fusion": {
                    "title": "多源数据融合",
                    "summary": "融合多种传感器数据，构建车队与乘员状态的完整画像。",
                    "key_points": [
                        "传感器类型：车内摄像头、体征传感器、GPS、IMU、激光雷达、毫米波雷达、气象传感器",
                        "采样频率：视觉30fps、体征1Hz、位置10Hz、振动100Hz、雷达20Hz",
                        "融合算法：扩展卡尔曼滤波（EKF）融合多源数据，消除传感器噪声与延迟",
                        "时间同步：统一时间戳（精度<10ms），确保多源数据时空对齐",
                        "输出格式：统一的车队状态向量（位置/速度/姿态/乘员/环境），每100ms更新一次"
                    ],
                    "knowledge_trace": "多传感器数据采集 → 时间同步与对齐 → 卡尔曼滤波融合 → 状态向量输出。"
                },
                "status_judgment": {
                    "title": "状态综合判别",
                    "summary": "基于融合数据实时判别车队、乘员与环境的运行状态，识别异常征兆。",
                    "key_points": [
                        "乘员状态：正常（体征正常+安全带系好）、警告（轻微不适）、异常（严重不适或安全带未系）",
                        "车辆状态：正常（>50%电量+路线偏离<10m）、注意（20-50%电量）、异常（<20%电量或偏离>50m）",
                        "环境状态：安全（无障碍+能见度良好）、警戒（障碍30-100m）、危险（障碍<30m或能见度<50m）",
                        "综合评估：基于乘员、车辆、环境三维度状态计算综合风险评分（0-100），>70触发告警"
                    ],
                    "knowledge_trace": "融合数据输入 → 各维度阈值判断 → 状态分类 → 综合风险评分 → 异常识别。"
                },
                "response_execution": {
                    "title": "响应措施执行",
                    "summary": "针对不同异常类型执行预设的应对策略，确保及时有效处理。",
                    "key_points": [
                        "乘员不适：轻微→减速并增强空调；严重→最近安全地点停车并呼叫医疗支援",
                        "环境风险：障碍接近→减速避让或绕行；不可通行→触发路径重规划",
                        "车辆异常：电量不足→导航至充电站；故障→停车检查或呼叫救援",
                        "执行模式：自动执行（一般异常）、人工确认（紧急异常）、立即执行（严重异常）",
                        "效果评估：执行后持续监控，确认异常解除或升级处理措施"
                    ],
                    "knowledge_trace": "异常类型识别 → 策略库匹配 → 执行方案生成 → 控制指令下发 → 效果评估反馈。"
                },
                "info_sync": {
                    "title": "信息实时同步",
                    "summary": "将车队状态、异常事件与处理措施实时同步至指挥端，实现远程监控与干预。",
                    "key_points": [
                        "同步内容：车辆位置、速度、电量、乘员状态、环境风险、异常事件、处理措施",
                        "同步频率：正常状态1Hz、异常状态10Hz、严重异常实时推送",
                        "通信方式：4G/5G主通道+卫星通信备份，确保全程连接",
                        "告警推送：分级告警实时推送至指挥端（延迟<1秒），支持短信/语音/可视化多种形式",
                        "远程干预：指挥端可下发指令（路径调整、停车检查、呼叫支援），车辆执行并反馈结果"
                    ],
                    "knowledge_trace": "状态与事件数据 → 数据打包与压缩 → 通信信道传输 → 指挥端接收与展示 → 远程指令下发。"
                },
                "arrival_confirmation": {
                    "title": "到达确认",
                    "summary": "到达区域X（210,145）后，完成位置确认、乘员交接与任务闭环，确保任务圆满完成。",
                    "key_points": [
                        "位置确认：通过GPS+视觉定位双重验证到达目标位置（误差<5m）",
                        "乘员交接：按名单逐一确认下车人员身份与健康状态，与接收方完成电子签名",
                        "任务闭环：生成完整任务记录（行驶轨迹、乘员状态曲线、异常事件日志），回传指挥端并归档",
                        "车辆复位：检查车辆状态（电量、损伤、清洁），补能后返回或执行下一任务"
                    ],
                    "knowledge_trace": "到达目的地 → 位置确认 → 乘员交接 → 任务记录生成 → 数据回传与归档 → 车辆复位。"
                },
                "location_verification": {
                    "title": "位置确认",
                    "summary": "通过多种定位手段精确确认车辆已到达目标区域。",
                    "key_points": [
                        "GPS定位：实时GPS坐标（210,145），水平精度<1m",
                        "视觉定位：摄像头识别地标建筑物或特征物，与高精地图匹配验证",
                        "双重验证：GPS+视觉定位结果一致性检查，误差<5m则确认到达",
                        "失败处理：若定位不一致或误差>5m，则在周边搜索或请求指挥端人工确认",
                        "记录存档：到达时间、坐标、定位精度记录至任务日志"
                    ],
                    "knowledge_trace": "GPS数据获取 → 视觉特征匹配 → 双重验证一致性检查 → 到达确认 → 记录存档。"
                },
                "passenger_handover": {
                    "title": "乘员交接",
                    "summary": "与接收方完成正式的人员交接手续，确保责任清晰。",
                    "key_points": [
                        "身份确认：按乘员名单逐一核对身份（人脸识别或证件）",
                        "健康检查：记录乘员下车时健康状态（体征正常、无不适主诉、行动自如）",
                        "电子签收：接收方通过移动终端确认收到人员并电子签名，系统自动记录时间戳",
                        "异常上报：若乘员在运输中出现健康异常，详细记录并告知接收方",
                        "文档生成：自动生成交接单（乘员名单、状态、时间、签收人），双方各留存一份"
                    ],
                    "knowledge_trace": "乘员名单核对 → 健康状态检查 → 电子签收 → 异常记录 → 文档生成与留存。"
                },
                "mission_closure": {
                    "title": "任务闭环",
                    "summary": "生成完整任务记录并回传指挥端，实现任务全流程可追溯。",
                    "key_points": [
                        "轨迹记录：完整行驶轨迹（GPS坐标序列，精度<1m，采样频率1Hz）",
                        "状态曲线：乘员体征曲线（心率、呼吸）、车辆状态曲线（速度、电量、振动）",
                        "事件日志：异常事件（类型、时间、位置、处理措施、效果）完整记录",
                        "统计分析：总行驶距离、平均速度、能耗、舒适度评分、异常次数等关键指标",
                        "数据回传：通过4G/5G或卫星通信回传指挥端，并在本地归档保留30天"
                    ],
                    "knowledge_trace": "任务数据汇总 → 轨迹/状态/事件结构化 → 统计分析 → 数据打包 → 回传与归档。"
                }
            }
        },
    ),
    Scenario(
        id="personnel_comfort_routing",  # 15. 舒适性导向路径规划（子场景，用于测试单一功能点）
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
        id="personnel_safety_monitor",  # 16. 人员与环境安全监控（子场景，用于测试单一功能点）
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
        id="personnel_multi_destination_dispatch",  # 17. 多目的地协同调度（子场景，用于测试单一功能点）
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
                            {"id": "local_policy", "label": "各车本地调度策略 π_i",
                                "type": "process"},
                            {"id": "local_experience",
                                "label": "本地执行轨迹与经验池 D_i", "type": "process"},
                            {"id": "consensus", "label": "分布式一致性信息聚合",
                                "type": "process"},
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
    )   
]