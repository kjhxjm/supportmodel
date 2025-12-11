from typing import List
from .schema import Scenario

SCENARIOS: List[Scenario] = [
    # 二、设备投放支援模型测试（7~12）
    Scenario(
        id="equipment_deployment_strategy",  # 设备投放策略（综合场景）
        model_name="设备投放",
        name="设备投放策略",
        example_input="（85,20）向前沿区域X（210,145）投放设备资源Y共2套，区域周边地形复杂且存在环境干扰风险，要求在确保作业安全的前提下于30分钟内完成部署。",
        reasoning_chain="任务解析（设备类型、重量、功能、生存性要求、投放精度需求、环境风险）→ 设备匹配（匹配适用的无人车类型）→ 数量推断（根据载荷能力与冗余策略推算所需设备数量）→ 投放方式匹配（地面配送、自主装卸、协同投放）→ 目标定位（环境解析、传感器融合定位、误差纠正、定位结果生成）→ 投放位置优化（基于地形、目标定位、信号覆盖）→ 风险规避策略（选择低可探测路径、规避威胁区域、备用投放点设置）→ 自主装卸控制（装卸需求解析、动作规划、安全检测、装卸完成确认）→ 投放确认（结果感知、落点偏差分析、功能状态检查、投放成功判定）",
        prompt=(
            "【设备投放-设备投放策略专项要求】\n"
            "1. 行为树必须至少包含以下核心节点，严格按照推理链条自上而下展开：\n"
            "   - task_analysis（任务解析）：解析设备类型（设备资源Y）、重量体积、功能、生存性要求、投放精度需求、环境干扰风险、时间约束（30分钟）；\n"
            "   - equipment_matching（设备匹配）：基于地形与载重特点，选择适用的无人车类型（机器狗/六轮越野无人车），说明选择理由；\n"
            "   - quantity_inference（数量推断）：根据载荷能力与冗余策略推算所需设备数量，确保2套设备安全运输；\n"
            "   - delivery_method_matching（投放方式匹配）：决定投放方式（地面配送、自主装卸、协同投放）；\n"
            "   - formation_summary（编组节点汇总）：汇总编组方案，必须包含 knowledge_graph；\n"
            "   - deployment_strategy（设备投放策略，二级节点）：必须包含以下子节点：\n"
            "       * target_localization（目标定位）：必须包含children以支持进一步展开，包含环境解析、传感器融合定位、误差纠正、定位结果生成；\n"
            "       * position_optimization（投放位置优化）：基于地形、信号覆盖优化投放点；\n"
            "       * risk_avoidance（风险规避策略）：低可探测路径选择、威胁区域规避、备用投放点设置；\n"
            "   - autonomous_loading_control（自主装卸控制，核心节点）：必须包含以下子节点：\n"
            "       * loading_requirement_analysis（装卸需求解析）：重量、尺寸、抓取方式；\n"
            "       * motion_planning（动作规划）：机械臂抓取路径、姿态调整、力控策略；\n"
            "       * safety_detection（安全检测）：防倾倒、防滑落、力反馈监测；\n"
            "       * loading_confirmation（装卸完成确认）：识别设备是否已稳定装载/完成卸载；\n"
            "       必须包含 knowledge_graph 字段。\n"
            "   - deployment_confirmation（投放确认）：必须包含以下子节点：\n"
            "       * result_perception（结果感知）：投放后图像、姿态信息、设备回传信号；\n"
            "       * landing_deviation_analysis（落点偏差分析）：比较实际坐标与目标坐标；\n"
            "       * function_status_check（功能状态检查）：是否正常通电、是否建立通信链路；\n"
            "       * deployment_success_judgment（投放成功判定）：成功/失败/需重投；\n"
            "       必须包含 knowledge_graph 字段。\n"
            "2. target_localization 节点的 knowledge_graph 必须体现：环境解析 → 传感器融合定位 → 误差纠正 → 定位结果生成。\n"
            "3. autonomous_loading_control 节点的 knowledge_graph 必须体现：装卸需求解析 → 动作规划 → 安全检测 → 装卸完成确认。\n"
            "4. deployment_confirmation 节点的 knowledge_graph 必须体现：结果感知 → 落点偏差分析 → 功能状态检查 → 投放成功判定。\n"
            "5. 在 node_insights 中，所有节点的 knowledge_trace 必须体现完整推理路径。\n"
            "6. 注意：本场景预设是在平整地面进行设备投放，使用无人车/机器狗，并非使用无人机。"
        ),
        example_output={
            "default_focus": "deployment_strategy",
            "behavior_tree": {
                "id": "deployment_strategy",
                "label": "🎯 设备投放策略",
                "status": "active",
                "summary": "生成包含任务解析、投放方式匹配、投放位置优化、风险规避与投放确认的完整投放策略，确保设备资源Y能够安全、准确、高效地投放至前沿区域X(210,145)。",
                "children": [
                    {
                        "id": "task_analysis",
                        "label": "📦 任务解析",
                        "status": "completed",
                        "summary": "解析从(85,20)向前沿区域X(210,145)投放设备资源Y共2套的任务，识别设备类型、重量体积、功能、生存性要求、投放精度需求与环境风险。",
                        "children": [
                            {
                                "id": "equipment_matching",
                                "label": "🚗 设备匹配：2辆六轮越野无人车+1只机器狗",
                                "status": "completed",
                                "summary": "基于156km运输距离、30分钟时限与复杂地形，选择2辆六轮越野无人车（各载1套设备Y）+1只机器狗（用于抵近侦察与精确定位），理由：六轮设计具备良好通过性与稳定性，机器狗适应复杂地形进行目标定位。",
                                "children": []
                            },
                            {
                                "id": "quantity_inference",
                                "label": "🔢 数量推断：2辆无人车+1只机器狗",
                                "status": "completed",
                                "summary": "设备资源Y单套重量约30kg，单车载重能力80kg，考虑运输安全余量（载重利用率70%），每车携带1套设备Y。增加1辆备用车应对故障，配置1只机器狗用于精确定位与辅助作业。最终编组：3辆六轮越野无人车（2主1备）+1只机器狗。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "delivery_method_matching",
                        "label": "📍 投放方式匹配：地面配送+自主装卸",
                        "status": "completed",
                        "summary": "基于平整地面投放环境与设备精度要求，选择地面配送+自主装卸方式。无人车到达投放点后，通过车载机械臂自主完成设备卸载与部署定位，机器狗辅助进行精确定位校准。",
                        "children": []
                    },
                    {
                        "id": "formation_summary",
                        "label": "✅ 编组节点汇总",
                        "status": "completed",
                        "summary": "形成由2辆六轮越野无人车（主力运输）+1辆备用车+1只机器狗（定位辅助）构成的投放编组，明确各自职责与协同方式。",
                        "children": []
                    },
                    {
                        "id": "position_optimization",
                        "label": "📐 投放位置优化",
                        "status": "completed",
                        "summary": "通过目标定位、地形分析与信号覆盖评估，优化最终投放点位置，确保设备部署后功能正常。",
                        "children": [
                            {
                                "id": "target_localization",
                                "label": "📍 目标定位",
                                "status": "completed",
                                "summary": "通过环境解析、多源传感器融合与误差纠正，实现前沿区域X(210,145)投放点的高精度定位。支持进一步展开查看详细定位流程。",
                                "children": [
                                    {
                                        "id": "environment_analysis",
                                        "label": "🗺️ 环境解析",
                                        "status": "completed",
                                        "summary": "读取前沿区域X的高精度地图（1:5000）、地物特征（建筑物、植被、道路）、遮挡信息（视线遮挡区、信号盲区），识别可能的投放候选点。",
                                        "children": [
                                            {
                                                "id": "map_reading",
                                                "label": "🗺️ 地图读取",
                                                "status": "completed",
                                                "summary": "加载1:5000高精度地图，包含地形高程、道路网络、建筑物轮廓、植被分布等信息，地图精度<0.5m。",
                                                "children": []
                                            },
                                            {
                                                "id": "terrain_feature",
                                                "label": "🏔️ 地物特征识别",
                                                "status": "completed",
                                                "summary": "识别目标区域周边的显著地物特征：建筑物（可作为参照物）、植被（可能遮挡信号）、平整地面区域（适合投放）。",
                                                "children": []
                                            },
                                            {
                                                "id": "occlusion_analysis",
                                                "label": "🚧 遮挡信息分析",
                                                "status": "completed",
                                                "summary": "分析视线遮挡区（影响视觉定位）、信号盲区（影响通信回传）、GPS多径效应区（影响定位精度），标注需规避区域。",
                                                "children": []
                                            }
                                        ]
                                    },
                                    {
                                        "id": "sensor_fusion_localization",
                                        "label": "📡 传感器融合定位",
                                        "status": "completed",
                                        "summary": "利用机器狗搭载的视觉相机、激光雷达、深度感知等多源传感器进行目标点推断，定位精度达到±0.3m。",
                                        "children": [
                                            {
                                                "id": "visual_recognition",
                                                "label": "👁️ 视觉识别",
                                                "status": "completed",
                                                "summary": "机器狗高清摄像头（4K分辨率）识别预设地面标记物（反光标识、颜色标记），视觉定位精度±0.5m。",
                                                "children": []
                                            },
                                            {
                                                "id": "lidar_ranging",
                                                "label": "📏 激光雷达测距",
                                                "status": "completed",
                                                "summary": "16线激光雷达扫描周边环境，构建3D点云地图，测距精度±2cm，有效距离100m。",
                                                "children": []
                                            },
                                            {
                                                "id": "depth_perception",
                                                "label": "🔍 深度感知",
                                                "status": "completed",
                                                "summary": "双目深度相机获取场景深度信息，结合点云数据进行三维重建，识别地面平整度与可投放区域。",
                                                "children": []
                                            },
                                            {
                                                "id": "data_fusion",
                                                "label": "🔗 多源数据融合",
                                                "status": "completed",
                                                "summary": "采用扩展卡尔曼滤波（EKF）融合视觉、激光雷达、深度感知与IMU数据，输出融合定位结果，精度±0.3m。",
                                                "children": []
                                            }
                                        ]
                                    },
                                    {
                                        "id": "error_correction",
                                        "label": "🔧 误差纠正",
                                        "status": "completed",
                                        "summary": "基于地面标志物（预设反光标识）进行定位偏差修正，消除累积误差与系统偏差，最终定位精度达到±0.1m。",
                                        "children": [
                                            {
                                                "id": "marker_detection",
                                                "label": "🎯 标志物检测",
                                                "status": "completed",
                                                "summary": "机器狗视觉系统检测预设地面反光标识（棋盘格图案），提取标识中心点坐标作为参考基准。",
                                                "children": []
                                            },
                                            {
                                                "id": "deviation_calculation",
                                                "label": "📐 偏差计算",
                                                "status": "completed",
                                                "summary": "比较融合定位结果与标志物基准坐标，计算水平偏差（ΔX, ΔY）与航向偏差（Δθ）。",
                                                "children": []
                                            },
                                            {
                                                "id": "correction_application",
                                                "label": "✅ 偏差修正",
                                                "status": "completed",
                                                "summary": "将计算的偏差值反向补偿至定位结果，更新坐标系变换矩阵，校正后定位精度±0.1m。",
                                                "children": []
                                            }
                                        ]
                                    },
                                    {
                                        "id": "localization_result",
                                        "label": "📍 定位结果生成",
                                        "status": "completed",
                                        "summary": "输出目标投放点的精确坐标(210.05, 145.02)，定位精度±0.1m，置信度98%，同步发送至无人车导航系统。",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "id": "terrain_suitability",
                                "label": "🏔️ 地形适宜性评估",
                                "status": "completed",
                                "summary": "评估候选投放点的地面平整度（坡度<5°）、承载能力（>100kg/m²）、排水条件，选择最优投放位置。",
                                "children": []
                            },
                            {
                                "id": "signal_coverage",
                                "label": "📶 信号覆盖评估",
                                "status": "completed",
                                "summary": "检测投放点的通信信号强度（4G/5G信号>-85dBm）、GPS信号质量（HDOP<2.0），确保设备部署后通信正常。",
                                "children": []
                            },
                            {
                                "id": "final_position",
                                "label": "✅ 最终位置确定",
                                "status": "completed",
                                "summary": "综合地形、信号与安全因素，确定最终投放点坐标(210.05, 145.02)，偏离初始目标0.07m，满足投放精度要求。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "risk_avoidance",
                        "label": "⚠️ 风险规避策略",
                        "status": "completed",
                        "summary": "制定包含低可探测路径选择、威胁区域规避与备用投放点设置的多层次风险规避方案。",
                        "children": [
                            {
                                "id": "low_detectability_path",
                                "label": "🛤️ 低可探测路径",
                                "status": "completed",
                                "summary": "规划利用地形遮蔽的行进路径，优先选择山脊背面、树林边缘等低可探测区域，降低被发现概率。",
                                "children": []
                            },
                            {
                                "id": "threat_zone_bypass",
                                "label": "🚫 威胁区域规避",
                                "status": "completed",
                                "summary": "标注环境干扰风险区域（电磁干扰区、不稳定地形区），规划绕行路径，安全距离>50m。",
                                "children": []
                            },
                            {
                                "id": "backup_deployment_point",
                                "label": "📍 备用投放点设置",
                                "status": "completed",
                                "summary": "预设2个备用投放点（距主投放点100m和200m），当主投放点不可用时自动切换，切换决策时间<30秒。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "autonomous_loading_control",
                        "label": "🦾 自主装卸控制",
                        "status": "active",
                        "summary": "控制无人车车载机械臂自主完成设备资源Y的装载与卸载动作，确保设备安全转移与精确放置。",
                        "children": [
                            {
                                "id": "loading_requirement_analysis",
                                "label": "📋 装卸需求解析",
                                "status": "completed",
                                "summary": "解析设备资源Y的物理特性：重量30kg、尺寸40×30×25cm、抓取方式（侧面夹持+底部托举）。",
                                "children": [
                                    {
                                        "id": "weight_analysis",
                                        "label": "⚖️ 重量分析",
                                        "status": "completed",
                                        "summary": "设备资源Y单套重量30kg，重心位于几何中心偏下5cm，需采用平衡抓取策略。",
                                        "children": []
                                    },
                                    {
                                        "id": "dimension_analysis",
                                        "label": "📏 尺寸分析",
                                        "status": "completed",
                                        "summary": "设备外形尺寸40×30×25cm，外壳材质为铝合金，表面有防滑纹理，适合机械夹持。",
                                        "children": []
                                    },
                                    {
                                        "id": "grip_method",
                                        "label": "🤖 抓取方式确定",
                                        "status": "completed",
                                        "summary": "采用侧面夹持（夹持力50-80N）+底部托举（托力>350N）的复合抓取方式，确保设备稳定。",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "id": "motion_planning",
                                "label": "🎯 动作规划",
                                "status": "completed",
                                "summary": "规划机械臂从车载位置到投放点的完整运动轨迹，包括抓取路径、姿态调整与力控策略。",
                                "children": [
                                    {
                                        "id": "arm_trajectory",
                                        "label": "🦾 机械臂抓取路径",
                                        "status": "completed",
                                        "summary": "六自由度机械臂从初始位置运动至设备位置，采用五次多项式轨迹规划，运动平滑无冲击，全程耗时8秒。",
                                        "children": []
                                    },
                                    {
                                        "id": "pose_adjustment",
                                        "label": "📐 姿态调整",
                                        "status": "completed",
                                        "summary": "根据设备当前姿态与目标放置姿态，计算末端执行器的旋转变换（Roll/Pitch/Yaw），调整精度±1°。",
                                        "children": []
                                    },
                                    {
                                        "id": "force_control",
                                        "label": "💪 力控策略",
                                        "status": "completed",
                                        "summary": "采用阻抗控制模式，设置刚度系数K=500N/m、阻尼系数B=50Ns/m，实现柔顺接触与安全放置。",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "id": "safety_detection",
                                "label": "🛡️ 安全检测",
                                "status": "completed",
                                "summary": "实时监测装卸过程中的安全状态，包括防倾倒、防滑落与力反馈监测。",
                                "children": [
                                    {
                                        "id": "anti_tipping",
                                        "label": "⚖️ 防倾倒检测",
                                        "status": "completed",
                                        "summary": "IMU实时监测设备倾斜角度，当倾斜>15°时触发防护动作（降低移动速度、调整抓取姿态）。",
                                        "children": []
                                    },
                                    {
                                        "id": "anti_slip",
                                        "label": "🔒 防滑落检测",
                                        "status": "completed",
                                        "summary": "夹持力传感器监测抓取力变化，当检测到力突降>20%时判定为滑落风险，自动增加夹持力或暂停动作。",
                                        "children": []
                                    },
                                    {
                                        "id": "force_feedback",
                                        "label": "📊 力反馈监测",
                                        "status": "completed",
                                        "summary": "六维力传感器实时监测末端力矩（Fx/Fy/Fz/Mx/My/Mz），当任意方向力超过安全阈值（100N/10Nm）时触发紧急停止。",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "id": "loading_confirmation",
                                "label": "✅ 装卸完成确认",
                                "status": "completed",
                                "summary": "通过多传感器验证设备是否已稳定装载或完成卸载，生成装卸完成状态报告。",
                                "children": [
                                    {
                                        "id": "position_verification",
                                        "label": "📍 位置验证",
                                        "status": "completed",
                                        "summary": "视觉系统确认设备已放置于目标位置，位置偏差<5cm，姿态偏差<3°。",
                                        "children": []
                                    },
                                    {
                                        "id": "stability_check",
                                        "label": "⚖️ 稳定性检查",
                                        "status": "completed",
                                        "summary": "机械臂缓慢释放夹持力，IMU监测设备5秒内无位移变化（<1mm），确认设备稳定放置。",
                                        "children": []
                                    },
                                    {
                                        "id": "loading_status_report",
                                        "label": "📋 装卸状态报告",
                                        "status": "completed",
                                        "summary": "生成装卸完成报告：设备编号、放置坐标、放置时间、姿态参数、稳定性评估结果，上传至指挥端。",
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "id": "deployment_confirmation",
                        "label": "🔍 投放确认",
                        "status": "pending",
                        "summary": "通过视觉、位姿与通信回传等方式自动确认设备投放结果，判定投放成功与否。",
                        "children": [
                            {
                                "id": "result_perception",
                                "label": "👁️ 结果感知",
                                "status": "pending",
                                "summary": "采集投放后的设备状态信息，包括图像、姿态与设备回传信号。",
                                "children": [
                                    {
                                        "id": "post_deployment_image",
                                        "label": "📷 投放后图像采集",
                                        "status": "pending",
                                        "summary": "机器狗高清摄像头拍摄设备部署后的全景图像与特写图像，用于视觉确认与存档。",
                                        "children": []
                                    },
                                    {
                                        "id": "pose_information",
                                        "label": "📐 姿态信息获取",
                                        "status": "pending",
                                        "summary": "通过视觉与激光雷达测量设备当前姿态（位置+方向），与目标姿态进行比对。",
                                        "children": []
                                    },
                                    {
                                        "id": "device_signal",
                                        "label": "📶 设备回传信号",
                                        "status": "pending",
                                        "summary": "检测设备Y是否开始发送心跳信号（每5秒一次），确认设备已激活并进入工作状态。",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "id": "landing_deviation_analysis",
                                "label": "📏 落点偏差分析",
                                "status": "pending",
                                "summary": "比较设备实际放置坐标与目标坐标，计算水平偏差与航向偏差。",
                                "children": [
                                    {
                                        "id": "actual_coordinate",
                                        "label": "📍 实际坐标测量",
                                        "status": "pending",
                                        "summary": "通过RTK-GPS与视觉定位融合，测量设备实际放置坐标，精度±5cm。",
                                        "children": []
                                    },
                                    {
                                        "id": "deviation_calculation_deploy",
                                        "label": "📐 偏差计算",
                                        "status": "pending",
                                        "summary": "计算实际坐标(210.08, 145.01)与目标坐标(210.05, 145.02)的偏差：水平偏差3.2cm，满足精度要求（<10cm）。",
                                        "children": []
                                    },
                                    {
                                        "id": "heading_deviation",
                                        "label": "🧭 航向偏差",
                                        "status": "pending",
                                        "summary": "测量设备实际朝向与目标朝向的角度差，偏差1.5°，满足精度要求（<5°）。",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "id": "function_status_check",
                                "label": "🔌 功能状态检查",
                                "status": "pending",
                                "summary": "检查设备是否正常通电、是否建立通信链路，验证设备功能完整性。",
                                "children": [
                                    {
                                        "id": "power_status",
                                        "label": "🔋 通电状态",
                                        "status": "pending",
                                        "summary": "检测设备电源指示灯状态（绿色常亮=正常），电池电量>90%，供电电压12.1V正常。",
                                        "children": []
                                    },
                                    {
                                        "id": "communication_link",
                                        "label": "📡 通信链路",
                                        "status": "pending",
                                        "summary": "验证设备与指挥端的通信链路：4G信号强度-72dBm，心跳包传输正常，延迟<200ms。",
                                        "children": []
                                    },
                                    {
                                        "id": "sensor_self_test",
                                        "label": "🔍 传感器自检",
                                        "status": "pending",
                                        "summary": "设备执行传感器自检程序，所有传感器（摄像头、麦克风、温湿度计）工作正常，自检通过。",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "id": "deployment_success_judgment",
                                "label": "✅ 投放成功判定",
                                "status": "pending",
                                "summary": "综合落点偏差、功能状态等信息，判定投放结果为成功/失败/需重投。",
                                "children": [
                                    {
                                        "id": "criteria_evaluation",
                                        "label": "📋 判定标准评估",
                                        "status": "pending",
                                        "summary": "评估各项指标：位置偏差3.2cm(<10cm✓)、航向偏差1.5°(<5°✓)、通电正常✓、通信正常✓、传感器自检通过✓。",
                                        "children": []
                                    },
                                    {
                                        "id": "final_judgment",
                                        "label": "🏁 最终判定",
                                        "status": "pending",
                                        "summary": "所有判定标准均满足，投放结果判定为【成功】，生成投放完成报告并上传指挥端。",
                                        "children": []
                                    },
                                    {
                                        "id": "retry_strategy",
                                        "label": "🔄 重投策略（备用）",
                                        "status": "pending",
                                        "summary": "若判定失败，启动重投流程：分析失败原因、调整投放参数、切换备用投放点（如需要）、执行重新投放。",
                                        "children": []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务解析",
                    "summary": "从任务文本中提取起点(85,20)、目标区域X(210,145)、设备资源Y（2套）、地形特征（复杂）、环境风险（干扰风险）、时间约束（30分钟）。",
                    "key_points": [
                        "起点坐标(85,20)，目标区域X坐标(210,145)，直线距离约156km",
                        "设备资源Y共2套，需确保运输安全与投放精度",
                        "时间约束：30分钟内完成部署，平均速度需>300km/h（不现实，需多车协同或分阶段部署）",
                        "风险因素：地形复杂、存在环境干扰风险，需预留备用投放点与应急方案"
                    ],
                    "knowledge_trace": "任务文本 → 坐标/距离/设备/时限/风险要素提取 → 形成任务约束条件 → 为后续设备匹配与策略生成提供输入。"
                },
                "equipment_matching": {
                    "title": "设备匹配",
                    "summary": "基于复杂地形、投放精度需求与设备重量，选择六轮越野无人车+机器狗的组合方案。",
                    "key_points": [
                        "六轮越野无人车：最高时速60km/h，续航150km，载重能力80kg，具备良好通过性（爬坡能力30°）",
                        "机器狗：四足行走适应复杂地形，搭载高精度传感器用于目标定位，最高速度3m/s",
                        "选择理由：六轮设计提供稳定运输能力，机器狗实现复杂地形下的精确定位与辅助作业",
                        "注意：本场景在平整地面进行设备投放，不使用无人机"
                    ],
                    "knowledge_trace": "运输距离+地形约束 → 平台能力分析 → 选择六轮越野无人车（运输）+ 机器狗（定位）组合方案。"
                },
                "quantity_inference": {
                    "title": "数量推断",
                    "summary": "依据设备Y重量体积与单车载荷，叠加冗余策略，推算所需无人车与机器狗数量。",
                    "key_points": [
                        "设备资源Y单套重量约30kg，体积40×30×25cm",
                        "单车有效载荷：80kg×70%=56kg（考虑安全余量）",
                        "运输需求：2套设备Y（共60kg），需2辆无人车（各携带1套）",
                        "冗余配置：增加1辆备用车+1只机器狗，最终编组3辆无人车+1只机器狗"
                    ],
                    "knowledge_trace": "设备总载荷计算 → 单车有效载荷评估 → 理论数量计算 → 冗余策略叠加 → 最终编组数量。"
                },
                "delivery_method_matching": {
                    "title": "投放方式匹配",
                    "summary": "在平整地面投放环境下，选择地面配送+自主装卸的投放方式。",
                    "key_points": [
                        "地面配送：无人车直接将设备运输至投放点附近",
                        "自主装卸：车载机械臂自主完成设备卸载与精确放置",
                        "协同投放：机器狗提供精确定位引导，无人车执行放置动作",
                        "选择理由：平整地面条件良好，自主装卸可实现高精度投放（<10cm）"
                    ],
                    "knowledge_trace": "环境条件评估 → 候选投放方式分析 → 精度需求匹配 → 选定地面配送+自主装卸方案。"
                },
                "formation_summary": {
                    "title": "编组节点汇总",
                    "summary": "将任务解析、设备匹配、数量推断和投放方式的结论汇总为可执行的编组方案。",
                    "key_points": [
                        "编组构成：2辆六轮越野无人车（主力运输）+1辆备用车+1只机器狗（定位辅助）",
                        "任务分工：主力车各载1套设备Y，备用车待命，机器狗先行进行目标定位",
                        "协同方式：机器狗引导→无人车到位→自主装卸→投放确认",
                        "时间规划：机器狗先行（10分钟）+无人车运输（15分钟）+装卸投放（5分钟）=30分钟"
                    ],
                    "knowledge_trace": "任务要素 → 设备匹配 → 数量与方式推断 → 汇总为编组方案。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "task_analysis",
                                "label": "任务解析(设备Y, 区域X)", "type": "input"},
                            {"id": "equipment_matching",
                                "label": "设备匹配(无人车+机器狗)", "type": "process"},
                            {"id": "quantity_inference",
                                "label": "数量计算(载荷+冗余)", "type": "process"},
                            {"id": "delivery_method",
                                "label": "投放方式选择", "type": "decision"},
                            {"id": "formation_plan",
                                "label": "编组方案输出", "type": "output"}
                        ],
                        "edges": [
                            {"source": "task_analysis",
                                "target": "equipment_matching"},
                            {"source": "equipment_matching",
                                "target": "quantity_inference"},
                            {"source": "quantity_inference",
                                "target": "delivery_method"},
                            {"source": "delivery_method",
                                "target": "formation_plan"}
                        ]
                    }
                },
                "deployment_strategy": {
                    "title": "设备投放策略",
                    "summary": "整合目标定位、投放位置优化与风险规避措施，生成完整的设备投放执行方案。",
                    "key_points": [
                        "目标定位：机器狗多源传感器融合实现±0.1m精度定位",
                        "位置优化：综合地形、信号覆盖优化最终投放点",
                        "风险规避：低可探测路径+威胁区域规避+备用投放点",
                        "执行流程：定位→优化→规避→装卸→确认"
                    ],
                    "knowledge_trace": "编组方案 + 目标定位 + 位置优化 + 风险规避 → 形成可执行投放策略。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "formation", "label": "编组方案", "type": "input"},
                            {"id": "target_loc", "label": "目标定位", "type": "process"},
                            {"id": "position_opt", "label": "投放位置优化",
                                "type": "process"},
                            {"id": "risk_avoid", "label": "风险规避策略", "type": "process"},
                            {"id": "loading_ctrl", "label": "自主装卸控制",
                                "type": "process"},
                            {"id": "deploy_confirm",
                                "label": "投放确认", "type": "output"}
                        ],
                        "edges": [
                            {"source": "formation", "target": "target_loc"},
                            {"source": "target_loc", "target": "position_opt"},
                            {"source": "position_opt", "target": "risk_avoid"},
                            {"source": "risk_avoid", "target": "loading_ctrl"},
                            {"source": "loading_ctrl", "target": "deploy_confirm"}
                        ]
                    }
                },
                "target_localization": {
                    "title": "目标定位",
                    "summary": "通过环境解析、多源传感器融合与误差纠正，实现目标投放点的高精度定位。",
                    "key_points": [
                        "环境解析：读取高精度地图、识别地物特征、分析遮挡信息",
                        "传感器融合：机器狗视觉+激光雷达+深度感知+IMU数据融合，精度±0.3m",
                        "误差纠正：基于地面标志物进行偏差修正，最终精度±0.1m",
                        "定位结果：输出精确坐标与置信度，用于投放位置优化"
                    ],
                    "knowledge_trace": "环境解析 → 传感器融合定位 → 误差纠正 → 定位结果生成。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "env_analysis", "label": "环境解析", "type": "input"},
                            {"id": "map_read", "label": "地图读取", "type": "input"},
                            {"id": "terrain_feat", "label": "地物特征识别", "type": "input"},
                            {"id": "occlusion", "label": "遮挡信息分析", "type": "input"},
                            {"id": "sensor_fusion",
                                "label": "传感器融合定位", "type": "process"},
                            {"id": "visual", "label": "视觉识别", "type": "process"},
                            {"id": "lidar", "label": "激光雷达测距", "type": "process"},
                            {"id": "depth", "label": "深度感知", "type": "process"},
                            {"id": "error_corr", "label": "误差纠正", "type": "process"},
                            {"id": "loc_result", "label": "定位结果生成", "type": "output"}
                        ],
                        "edges": [
                            {"source": "map_read", "target": "env_analysis"},
                            {"source": "terrain_feat", "target": "env_analysis"},
                            {"source": "occlusion", "target": "env_analysis"},
                            {"source": "env_analysis", "target": "sensor_fusion"},
                            {"source": "visual", "target": "sensor_fusion"},
                            {"source": "lidar", "target": "sensor_fusion"},
                            {"source": "depth", "target": "sensor_fusion"},
                            {"source": "sensor_fusion", "target": "error_corr"},
                            {"source": "error_corr", "target": "loc_result"}
                        ]
                    }
                },
                "environment_analysis": {
                    "title": "环境解析",
                    "summary": "读取目标区域的地图、地物特征与遮挡信息，为传感器融合定位提供先验知识。",
                    "key_points": [
                        "地图数据：1:5000高精度地图，包含地形高程、道路、建筑物、植被分布",
                        "地物特征：识别可作为参照物的显著地标（建筑物角点、道路交叉口）",
                        "遮挡分析：标注视线遮挡区（影响视觉定位）、信号盲区（影响通信）、GPS多径区"
                    ],
                    "knowledge_trace": "地图加载 → 地物特征提取 → 遮挡区域标注 → 形成环境先验模型。"
                },
                "sensor_fusion_localization": {
                    "title": "传感器融合定位",
                    "summary": "融合机器狗搭载的多源传感器数据，实现目标点的高精度推断。",
                    "key_points": [
                        "视觉识别：4K摄像头识别预设标记，视觉定位精度±0.5m",
                        "激光雷达：16线LiDAR构建3D点云，测距精度±2cm",
                        "深度感知：双目相机获取场景深度，识别地面平整度",
                        "数据融合：EKF算法融合多源数据，输出精度±0.3m"
                    ],
                    "knowledge_trace": "多传感器数据采集 → 特征提取 → EKF融合 → 融合定位结果输出。"
                },
                "error_correction": {
                    "title": "误差纠正",
                    "summary": "基于地面标志物进行定位偏差修正，消除累积误差与系统偏差。",
                    "key_points": [
                        "标志物检测：识别预设地面反光标识（棋盘格图案）",
                        "偏差计算：比较融合结果与标志物基准，计算水平与航向偏差",
                        "修正应用：反向补偿偏差值，校正后精度±0.1m"
                    ],
                    "knowledge_trace": "标志物检测 → 偏差计算 → 补偿修正 → 输出高精度定位结果。"
                },
                "localization_result": {
                    "title": "定位结果生成",
                    "summary": "输出目标投放点的精确坐标，附带精度评估与置信度指标。",
                    "key_points": [
                        "坐标输出：目标点精确坐标(210.05, 145.02)，坐标系WGS84",
                        "精度评估：水平精度±0.1m，航向精度±0.5°",
                        "置信度：定位置信度98%，满足投放精度要求",
                        "数据同步：定位结果实时同步至无人车导航系统"
                    ],
                    "knowledge_trace": "误差纠正后数据 → 坐标格式转换 → 精度与置信度评估 → 结果输出与同步。"
                },
                "position_optimization": {
                    "title": "投放位置优化",
                    "summary": "基于地形、信号覆盖等因素，优化最终投放点位置。",
                    "key_points": [
                        "地形适宜性：坡度<5°、承载力>100kg/m²、排水良好",
                        "信号覆盖：4G/5G信号>-85dBm、GPS HDOP<2.0",
                        "综合优化：在满足精度要求前提下选择最优投放位置"
                    ],
                    "knowledge_trace": "定位结果 + 地形评估 + 信号评估 → 综合优化 → 最终位置确定。"
                },
                "risk_avoidance": {
                    "title": "风险规避策略",
                    "summary": "制定多层次风险规避方案，确保投放任务安全完成。",
                    "key_points": [
                        "低可探测路径：利用地形遮蔽规划行进路径，降低被发现概率",
                        "威胁区域规避：标注电磁干扰区、不稳定地形区，安全距离>50m",
                        "备用投放点：预设2个备用点，切换决策时间<30秒"
                    ],
                    "knowledge_trace": "威胁识别 → 路径规划 → 区域规避 → 备用点设置 → 形成风险规避方案。"
                },
                "autonomous_loading_control": {
                    "title": "自主装卸控制",
                    "summary": "控制无人车机械臂自主完成设备装载与卸载，确保设备安全转移与精确放置。",
                    "key_points": [
                        "装卸需求解析：设备重量30kg、尺寸40×30×25cm、侧面夹持+底部托举",
                        "动作规划：五次多项式轨迹规划、姿态调整精度±1°、阻抗力控",
                        "安全检测：防倾倒（>15°触发）、防滑落（力突降>20%触发）、力反馈监测",
                        "装卸确认：位置偏差<5cm、姿态偏差<3°、5秒稳定性验证"
                    ],
                    "knowledge_trace": "装卸需求解析 → 动作规划 → 安全检测 → 装卸完成确认。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "load_req", "label": "装卸需求解析", "type": "input"},
                            {"id": "weight", "label": "重量分析", "type": "input"},
                            {"id": "dimension", "label": "尺寸分析", "type": "input"},
                            {"id": "grip", "label": "抓取方式", "type": "input"},
                            {"id": "motion_plan", "label": "动作规划", "type": "process"},
                            {"id": "trajectory", "label": "机械臂轨迹", "type": "process"},
                            {"id": "pose_adj", "label": "姿态调整", "type": "process"},
                            {"id": "force_ctrl", "label": "力控策略", "type": "process"},
                            {"id": "safety_det", "label": "安全检测", "type": "decision"},
                            {"id": "load_confirm", "label": "装卸完成确认", "type": "output"}
                        ],
                        "edges": [
                            {"source": "weight", "target": "load_req"},
                            {"source": "dimension", "target": "load_req"},
                            {"source": "grip", "target": "load_req"},
                            {"source": "load_req", "target": "motion_plan"},
                            {"source": "trajectory", "target": "motion_plan"},
                            {"source": "pose_adj", "target": "motion_plan"},
                            {"source": "force_ctrl", "target": "motion_plan"},
                            {"source": "motion_plan", "target": "safety_det"},
                            {"source": "safety_det", "target": "load_confirm"}
                        ]
                    }
                },
                "loading_requirement_analysis": {
                    "title": "装卸需求解析",
                    "summary": "解析设备资源Y的物理特性，确定抓取与放置方式。",
                    "key_points": [
                        "重量分析：单套30kg，重心偏下5cm，需平衡抓取",
                        "尺寸分析：40×30×25cm，铝合金外壳，表面防滑纹理",
                        "抓取方式：侧面夹持（50-80N）+ 底部托举（>350N）"
                    ],
                    "knowledge_trace": "设备规格获取 → 重量/尺寸分析 → 抓取方式确定 → 为动作规划提供参数。"
                },
                "motion_planning": {
                    "title": "动作规划",
                    "summary": "规划机械臂的完整运动轨迹，包括路径、姿态与力控。",
                    "key_points": [
                        "抓取路径：五次多项式轨迹规划，运动平滑，耗时8秒",
                        "姿态调整：末端执行器Roll/Pitch/Yaw调整，精度±1°",
                        "力控策略：阻抗控制模式，刚度K=500N/m，阻尼B=50Ns/m"
                    ],
                    "knowledge_trace": "装卸需求 → 轨迹规划 → 姿态计算 → 力控参数设置 → 完整动作序列。"
                },
                "safety_detection": {
                    "title": "安全检测",
                    "summary": "实时监测装卸过程中的安全状态，及时触发防护动作。",
                    "key_points": [
                        "防倾倒：IMU监测倾斜角，>15°触发降速/调整姿态",
                        "防滑落：力传感器监测夹持力，突降>20%触发增力/暂停",
                        "力反馈：六维力传感器监测，超阈值（100N/10Nm）触发急停"
                    ],
                    "knowledge_trace": "多传感器实时监测 → 阈值判断 → 防护动作触发 → 安全状态确认。"
                },
                "loading_confirmation": {
                    "title": "装卸完成确认",
                    "summary": "通过多传感器验证设备装卸状态，生成完成报告。",
                    "key_points": [
                        "位置验证：视觉确认设备位置偏差<5cm，姿态偏差<3°",
                        "稳定性检查：释放夹持力后5秒内无位移变化（<1mm）",
                        "状态报告：生成装卸完成报告，上传指挥端"
                    ],
                    "knowledge_trace": "位置验证 → 稳定性检查 → 状态报告生成 → 上传确认。"
                },
                "deployment_confirmation": {
                    "title": "投放确认",
                    "summary": "通过视觉、位姿与通信回传自动确认投放结果，判定成功与否。",
                    "key_points": [
                        "结果感知：采集投放后图像、姿态、设备回传信号",
                        "落点偏差：比较实际与目标坐标，水平偏差<10cm判定合格",
                        "功能检查：验证通电状态、通信链路、传感器自检",
                        "成功判定：综合评估，输出成功/失败/需重投结论"
                    ],
                    "knowledge_trace": "结果感知 → 落点偏差分析 → 功能状态检查 → 投放成功判定。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "result_perc", "label": "结果感知", "type": "input"},
                            {"id": "image", "label": "投放后图像", "type": "input"},
                            {"id": "pose", "label": "姿态信息", "type": "input"},
                            {"id": "signal", "label": "设备回传信号", "type": "input"},
                            {"id": "deviation", "label": "落点偏差分析", "type": "process"},
                            {"id": "func_check", "label": "功能状态检查", "type": "process"},
                            {"id": "power", "label": "通电状态", "type": "process"},
                            {"id": "comm", "label": "通信链路", "type": "process"},
                            {"id": "self_test", "label": "传感器自检", "type": "process"},
                            {"id": "judgment", "label": "投放成功判定", "type": "output"}
                        ],
                        "edges": [
                            {"source": "image", "target": "result_perc"},
                            {"source": "pose", "target": "result_perc"},
                            {"source": "signal", "target": "result_perc"},
                            {"source": "result_perc", "target": "deviation"},
                            {"source": "deviation", "target": "func_check"},
                            {"source": "power", "target": "func_check"},
                            {"source": "comm", "target": "func_check"},
                            {"source": "self_test", "target": "func_check"},
                            {"source": "func_check", "target": "judgment"}
                        ]
                    }
                },
                "result_perception": {
                    "title": "结果感知",
                    "summary": "采集投放后的设备状态信息，为投放确认提供数据支撑。",
                    "key_points": [
                        "图像采集：机器狗高清摄像头拍摄全景与特写图像",
                        "姿态测量：视觉+激光雷达测量设备当前位置与方向",
                        "信号检测：检测设备心跳信号（每5秒），确认设备激活"
                    ],
                    "knowledge_trace": "图像采集 + 姿态测量 + 信号检测 → 形成结果感知数据集。"
                },
                "landing_deviation_analysis": {
                    "title": "落点偏差分析",
                    "summary": "比较实际放置坐标与目标坐标，计算并评估偏差。",
                    "key_points": [
                        "实际坐标：RTK-GPS+视觉融合测量，精度±5cm",
                        "偏差计算：水平偏差3.2cm（<10cm✓），航向偏差1.5°（<5°✓）",
                        "评估结论：落点偏差满足精度要求"
                    ],
                    "knowledge_trace": "实际坐标测量 → 目标坐标比对 → 偏差计算 → 精度评估。"
                },
                "function_status_check": {
                    "title": "功能状态检查",
                    "summary": "检查设备通电、通信与传感器工作状态，验证功能完整性。",
                    "key_points": [
                        "通电状态：电源指示灯绿色常亮，电量>90%，电压12.1V正常",
                        "通信链路：4G信号-72dBm，心跳包正常，延迟<200ms",
                        "传感器自检：所有传感器工作正常，自检通过"
                    ],
                    "knowledge_trace": "通电检测 → 通信验证 → 传感器自检 → 功能状态汇总。"
                },
                "deployment_success_judgment": {
                    "title": "投放成功判定",
                    "summary": "综合各项指标，判定投放结果为成功、失败或需重投。",
                    "key_points": [
                        "判定标准：位置偏差<10cm、航向偏差<5°、通电正常、通信正常、传感器自检通过",
                        "本次结果：所有标准均满足，判定为【成功】",
                        "重投策略：若失败，分析原因→调整参数→切换备用点→重新投放"
                    ],
                    "knowledge_trace": "各项指标评估 → 标准比对 → 最终判定 → 结果上报/重投决策。"
                }
            }
        },
    ),
    Scenario(
        id="equipment_precision_location",  # 6. 高精度目标定位
        model_name="设备投放",
        name="高精度目标定位",
        example_input="向X区域精确投放设备传感器Y",
        reasoning_chain="环境解析（读取地图、地物特征、遮挡信息）→ 传感器融合定位（无人机视觉、激光雷达、深度感知等多源数据融合）→ 误差纠正（基于航迹、风场、地面标志物进行偏差修正）→ 定位结果生成（输出目标区域精确坐标）",
        prompt=(
            "【设备投放-高精度目标定位专项要求】\n"
            "1. 行为树必须包含：task_ingest（任务接收）→ environment_analysis（读取地图、地物特征、遮挡信息）→ "
            "sensor_fusion（多源数据融合：视觉、激光雷达、深度感知）→ "
            "error_correction（基于航迹、风场、地面标志物进行偏差修正）→ "
            "location_result（输出精确坐标，包含 knowledge_graph）。\n"
            "2. location_result 的 knowledge_graph 应体现完整推理链：环境解析 → 多源传感器融合 → 误差纠正 → 精确坐标输出。"
        ),
        example_output={
            "default_focus": "location_result",
            "behavior_tree": {
                "id": "task_ingest",
                "label": "📋 任务接收",
                "status": "completed",
                "summary": "接收精确投放传感器Y至X区域的任务，解析投放精度要求。",
                "children": [
                    {
                        "id": "precision_location_sequence",
                        "label": "🎯 高精度目标定位",
                        "status": "active",
                        "summary": "通过多源传感器融合与误差纠正，实现目标点的高精度定位。",
                        "children": [
                            {
                                "id": "environment_analysis",
                                "label": "🗺️ 环境解析",
                                "status": "completed",
                                "summary": "读取X区域的地图、地物特征与遮挡情况，圈定可能的目标投放区域。",
                                "children": []
                            },
                            {
                                "id": "sensor_fusion",
                                "label": "📡 传感器融合定位",
                                "status": "completed",
                                "summary": "融合无人机视觉、激光雷达与深度感知数据，对预设标记进行识别与空间定位。",
                                "children": []
                            },
                            {
                                "id": "error_correction",
                                "label": "🔧 误差纠正",
                                "status": "completed",
                                "summary": "利用航迹、风场模型和地面标志物对初始定位结果进行偏差修正。",
                                "children": []
                            },
                            {
                                "id": "location_result",
                                "label": "✅ 定位结果生成",
                                "status": "active",
                                "summary": "输出目标区域的精确坐标（WGS84），附带精度评估指标，用于后续投放控制。",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            "node_insights": {
                "task_ingest": {
                    "title": "任务接收",
                    "summary": "接收并解析精确投放任务，明确传感器Y的投放目标区域X及精度要求。",
                    "key_points": [
                        "解析任务描述中的目标区域X和待投放设备Y",
                        "提取投放精度要求（如±1米、±5米等）",
                        "确认无人机平台的传感器配置与定位能力"
                    ],
                    "knowledge_trace": "任务文本 → 关键要素提取 → 精度需求明确 → 传感器能力匹配。"
                },
                "precision_location_sequence": {
                    "title": "高精度目标定位序列",
                    "summary": "通过环境解析、多源融合、误差纠正的顺序流程，实现目标点的高精度定位。",
                    "key_points": [
                        "分步骤执行：环境感知 → 多源融合 → 误差校正 → 结果输出",
                        "各步骤相互依赖，后续步骤基于前序结果进行优化",
                        "确保定位精度满足投放任务要求"
                    ],
                    "knowledge_trace": "顺序执行定位流程 → 逐步提升定位精度 → 输出可靠坐标。"
                },
                "environment_analysis": {
                    "title": "环境解析",
                    "summary": "通过地图与感知数据，识别X区域的关键地物、遮挡物和候选目标区域。",
                    "key_points": [
                        "从电子地图中提取道路、建筑物、水体等基础地物特征",
                        "结合任务预设标记的大致位置缩小搜索范围",
                        "识别高遮挡区域（树木、建筑物阴影），为传感器视角规划提供参考",
                        "评估地形起伏与可达性，排除不适合投放的区域"
                    ],
                    "knowledge_trace": "地图与先验信息 → 地物特征提取 → 遮挡分析 → 候选目标区域圈定。"
                },
                "sensor_fusion": {
                    "title": "传感器融合定位",
                    "summary": "利用视觉、激光雷达与深度传感器联合识别预设标记，并估算其空间位置。",
                    "key_points": [
                        "视觉模块检测地面或建筑表面的预设标记图案（如二维码、特征标志物）",
                        "激光雷达提供三维点云以刻画空间结构和障碍物位置",
                        "深度感知补充距离信息，提升目标位置估计的精度",
                        "采用卡尔曼滤波或粒子滤波进行多源数据融合"
                    ],
                    "knowledge_trace": "多源数据采集 → 时空对齐 → 特征级或决策级融合 → 输出目标的初始空间位置估计。"
                },
                "error_correction": {
                    "title": "误差纠正",
                    "summary": "结合无人机航迹、风场估计与地面标志物位置，修正初始定位误差。",
                    "key_points": [
                        "利用历史航迹和IMU/GNSS数据对定位漂移进行估计与补偿",
                        "将风场对无人机姿态与轨迹的影响纳入误差模型",
                        "使用已知坐标的地面标志物（如GPS基站、预设信标）进行绝对坐标对齐",
                        "基于多次观测进行统计滤波，降低随机误差"
                    ],
                    "knowledge_trace": "初始定位结果 → 引入航迹与风场模型 → 与地面标志物对齐 → 统计滤波 → 得到修正后坐标。"
                },
                "location_result": {
                    "title": "定位结果生成",
                    "summary": "在误差纠正后的基础上，输出可用于后续投放任务的目标区域精确坐标与精度指标。",
                    "key_points": [
                        "将修正后的目标位置转换为统一坐标系（如WGS84或本地平面坐标系）",
                        "附带定位精度评估指标（如误差椭圆、置信区间、CEP值）",
                        "为投放控制系统提供标准化接口（JSON格式：坐标、精度、时间戳）",
                        "记录定位过程的关键参数（传感器状态、融合权重、修正量）供审计使用"
                    ],
                    "knowledge_trace": "修正后空间位置 → 坐标系转换与精度评估 → 输出标准化定位结果。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "env_analysis",
                                "label": "环境解析\n(地图+地物+遮挡)", "type": "input"},
                            {"id": "sensor_fusion",
                                "label": "多源传感器融合\n(视觉+激光雷达+深度)", "type": "process"},
                            {"id": "error_correction",
                                "label": "误差纠正\n(航迹+风场+标志物)", "type": "process"},
                            {"id": "coord_output",
                                "label": "精确坐标输出\n(WGS84+精度指标)", "type": "output"}
                        ],
                        "edges": [
                            {"source": "env_analysis", "target": "sensor_fusion"},
                            {"source": "sensor_fusion",
                                "target": "error_correction"},
                            {"source": "error_correction",
                                "target": "coord_output"}
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
        example_input="将设备Y通过无人车投放至X点，并由机械臂自主卸载",
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
        id="equipment_delivery_confirmation",  # 8. 投放确认
        model_name="设备投放",
        name="投放确认",
        example_input="将侦察节点Y投放至X点并确认部署成功",
        reasoning_chain="结果感知（投放后图像、姿态信息、设备回传信号）→ 落点偏差分析（比较实际坐标与目标坐标）→ 功能状态检查（是否正常通电、是否建立通信链路）→ 投放成功判定（成功/失败/需重投）",
        prompt=(
            "【设备投放-投放确认专项要求】\n"
            "1. 行为树必须包含：task_ingest（任务接收）→ deployment_confirmation_sequence（投放确认序列）：\n"
            "   - result_perception（投放后图像、姿态信息、设备回传信号）\n"
            "   - deviation_analysis（比较实际坐标与目标坐标）\n"
            "   - function_check（检查通电、通信链路状态）\n"
            "   - deployment_judgment（判定成功/失败/需重投，包含 knowledge_graph）\n"
            "2. deployment_judgment 的 knowledge_graph 应体现完整推理链：结果感知 → 落点偏差分析 → 功能状态检查 → 投放成功判定。"
        ),
        example_output={
            "default_focus": "deployment_judgment",
            "behavior_tree": {
                "id": "task_ingest",
                "label": "📋 任务接收",
                "status": "completed",
                "summary": "接收侦察节点Y投放至X点并确认部署成功的任务，解析确认要求与成功标准。",
                "children": [
                    {
                        "id": "deployment_confirmation_sequence",
                        "label": "✅ 投放确认序列",
                        "status": "active",
                        "summary": "通过多维度感知、偏差分析与功能检测，完成投放结果的自动确认。",
                        "children": [
                            {
                                "id": "result_perception",
                                "label": "📷 结果感知",
                                "status": "completed",
                                "summary": "采集投放后图像、姿态信息与设备回传信号，建立投放结果的感知基础。",
                                "children": []
                            },
                            {
                                "id": "deviation_analysis",
                                "label": "📐 落点偏差分析",
                                "status": "completed",
                                "summary": "将实际落点坐标与目标X点坐标对比，评估空间偏差是否在容差范围内。",
                                "children": []
                            },
                            {
                                "id": "function_check",
                                "label": "🔌 功能状态检查",
                                "status": "completed",
                                "summary": "检查侦察节点Y是否正常通电、建立通信链路并处于预期工作模式。",
                                "children": []
                            },
                            {
                                "id": "deployment_judgment",
                                "label": "✅ 投放成功判定",
                                "status": "active",
                                "summary": "综合落点偏差与功能状态，判定投放结果为成功/失败/需重投，并给出决策理由。",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            "node_insights": {
                "task_ingest": {
                    "title": "任务接收",
                    "summary": "接收并解析投放确认任务，明确侦察节点Y、目标点X及部署成功的判定标准。",
                    "key_points": [
                        "解析任务描述：待投放设备为侦察节点Y，目标点为X",
                        "提取确认要求：落点偏差容差、通电状态、通信链路建立",
                        "明确判定标准：成功（偏差在容差内+功能正常）、失败（严重偏差或功能受损）、需重投（可修复或轻微偏差）"
                    ],
                    "knowledge_trace": "任务文本 → 关键要素提取 → 确认标准明确 → 后续感知与判定准备。"
                },
                "deployment_confirmation_sequence": {
                    "title": "投放确认序列",
                    "summary": "通过结果感知、偏差分析、功能检查的顺序流程，实现投放结果的自动化确认。",
                    "key_points": [
                        "分步骤执行：感知采集 → 偏差评估 → 功能检测 → 综合判定",
                        "各步骤相互支撑，共同形成投放结果的多维度评估",
                        "确保判定依据充分、结论可靠、可追溯"
                    ],
                    "knowledge_trace": "顺序执行确认流程 → 汇总多维度证据 → 输出可靠判定结论。"
                },
                "result_perception": {
                    "title": "结果感知",
                    "summary": "通过机载和地面传感器获取设备投放后的图像、姿态与通信状态，建立投放结果的感知基础。",
                    "key_points": [
                        "图像采集：使用无人机或地面摄像头获取设备落点的全景或多角度图像",
                        "姿态感知：通过惯导或姿态传感器估计设备姿态（俯仰、横滚、偏航角），判断是否倾倒或倾斜",
                        "信号回传：监听设备的心跳信号、状态码与初始化信息，确认设备是否上线",
                        "环境感知：识别落点周边障碍物、地形坡度等环境因素"
                    ],
                    "knowledge_trace": "传感器触发 → 图像/姿态/信号数据采集 → 数据预处理与对齐 → 形成可用于分析的投放结果数据集。"
                },
                "deviation_analysis": {
                    "title": "落点偏差分析",
                    "summary": "将设备实际落点坐标与任务规划的目标X点坐标进行对比，评估偏差是否在可接受范围内。",
                    "key_points": [
                        "位置反算：基于图像识别、GPS或视觉定位技术估算设备在地图坐标系中的实际位置",
                        "偏差计算：计算实际落点与目标X点之间的水平偏差（欧氏距离或沿东北向分量）和高度差",
                        "容差比对：将偏差值与任务容差阈值（如水平±5m，高度±2m）进行比较",
                        "偏差分级：给出\"在容差内/接近容差/超出容差\"的分级结论，供后续判定使用"
                    ],
                    "knowledge_trace": "感知数据 → 实际位置反算 → 与目标坐标对比 → 偏差量化与分级标记。"
                },
                "function_check": {
                    "title": "功能状态检查",
                    "summary": "检查侦察节点Y是否正常通电、建立通信链路并在预期模式下运行。",
                    "key_points": [
                        "电源检查：确认设备电源状态（开机/关机）、电量水平（百分比）、供电稳定性",
                        "通信链路：验证与指挥端、中继节点或卫星的通信链路是否建立，测试信号强度与延迟",
                        "功能模块自检：检查关键模块（传感器、计算单元、通信模块）是否通过上电自检（POST）",
                        "工作模式确认：确认设备是否进入预期的工作模式（如侦察、待机、数据采集）",
                        "异常告警：记录并上报任何功能异常、告警或故障代码"
                    ],
                    "knowledge_trace": "设备状态采集 → 电源/通信/功能模块逐项检查 → 形成\"可用/受限/不可用\"的功能结论。"
                },
                "deployment_judgment": {
                    "title": "投放成功判定",
                    "summary": "综合落点偏差结果与功能状态，判断本次投放是否成功，如失败则给出是否需要重投的建议。",
                    "key_points": [
                        "成功判定：落点偏差在容差范围内 且 设备功能完好 且 通信链路稳定 → 标记为\"投放成功\"",
                        "失败判定：落点偏差严重超出容差 或 设备功能严重受损/无法通信 → 标记为\"投放失败\"",
                        "重投建议：轻微偏差（接近容差边界）或 部分功能受限但可补救 → 标记为\"需重投/建议人工介入\"",
                        "决策依据：记录偏差值、功能检查结果、判定规则与最终结论，形成可追溯的判定报告",
                        "后续动作：成功则进入下一任务，失败则触发重投流程或告警通知"
                    ],
                    "knowledge_trace": "落点偏差分析结果 + 功能状态检查结果 → 规则引擎或决策模型推理 → 输出成功/失败/需重投的判定及详细理由。",
                    "knowledge_graph": {
                        "nodes": [
                            {"id": "result_perception",
                                "label": "结果感知", "type": "input"},
                            {"id": "deviation_analysis",
                                "label": "落点偏差分析", "type": "process"},
                            {"id": "function_check",
                                "label": "功能状态检查", "type": "process"},
                            {"id": "deployment_judgment",
                                "label": "投放成功判定", "type": "output"}
                        ],
                        "edges": [
                            {"source": "result_perception",
                                "target": "deviation_analysis"},
                            {"source": "result_perception",
                                "target": "function_check"},
                            {"source": "deviation_analysis",
                                "target": "deployment_judgment"},
                            {"source": "function_check",
                                "target": "deployment_judgment"}
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
                            {"id": "ground_state",
                                "label": "地面状态识别结果", "type": "input"},
                            {"id": "env_factors", "label": "环境因素分析结果", "type": "input"},
                            {"id": "landing_risk", "label": "降落风险评估",
                                "type": "process"},
                            {"id": "landing_strategy",
                                "label": "投放策略生成", "type": "decision"},
                            {"id": "safety_level",
                                "label": "投放点安全等级与建议", "type": "output"}
                        ],
                        "edges": [
                            {"source": "ground_state", "target": "landing_risk"},
                            {"source": "env_factors", "target": "landing_risk"},
                            {"source": "landing_risk", "target": "landing_strategy"},
                            {"source": "landing_strategy",
                                "target": "safety_level"}
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
                            {"id": "drop_monitoring",
                                "label": "投放动作监测数据", "type": "input"},
                            {"id": "anomaly_pattern",
                                "label": "异常模式识别结果", "type": "process"},
                            {"id": "risk_level", "label": "风险等级判断", "type": "process"},
                            {"id": "emergency_strategy",
                                "label": "应急策略生成", "type": "decision"},
                            {"id": "execution_result",
                                "label": "执行结果与流程恢复状态", "type": "output"}
                        ],
                        "edges": [
                            {"source": "drop_monitoring",
                                "target": "anomaly_pattern"},
                            {"source": "anomaly_pattern", "target": "risk_level"},
                            {"source": "risk_level", "target": "emergency_strategy"},
                            {"source": "emergency_strategy",
                                "target": "execution_result"}
                        ]
                    }
                }
            }
        },
    ),
    Scenario(
        id="equipment_task_formation",  # 任务编组
        model_name="设备投放",
        name="任务编组",
        example_input="（85,20）向前沿区域X（210,145）投放设备资源Y，在确保安全的前提下完成部署，给出对应的任务编组。",
        reasoning_chain="任务解析（物资类型、重量与体积、投放精度需求、环境风险）→ 设备匹配（匹配适用的无人车类型）→ 数量推断（根据载荷能力与冗余策略推算所需设备数量）→ 投放方式生成（决定投放方式）",
        prompt=(
            "【设备投放-任务编组专项要求】\n"
            "1. 行为树必须至少包含以下核心节点，严格按照推理链条自上而下展开：\n"
            "   - task_analysis（任务解析）：解析物资类型（设备资源Y）、重量与体积、投放精度需求、环境风险；\n"
            "   - equipment_matching（设备匹配）：匹配适用的无人车类型（机器狗/六轮越野无人车），说明选择理由；\n"
            "   - quantity_inference（数量推断）：根据载荷能力与冗余策略推算所需设备数量；\n"
            "   - delivery_method_generation（投放方式生成）：决定投放方式（地面配送、自主装卸、协同投放）；\n"
            "   - formation_summary（编组节点汇总，核心节点）：汇总编组方案，必须包含 knowledge_graph 字段。\n"
            "2. formation_summary 节点的 knowledge_graph 必须体现：任务解析 → 设备匹配 → 数量推断 → 投放方式生成 → 编组方案输出。\n"
            "3. knowledge_graph 中必须包含至少8个节点，包括主推理链节点和辅助细节节点（如地形数据、设备库存状态、任务优先级、气象条件等）。\n"
            "4. 在 node_insights 中，所有节点的 knowledge_trace 必须体现完整推理路径。"
        ),
        example_output={
            "default_focus": "formation_summary",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "📦 任务解析：投放任务编组",
                "status": "completed",
                "summary": "解析从(85,20)向前沿区域X(210,145)投放设备资源Y的任务，明确物资类型、重量体积、投放精度需求与环境风险。",
                "children": [
                    {
                        "id": "equipment_matching",
                        "label": "🚗 设备匹配：六轮越野无人车+机器狗",
                        "status": "completed",
                        "summary": "基于运输距离约156km、地形复杂度与设备特性，选择2辆六轮越野无人车（主力运输）+1只机器狗（精确定位辅助）。",
                        "children": []
                    },
                    {
                        "id": "quantity_inference",
                        "label": "🔢 数量推断：2辆无人车+1只机器狗",
                        "status": "completed",
                        "summary": "设备资源Y单套重量约30kg，单车载重能力80kg，考虑安全余量（载重利用率70%），每车携带1套设备。配置1只机器狗用于精确定位。",
                        "children": []
                    },
                    {
                        "id": "delivery_method_generation",
                        "label": "📍 投放方式生成：地面配送+自主装卸",
                        "status": "completed",
                        "summary": "基于平整地面环境与精度要求，选择地面配送+自主装卸方式。无人车到达投放点后，通过车载机械臂自主完成设备卸载。",
                        "children": []
                    },
                    {
                        "id": "formation_summary",
                        "label": "✅ 编组节点汇总",
                        "status": "active",
                        "summary": "形成由2辆六轮越野无人车（主力运输）+1只机器狗（定位辅助）构成的投放编组，明确各自职责与协同方式。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务解析",
                    "summary": "从任务文本中提取起点(85,20)、目标区域X(210,145)、设备资源Y等关键要素，为编组决策提供输入。",
                    "key_points": [
                        "起点坐标(85,20)，目标区域X坐标(210,145)，直线距离约156km",
                        "设备资源Y需要投放，需确定具体数量、重量与体积特性",
                        "安全要求：在确保安全的前提下完成部署",
                        "为后续设备匹配与数量推断提供约束条件"
                    ],
                    "knowledge_trace": "任务文本 → 坐标/距离/设备/安全要素提取 → 形成任务约束条件 → 为编组决策提供输入。"
                },
                "equipment_matching": {
                    "title": "设备匹配",
                    "summary": "基于任务距离、地形特点与设备特性，选择适用的无人车类型与辅助设备。",
                    "key_points": [
                        "运输距离156km，需选择续航能力强的无人车平台",
                        "六轮越野无人车：最高时速60km/h，续航150km，载重80kg，适合长距离运输",
                        "机器狗：四足行走适应复杂地形，搭载高精度传感器用于目标定位",
                        "选择理由：六轮设计提供稳定运输能力，机器狗实现精确定位"
                    ],
                    "knowledge_trace": "运输距离+地形约束 → 平台能力分析 → 选择六轮越野无人车（运输）+ 机器狗（定位）组合。"
                },
                "quantity_inference": {
                    "title": "数量推断",
                    "summary": "依据设备重量体积与单车载荷，叠加冗余策略，推算所需无人车与机器狗数量。",
                    "key_points": [
                        "设备资源Y假设单套重量约30kg，体积40×30×25cm",
                        "单车有效载荷：80kg×70%=56kg（考虑安全余量）",
                        "运输需求：假设需要2套设备（共60kg），需2辆无人车（各携带1套）",
                        "配置1只机器狗用于精确定位与辅助作业"
                    ],
                    "knowledge_trace": "设备总载荷计算 → 单车有效载荷评估 → 理论数量计算 → 冗余策略叠加 → 最终编组数量。"
                },
                "delivery_method_generation": {
                    "title": "投放方式生成",
                    "summary": "在平整地面投放环境下，生成地面配送+自主装卸的投放方式。",
                    "key_points": [
                        "地面配送：无人车直接将设备运输至投放点附近",
                        "自主装卸：车载机械臂自主完成设备卸载与精确放置",
                        "协同投放：机器狗提供精确定位引导，无人车执行放置动作",
                        "选择理由：平整地面条件良好，自主装卸可实现高精度投放"
                    ],
                    "knowledge_trace": "环境条件评估 → 候选投放方式分析 → 精度需求匹配 → 生成投放方式决策。"
                },
                "formation_summary": {
                    "title": "编组节点汇总",
                    "summary": "将任务解析、设备匹配、数量推断和投放方式的结论汇总为可执行的编组方案。",
                    "key_points": [
                        "编组构成：2辆六轮越野无人车（主力运输）+1只机器狗（定位辅助）",
                        "任务分工：无人车负责设备运输与自主装卸，机器狗负责精确定位与引导",
                        "协同方式：机器狗先行进行目标定位→无人车到位→自主装卸→投放确认",
                        "输出：完整的投放编组方案，包含设备类型、数量与协同策略"
                    ],
                    "knowledge_trace": "任务要素 → 设备匹配 → 数量与方式推断 → 汇总为编组方案。",
                    "knowledge_graph": {
                        "nodes": [
                            # 主推理链节点（5个）
                            {"id": "task_parsing", "label": "任务解析", "type": "input"},
                            {"id": "equipment_matching", "label": "设备匹配", "type": "process"},
                            {"id": "quantity_inference", "label": "数量推断", "type": "process"},
                            {"id": "delivery_method", "label": "投放方式生成", "type": "decision"},
                            {"id": "formation_output", "label": "编组方案输出", "type": "output"},
                            
                            # 辅助细节节点（4个）
                            {"id": "terrain_data", "label": "地形数据", "type": "input"},
                            {"id": "equipment_inventory", "label": "设备库存状态", "type": "input"},
                            {"id": "mission_priority", "label": "任务优先级", "type": "input"},
                            {"id": "weather_condition", "label": "气象条件", "type": "input"}
                        ],
                        "edges": [
                            # 主推理链连接
                            {"source": "task_parsing", "target": "equipment_matching"},
                            {"source": "equipment_matching", "target": "quantity_inference"},
                            {"source": "quantity_inference", "target": "delivery_method"},
                            {"source": "delivery_method", "target": "formation_output"},
                            
                            # 辅助节点的单向连接
                            {"source": "terrain_data", "target": "equipment_matching"},
                            {"source": "equipment_inventory", "target": "quantity_inference"},
                            {"source": "weather_condition", "target": "delivery_method"}
                            
                            # 注意：mission_priority 独立存在，不连接到主链
                        ]
                    }
                }
            }
        },
    )
]