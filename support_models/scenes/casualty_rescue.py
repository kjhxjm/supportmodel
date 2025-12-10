from typing import List
from .schema import Scenario

# 三、伤员救助支援模型测试
SCENARIOS: List[Scenario] = [
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
                            {"id": "task",
                                "label": "任务解析(两名伤员,X区域)", "type": "input"},
                            {"id": "equip",
                                "label": "设备匹配(无人机/担架车/机器人)", "type": "process"},
                            {"id": "qty",
                                "label": "数量计算(载荷+冗余)", "type": "process"},
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
        id="casualty_rescue_strategy",  # 伤员救助策略（完整综合场景）
        model_name="伤员救助",
        name="伤员救助策略",
        example_input="在区域X（210,145）发现2名伤员，需从位置（85,20）调派无人救援设备前往实施救助，并将伤员运回安全点（60,10），要求全程确保救援过程安全可靠。",
        reasoning_chain="伤员定位（接收消息、无人机搜索、确定可疑区域、机械狗二次确认）→ 任务解析（受伤人数、环境风险、可达性、急迫程度）→ 伤情评估与分类（是否具备意识+能否行动）→ 救援方式匹配（无人车担架）→ 路径与救援流程优化（选择最安全可达路线、分批救援或集中救援）→ 协同策略（指挥端同步、医疗点准备、途中状态监测）→ 救助完成伤情数据同步（伤情同步、任务闭环）",
        prompt=(
            "【伤员救助-伤员救助策略专项要求】\n"
            "1. 行为树必须至少包含以下核心节点，严格按照推理链条自上而下展开：\n"
            "   - casualty_localization（伤员定位，核心节点）：必须包含以下子节点：\n"
            "       * message_reception（接收消息）：接收伤员求救信号或任务指令；\n"
            "       * uav_search（无人机搜索）：远距热成像扫描与生命信号捕获，包含航迹规划、热成像扫描、信号捕获子节点；\n"
            "       * suspect_area_determination（确定可疑区域）：区域热斑检测、可疑目标标注、搜索网格生成；\n"
            "       * robot_dog_confirmation（机械狗二次确认）：近距多模态精定位，包含可穿戴信号、UWB定位、视觉/热成像确认；\n"
            "       必须包含 knowledge_graph 字段。\n"
            "   - task_analysis（任务解析）：解析受伤人数（2名）、环境风险、可达性、急迫程度；\n"
            "   - casualty_assessment_classification（伤情评估与分类，核心节点）：必须包含以下子节点：\n"
            "       * near_field_sensing_init（近距感知初始化）：高清视觉、深度、红外；\n"
            "       * key_area_identification（重点部位识别）：出血点、骨折、胸腹部检查；\n"
            "       * vital_signs_measurement（生命体征测量）：血氧、心率、呼吸、体温；\n"
            "       * consciousness_mobility_assessment（意识与行动能力评估）：意识状态判定、行动能力判定；\n"
            "       必须包含 knowledge_graph 字段。\n"
            "   - rescue_method_matching（救援方式匹配）：担架无人车选型、担架配置、搬运姿势；\n"
            "   - path_rescue_flow_optimization（路径与救援流程优化）：最安全路线、分批/集中决策、装载顺序；\n"
            "   - coordination_strategy（协同策略）：指挥端同步、医疗点准备、途中监测；\n"
            "   - casualty_data_sync（救助完成伤情数据同步，核心节点）：必须包含以下子节点：\n"
            "       * data_organization_and_sync（伤情数据同步）：数据整理、链路选择、同步策略；\n"
            "       * task_closure（任务闭环）：同步确认、任务完成报告、资源释放；\n"
            "       必须包含 knowledge_graph 字段。\n"
            "2. casualty_localization 的 knowledge_graph 必须体现：接收消息 → 无人机搜索 → 确定可疑区域 → 机械狗确认 → 定位结果输出。\n"
            "3. casualty_assessment_classification 的 knowledge_graph 必须体现：近距感知 → 重点部位识别 → 生命体征测量 → 意识行动评估 → 伤情分级。\n"
            "4. casualty_data_sync 的 knowledge_graph 必须体现：数据整理 → 链路选择 → 同步传输 → 确认闭环。\n"
            "5. 在 node_insights 中，所有节点的 knowledge_trace 必须体现完整推理路径。"
        ),
        example_output={
            "default_focus": "casualty_assessment_classification",
            "behavior_tree": {
                "id": "rescue_mission",
                "label": "🚑 伤员救助任务",
                "status": "active",
                "summary": "从(85,20)出发救助区域X(210,145)的2名伤员并运回安全点(60,10)，全流程包含定位、评估、救援、转运与数据同步。",
                "children": [
                    {
                        "id": "casualty_localization",
                        "label": "📍 伤员定位",
                        "status": "completed",
                        "summary": "通过接收消息、无人机远距搜索、确定可疑区域、机器狗二次确认的完整流程，实现区域X(210,145)的2名伤员精确定位，定位精度±0.5m。",
                        "children": [
                            {
                                "id": "message_reception",
                                "label": "📨 接收消息",
                                "status": "completed",
                                "summary": "接收伤员求救信号或指挥端任务指令，初步获取伤员位置区域X(210,145)与伤员数量（2名）信息。",
                                "children": []
                            },
                            {
                                "id": "uav_search",
                                "label": "🚁 无人机搜索",
                                "status": "completed",
                                "summary": "派遣无人机在100m高度进行热成像扫描与生命信号捕获，覆盖500m×500m搜索区域，飞行时间约8分钟。",
                                "children": [
                                    {
                                        "id": "flight_planning",
                                        "label": "🗺️ 航迹规划",
                                        "status": "completed",
                                        "summary": "规划S型扫描航迹，确保区域全覆盖，航迹间隔50m，扫描效率95%。",
                                        "children": []
                                    },
                                    {
                                        "id": "thermal_scanning",
                                        "label": "🔥 热成像扫描",
                                        "status": "completed",
                                        "summary": "热成像相机检测温度异常点（36-37°C人体特征），灵敏度0.1°C，检测距离150m。",
                                        "children": []
                                    },
                                    {
                                        "id": "life_signal_capture",
                                        "label": "📡 生命信号捕获",
                                        "status": "completed",
                                        "summary": "扫描蓝牙、WiFi等可穿戴设备信号，辅助定位伤员位置。",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "id": "suspect_area_determination",
                                "label": "🎯 确定可疑区域",
                                "status": "completed",
                                "summary": "基于热成像扫描结果，检测到2处热源异常点，生成精细搜索网格，定位精度±10m。",
                                "children": [
                                    {
                                        "id": "thermal_spot_detection",
                                        "label": "🔥 区域热斑检测",
                                        "status": "completed",
                                        "summary": "热成像相机检测到2处体温特征的热源点，温度36-37°C，疑似伤员。",
                                        "children": []
                                    },
                                    {
                                        "id": "suspect_target_marking",
                                        "label": "🎯 可疑目标标注",
                                        "status": "completed",
                                        "summary": "标注疑似伤员位置为目标A(210,143)与目标B(212,146)，置信度85%。",
                                        "children": []
                                    },
                                    {
                                        "id": "search_grid_generation",
                                        "label": "🗺️ 搜索网格生成",
                                        "status": "completed",
                                        "summary": "生成以两处可疑目标为中心的20m×20m精细搜索网格，指导机器狗接近。",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "id": "robot_dog_confirmation",
                                "label": "🐕 机械狗二次确认",
                                "status": "completed",
                                "summary": "机器狗抵近目标区域，通过可穿戴信号检测、UWB超宽带定位、视觉/热成像特征确认，实现±0.5m精确定位。",
                                "children": [
                                    {
                                        "id": "wearable_signal_detection",
                                        "label": "⌚ 可穿戴信号检测",
                                        "status": "completed",
                                        "summary": "检测到1个可穿戴设备蓝牙信号（伤员A佩戴智能手环），信号强度-60dBm。",
                                        "children": []
                                    },
                                    {
                                        "id": "uwb_localization",
                                        "label": "📍 超宽带定位",
                                        "status": "completed",
                                        "summary": "UWB基站与标签测距，定位精度±0.3m，确认伤员A坐标(210.2, 143.1)。",
                                        "children": []
                                    },
                                    {
                                        "id": "visual_thermal_confirmation",
                                        "label": "👁️ 视觉/热成像特征确认",
                                        "status": "completed",
                                        "summary": "高清摄像头识别人体轮廓，热成像确认体温分布，置信度98%确认为伤员。",
                                        "children": []
                                    },
                                    {
                                        "id": "localization_result",
                                        "label": "✅ 定位结果输出",
                                        "status": "completed",
                                        "summary": "输出伤员A精确坐标(210.15, 143.08)、伤员B坐标(211.92, 145.95)，置信度97%，同步至救援系统。",
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": "task_analysis",
                        "label": "📋 任务解析",
                        "status": "completed",
                        "summary": "解析任务参数：伤员人数2名、区域X环境风险中等、可达性良好、急迫程度高。",
                        "children": []
                    },
                    {
                        "id": "casualty_assessment_classification",
                        "label": "🏥 伤情评估与分类",
                        "status": "completed",
                        "summary": "通过近距多模态感知、重点部位识别、生命体征测量与意识行动能力评估，对2名伤员进行精细伤情分级。",
                        "children": [
                            {
                                "id": "near_field_sensing_init",
                                "label": "📹 近距感知初始化",
                                "status": "completed",
                                "summary": "启动高清视觉、深度相机与红外传感器，构建伤员近场环境模型。",
                                "children": []
                            },
                            {
                                "id": "key_area_identification",
                                "label": "🔍 重点部位识别",
                                "status": "completed",
                                "summary": "识别伤员A左臂出血点、伤员B疑似左腿骨折，未见明显胸腹部异常。",
                                "children": []
                            },
                            {
                                "id": "vital_signs_measurement",
                                "label": "💓 生命体征测量",
                                "status": "completed",
                                "summary": "伤员A：血氧95%、心率98、呼吸18、体温36.8°C；伤员B：血氧92%、心率105、呼吸20、体温37.1°C。",
                                "children": []
                            },
                            {
                                "id": "consciousness_mobility_assessment",
                                "label": "🧠 意识与行动能力评估",
                                "status": "completed",
                                "summary": "伤员A意识清醒、可自主行动但需止血；伤员B意识清醒、行动受限需担架搬运。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "rescue_method_matching",
                        "label": "🚑 救援方式匹配",
                        "status": "completed",
                        "summary": "匹配2辆担架无人车，配置标准担架与急救包，伤员B平卧搬运、伤员A协助行走上车。",
                        "children": []
                    },
                    {
                        "id": "path_rescue_flow_optimization",
                        "label": "🗺️ 路径与救援流程优化",
                        "status": "completed",
                        "summary": "选择最安全路线(210,145)→(85,20)→(60,10)，采用分批救援，先转运重伤员B再接伤员A。",
                        "children": []
                    },
                    {
                        "id": "coordination_strategy",
                        "label": "🤝 协同策略",
                        "status": "completed",
                        "summary": "实时同步指挥端、通知医疗点准备接收、途中持续监测伤员生命体征。",
                        "children": []
                    },
                    {
                        "id": "casualty_data_sync",
                        "label": "📡 救助完成伤情数据同步",
                        "status": "completed",
                        "summary": "将伤情数据、定位信息、救援记录完整同步至指挥端，形成任务闭环。",
                        "children": [
                            {
                                "id": "data_organization_and_sync",
                                "label": "🗂️ 伤情数据同步",
                                "status": "completed",
                                "summary": "整理2名伤员生命体征、伤情分级、精确坐标，通过4G网络实时同步至指挥端。",
                                "children": []
                            },
                            {
                                "id": "task_closure",
                                "label": "✅ 任务闭环",
                                "status": "completed",
                                "summary": "指挥端确认数据接收，生成任务完成报告，释放救援设备资源。",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            "node_insights": {
                "casualty_localization": {
                    "title": "伤员定位",
                    "summary": "从区域任务解析到精确坐标输出的七阶段渐进式定位流程，实现从粗到精的伤员位置确定，最终定位精度±0.5m。",
                    "key_points": [
                        "区域任务解析：分析地形特征、遮挡情况与搜索范围，确定定位策略",
                        "远距感知方式选择：规划无人机航迹、配置热成像扫描与信号捕获方案",
                        "远距粗粒度定位：热斑检测+目标标注+网格生成，定位精度±10m",
                        "向精细定位阶段过渡：引导机械狗导航至疑似位置，优化接近路线",
                        "近距多模态精定位：融合可穿戴信号、UWB、视觉与热成像，精度±0.5m",
                        "误差修正与坐标融合：多传感器一致性校准、遮挡补偿、异常值剔除",
                        "定位结果确认与同步：输出精确坐标、置信度评估、同步至救援系统"
                    ],
                    "knowledge_trace": "区域任务解析 → 远距感知方式选择 → 远距粗粒度定位 → 向精细定位阶段过渡 → 近距多模态精定位 → 误差修正与坐标融合 → 定位结果确认与同步。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "task_parsing", "label": "区域任务解析", "type": "input"},
                            {"id": "remote_sensing_selection",
                                "label": "远距感知方式选择", "type": "process"},
                            {"id": "coarse_localization",
                                "label": "远距粗粒度定位", "type": "process"},
                            {"id": "transition_to_fine",
                                "label": "向精细定位阶段过渡", "type": "process"},
                            {"id": "fine_localization",
                                "label": "近距多模态精定位", "type": "process"},
                            {"id": "error_correction",
                                "label": "误差修正与坐标融合", "type": "process"},
                            {"id": "result_confirm",
                                "label": "定位结果确认与同步", "type": "output"}
                        ],
                        "edges": [
                            {"source": "task_parsing",
                                "target": "remote_sensing_selection"},
                            {"source": "remote_sensing_selection",
                                "target": "coarse_localization"},
                            {"source": "coarse_localization",
                                "target": "transition_to_fine"},
                            {"source": "transition_to_fine",
                                "target": "fine_localization"},
                            {"source": "fine_localization",
                                "target": "error_correction"},
                            {"source": "error_correction",
                                "target": "result_confirm"}
                        ]
                    }
                },
                "task_analysis": {
                    "title": "任务解析",
                    "summary": "解析任务关键参数，为后续救援决策提供依据。",
                    "key_points": [
                        "受伤人数：2名伤员需要救助",
                        "环境风险：区域X风险等级中等，无明显次生灾害",
                        "可达性：路线通畅，无人车可直接抵达",
                        "急迫程度：伤情稳定但需尽快转运"
                    ],
                    "knowledge_trace": "任务文本解析 → 提取关键参数 → 评估风险与优先级 → 输出任务配置。"
                },
                "casualty_assessment_classification": {
                    "title": "伤情评估与分类",
                    "summary": "通过近距感知初始化、重点部位识别、生命体征精细测量，最终形成伤情诊断与救治建议的完整评估流程。",
                    "key_points": [
                        "近距感知初始化：启动高清视觉、深度相机与红外传感器，构建伤员近场环境模型",
                        "重点部位识别：自动识别出血点、骨折可疑部位、胸腹部异常区域",
                        "生命体征精细测量：精确测量血氧、心率、呼吸频率、体温等关键指标",
                        "伤情诊断与建议：综合分析形成诊断结论，给出止血、固定、搬运姿势调整等救治建议"
                    ],
                    "knowledge_trace": "近距感知初始化 → 重点部位识别 → 生命体征精细测量 → 伤情诊断与建议。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "near_field_sensing_init",
                                "label": "近距感知初始化", "type": "input"},
                            {"id": "key_area_identification",
                                "label": "重点部位识别", "type": "process"},
                            {"id": "vital_signs_measurement",
                                "label": "生命体征精细测量", "type": "process"},
                            {"id": "diagnosis_recommendation",
                                "label": "伤情诊断与建议", "type": "output"}
                        ],
                        "edges": [
                            {"source": "near_field_sensing_init",
                                "target": "key_area_identification"},
                            {"source": "key_area_identification",
                                "target": "vital_signs_measurement"},
                            {"source": "vital_signs_measurement",
                                "target": "diagnosis_recommendation"}
                        ]
                    }
                },
                "rescue_method_matching": {
                    "title": "救援方式匹配",
                    "summary": "根据伤情分级结果，匹配合适的救援设备与搬运方式。",
                    "key_points": [
                        "设备选型：2辆担架无人车，载重能力200kg",
                        "担架配置：标准平板担架，适配骨折与出血伤员",
                        "搬运姿势：重伤员平卧固定，轻伤员协助上车",
                        "急救配置：配备止血包、固定夹板等基础急救物资"
                    ],
                    "knowledge_trace": "伤情分级结果 → 救援设备匹配 → 搬运方式选择 → 急救物资配置。"
                },
                "path_rescue_flow_optimization": {
                    "title": "路径与救援流程优化",
                    "summary": "规划最安全高效的救援路线与转运流程。",
                    "key_points": [
                        "路径规划：(210,145)→(85,20)→(60,10)，总距离约180m",
                        "救援策略：分批救援，优先转运行动受限的重伤员",
                        "时间预估：单程约5分钟，双批次约15分钟完成",
                        "安全措施：避开坍塌区域，选择平坦路面"
                    ],
                    "knowledge_trace": "地图数据 + 伤情分级 → 路径规划 → 批次决策 → 流程优化方案。"
                },
                "coordination_strategy": {
                    "title": "协同策略",
                    "summary": "确保救援过程中各方协同配合，信息实时共享。",
                    "key_points": [
                        "指挥端同步：实时上报救援进度与伤员状态",
                        "医疗点准备：提前通知医疗点准备接收伤员",
                        "途中监测：持续监测生命体征，异常时立即告警",
                        "资源调度：根据实时状况动态调整救援资源"
                    ],
                    "knowledge_trace": "任务启动 → 多方通信建立 → 状态实时同步 → 协同执行 → 异常响应。"
                },
                "casualty_data_sync": {
                    "title": "救助完成伤情数据同步",
                    "summary": "将完整救援数据同步至指挥系统，形成任务闭环。",
                    "key_points": [
                        "数据结构整理：汇总生命体征、伤情分级、位置坐标等完整记录",
                        "通信链路选择：在点对点、组网中继、卫星链路中选择合适传输路径",
                        "数据同步策略：配置周期同步、事件触发与异常加密传输策略",
                        "同步确认：指挥端数据校验、时间戳比对，确认接收完成形成任务闭环"
                    ],
                    "knowledge_trace": "数据结构整理 → 通信链路选择 → 数据同步策略 → 同步确认。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "data_structure_org",
                                "label": "数据结构整理", "type": "input"},
                            {"id": "communication_link",
                                "label": "通信链路选择", "type": "process"},
                            {"id": "sync_strategy",
                                "label": "数据同步策略", "type": "process"},
                            {"id": "sync_confirmation",
                                "label": "同步确认", "type": "output"}
                        ],
                        "edges": [
                            {"source": "data_structure_org",
                                "target": "communication_link"},
                            {"source": "communication_link",
                                "target": "sync_strategy"},
                            {"source": "sync_strategy",
                                "target": "sync_confirmation"}
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
    )
]
