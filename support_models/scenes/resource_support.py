from typing import List
from .schema import Scenario

# 五、资源保障支援模型测试
SCENARIOS: List[Scenario] = [
        # 五、资源保障支援模型测试 - 综合策略场景
    Scenario(
        id="resource_support_strategy",  # 资源保障策略（综合场景）
        model_name="资源保障",
        name="资源保障策略",
        example_input="监控当前所有前线单位的物资状态，为A、B、C三个小队分配现有急救物资，对X区域缺乏医疗物资生成补给任务并安排运输，预测未来72小时内X作业区的燃料需求",
        reasoning_chain="任务解析（资源类型、需求单位、时限要求）→ 资源评估（资源类别解析、追踪方式匹配、状态更新机制、异常识别）→ 需求分配建议（需求解析、库存计算、分配策略推理、分配方案生成）→ 补给任务生成与调度（短缺资源识别、补给任务构建、运输与调度规划、任务执行检测）→ 资源消耗预测与规划（历史数据分析、环境与任务强度建模、消耗量预测、储备规划与建议）",
        prompt=(
            "【资源保障-资源保障策略专项要求】\n"
            "1. 行为树必须至少包含以下核心节点，严格按照推理链条自上而下展开：\n"
            "   - task_analysis（任务解析）：解析资源类型（急救物资、医疗物资、燃料等）、需求单位（小队A/B/C、X区域）、时限要求（72小时）；\n"
            "   - resource_assessment（资源评估，核心节点）：必须包含以下子节点：\n"
            "       * resource_category_parsing（资源类别解析）：解析食物、燃料、备件等类别；\n"
            "       * tracking_method_matching（追踪方式匹配）：匹配RFID、二维码、GPS、无人机盘点；\n"
            "       * status_update_mechanism（状态更新机制）：更新位置、数量、消耗速率；\n"
            "       * anomaly_identification（异常识别）：识别资源丢失、库存异常、传感器失联；\n"
            "       必须包含 knowledge_graph 字段。\n"
            "   - demand_allocation_advice（需求分配建议，核心节点）：必须包含以下子节点：\n"
            "       * demand_parsing（需求解析）：解析数量、紧急度、使用场景；\n"
            "       * inventory_calculation（库存与可用量计算）：计算各类资源的可用量；\n"
            "       * allocation_strategy_reasoning（分配策略推理）：优先级分级、需求满足度、运输成本；\n"
            "       * allocation_plan_generation（分配方案生成）：建议分配比例与对应理由；\n"
            "       必须包含 knowledge_graph 字段。\n"
            "   - supply_task_generation（补给任务生成与调度，核心节点）：必须包含以下子节点：\n"
            "       * shortage_resource_identification（短缺资源识别）：消耗异常、低库存预警；\n"
            "       * supply_task_construction（补给任务构建）：物资清单、目标位置、时限要求；\n"
            "       * transport_scheduling_planning（运输与调度规划）：车辆匹配、路线规划、补给顺序；\n"
            "       * task_execution_monitoring（任务执行检测与回传）：补给确认、状态更新；\n"
            "       必须包含 knowledge_graph 字段。\n"
            "   - resource_consumption_prediction（资源消耗预测与规划，核心节点）：必须包含以下子节点：\n"
            "       * historical_data_analysis（历史数据分析）：消耗模式、任务类型；\n"
            "       * environment_task_modeling（环境与任务强度建模）：温度、地形、操作负载；\n"
            "       * consumption_prediction（消耗量预测）：短期/中期预测曲线；\n"
            "       * reserve_planning_advice（储备规划与建议）：最小库存量、安全冗余、补给周期；\n"
            "       必须包含 knowledge_graph 字段。\n"
            "2. resource_assessment 节点的 knowledge_graph 必须体现：资源类别解析 → 追踪方式匹配 → 状态更新机制 → 异常识别。\n"
            "3. demand_allocation_advice 节点的 knowledge_graph 必须体现：需求解析 → 库存计算 → 分配策略推理 → 分配方案生成。\n"
            "4. supply_task_generation 节点的 knowledge_graph 必须体现：短缺资源识别 → 补给任务构建 → 运输与调度规划 → 任务执行检测。\n"
            "5. resource_consumption_prediction 节点的 knowledge_graph 必须体现：历史数据分析 → 环境与任务强度建模 → 消耗量预测 → 储备规划与建议。\n"
            "6. 在 node_insights 中，所有节点的 knowledge_trace 必须体现完整推理路径。"
        ),
        example_output={
            "default_focus": "resource_support_strategy",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "📋 任务解析：资源保障综合任务",
                "status": "completed",
                "summary": "解析包含资源监控、需求分配、补给调度与消耗预测的综合资源保障任务，涉及前线单位物资状态监控、A/B/C三个小队急救物资分配、X区域医疗物资补给及72小时燃料需求预测。",
                "children": [
                    {
                        "id": "resource_support_strategy",
                        "label": "🎯 资源保障策略",
                        "status": "active",
                        "summary": "生成包含资源评估、需求分配、补给调度与消耗预测的完整资源保障策略，确保前线单位物资充足、分配合理、补给及时。",
                        "children": [
                            {
                                "id": "resource_assessment",
                                "label": "📦 资源评估",
                                "status": "completed",
                                "summary": "对各类资源（物资、装备、燃料、备件等）进行实时位置与数量追踪，并在状态变化时保持同步更新。",
                                "children": [
                                    {
                                        "id": "resource_category_parsing",
                                        "label": "🏷️ 资源类别解析",
                                        "status": "completed",
                                        "summary": "解析食物、燃料、备件等资源类别，建立统一的资源分类体系。",
                                        "children": [
                                            {
                                                "id": "food_category",
                                                "label": "🍱 食物类别",
                                "status": "completed",
                                "summary": "分类记录食物资源的种类、批次、保质期及分发情况。",
                                "children": []
                            },
                            {
                                                "id": "fuel_category",
                                                "label": "⛽ 燃料类别",
                                                "status": "completed",
                                                "summary": "登记各类型燃料（汽油、柴油等）仓储与消耗状况。",
                                                "children": []
                                            },
                                            {
                                                "id": "spare_parts_category",
                                                "label": "🔧 备件类别",
                                                "status": "completed",
                                                "summary": "建立备件库，明细备件用途、型号和配发情况。",
                                                "children": []
                                            },
                                            {
                                                "id": "medical_supplies_category",
                                                "label": "💊 医疗物资类别",
                                                "status": "completed",
                                                "summary": "分类记录急救包、药品、医疗器械等医疗物资。",
                                                "children": []
                                            }
                                        ]
                                    },
                                    {
                                        "id": "tracking_method_matching",
                                        "label": "📡 追踪方式匹配",
                                        "status": "completed",
                                        "summary": "为不同资源类别匹配合适的追踪手段（RFID、二维码、GPS、无人机盘点）。",
                                        "children": [
                                            {
                                                "id": "rfid_tracking",
                                                "label": "📱 RFID追踪",
                                                "status": "completed",
                                                "summary": "对高价值资源使用RFID标签进行实时追踪，读取距离3-5m，精度高。",
                                                "children": []
                                            },
                                            {
                                                "id": "qrcode_tracking",
                                                "label": "📷 二维码追踪",
                                                "status": "completed",
                                                "summary": "对大宗低价值物资采用二维码标记，扫描记录出入库信息。",
                                                "children": []
                                            },
                                            {
                                                "id": "gps_tracking",
                                                "label": "🛰️ GPS追踪",
                                                "status": "completed",
                                                "summary": "对运输车辆与移动仓库使用GPS追踪，实时更新位置信息。",
                                                "children": []
                                            },
                                            {
                                                "id": "drone_inventory",
                                                "label": "🚁 无人机盘点",
                                                "status": "completed",
                                                "summary": "使用无人机对分散物资进行空中盘点，视觉识别与计数。",
                                                "children": []
                                            }
                                        ]
                                    },
                                    {
                                        "id": "status_update_mechanism",
                                        "label": "🔄 状态更新机制",
                                        "status": "completed",
                                        "summary": "实时更新资源的位置、数量、消耗速率等状态信息。",
                                        "children": [
                                            {
                                                "id": "location_update",
                                                "label": "📍 位置更新",
                                                "status": "completed",
                                                "summary": "基于GPS/RFID读取结果更新资源实时位置。",
                                                "children": []
                                            },
                                            {
                                                "id": "quantity_update",
                                                "label": "📊 数量更新",
                                                "status": "completed",
                                                "summary": "根据出入库记录与盘点结果更新库存数量。",
                                                "children": []
                                            },
                                            {
                                                "id": "consumption_rate_tracking",
                                                "label": "📈 消耗速率追踪",
                                                "status": "completed",
                                                "summary": "分析历史消耗数据，计算各类资源的实时消耗速率。",
                                                "children": []
                                            }
                                        ]
                                    },
                                    {
                                        "id": "anomaly_identification",
                                        "label": "⚠️ 异常识别",
                                        "status": "completed",
                                        "summary": "识别资源丢失、库存异常、传感器失联等异常情况。",
                                        "children": [
                                            {
                                                "id": "resource_loss_detection",
                                                "label": "🚨 资源丢失检测",
                                                "status": "completed",
                                                "summary": "当RFID/GPS信号长时间未更新时判定为资源丢失。",
                                                "children": []
                                            },
                                            {
                                                "id": "inventory_anomaly_detection",
                                                "label": "📉 库存异常检测",
                                                "status": "completed",
                                                "summary": "账面数量与实际盘点结果差异超过阈值时标记为库存异常。",
                                                "children": []
                                            },
                                            {
                                                "id": "sensor_disconnect_detection",
                                                "label": "🔌 传感器失联检测",
                                "status": "completed",
                                                "summary": "监控追踪设备心跳信号，超时未响应则判定为传感器失联。",
                                "children": []
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "id": "demand_allocation_advice",
                                "label": "🎯 需求分配建议",
                                "status": "completed",
                                "summary": "基于任务优先级、可用资源和紧急程度，自动生成多单位间的最优资源分配建议。",
                                "children": [
                                    {
                                        "id": "demand_parsing",
                                        "label": "📋 需求解析",
                                        "status": "completed",
                                        "summary": "解析A/B/C三个小队对急救物资的数量、紧急度与使用场景需求。",
                                        "children": [
                                            {
                                                "id": "quantity_demand",
                                                "label": "🔢 数量需求",
                                                "status": "completed",
                                                "summary": "提取各小队需要的急救物资具体数量（急救包、绷带、止血药等）。",
                                                "children": []
                                            },
                                            {
                                                "id": "urgency_assessment",
                                                "label": "⏰ 紧急度评估",
                                                "status": "completed",
                                                "summary": "根据任务类型（进攻/防御/救援）与危险程度评估需求紧急度。",
                                                "children": []
                                            },
                                            {
                                                "id": "usage_scenario_analysis",
                                                "label": "🎭 使用场景分析",
                                                "status": "completed",
                                                "summary": "分析各小队的作战环境与可能遭遇的伤亡情况。",
                                                "children": []
                                            }
                                        ]
                                    },
                                    {
                                        "id": "inventory_calculation",
                                        "label": "📊 库存与可用量计算",
                                        "status": "completed",
                                        "summary": "统计当前中央与各前线仓的库存，计算可下发的可用量。",
                                        "children": [
                                            {
                                                "id": "total_inventory_check",
                                                "label": "🏪 总库存查询",
                                                "status": "completed",
                                                "summary": "查询所有仓库的急救物资总库存量。",
                                                "children": []
                                            },
                                            {
                                                "id": "locked_resource_deduction",
                                                "label": "🔒 锁定资源扣除",
                                                "status": "completed",
                                                "summary": "扣除已分配给其他任务的锁定资源。",
                                                "children": []
                                            },
                                            {
                                                "id": "available_resource_calculation",
                                                "label": "✅ 可用资源计算",
                                                "status": "completed",
                                                "summary": "计算可用于本次分配的净可用量，考虑保质期、损坏品等约束。",
                                                "children": []
                                            }
                                        ]
                                    },
                                    {
                                        "id": "allocation_strategy_reasoning",
                                        "label": "🧠 分配策略推理",
                                        "status": "completed",
                                        "summary": "综合优先级分级、需求满足度与运输成本推导分配策略。",
                                        "children": [
                                            {
                                                "id": "priority_ranking",
                                                "label": "🏆 优先级排序",
                                                "status": "completed",
                                                "summary": "根据任务紧急度与伤亡风险对A/B/C小队进行优先级排序。",
                                                "children": []
                                            },
                                            {
                                                "id": "satisfaction_optimization",
                                                "label": "📈 满足度优化",
                                                "status": "completed",
                                                "summary": "在资源有限情况下，优化整体需求满足度。",
                                                "children": []
                                            },
                                            {
                                                "id": "transport_cost_consideration",
                                                "label": "🚚 运输成本考量",
                                                "status": "completed",
                                                "summary": "在多个满足方案中选择运输距离/时间成本更低的方案。",
                                "children": []
                            }
                        ]
                    },
                    {
                                        "id": "allocation_plan_generation",
                                        "label": "📝 分配方案生成",
                        "status": "completed",
                                        "summary": "生成具体的分配比例与对应理由，输出可执行的分配清单。",
                        "children": [
                            {
                                                "id": "squad_a_allocation",
                                                "label": "🅰️ 小队A分配",
                                                "status": "completed",
                                                "summary": "小队A分配急救包15个（占比40%），因任务紧急度最高。",
                                                "children": []
                                            },
                                            {
                                                "id": "squad_b_allocation",
                                                "label": "🅱️ 小队B分配",
                                                "status": "completed",
                                                "summary": "小队B分配急救包12个（占比32%），任务难度中等。",
                                                "children": []
                                            },
                                            {
                                                "id": "squad_c_allocation",
                                                "label": "🆑 小队C分配",
                                "status": "completed",
                                                "summary": "小队C分配急救包10个（占比28%），后勤距离最短。",
                                "children": []
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "id": "supply_task_generation",
                                "label": "🚛 补给任务生成与调度",
                                "status": "completed",
                                "summary": "基于实时资源短缺情况，自动生成补给任务，并推理出最佳补给路线、补给顺序与车辆安排。",
                                "children": [
                                    {
                                        "id": "shortage_resource_identification",
                                        "label": "🔍 短缺资源识别",
                                        "status": "completed",
                                        "summary": "识别X区域医疗物资的消耗异常与低库存预警。",
                                        "children": [
                                            {
                                                "id": "consumption_anomaly_detection",
                                                "label": "📉 消耗异常检测",
                                                "status": "completed",
                                                "summary": "分析X区域医疗物资消耗曲线，识别异常加速消耗段。",
                                                "children": []
                                            },
                                            {
                                                "id": "low_inventory_warning",
                                                "label": "⚠️ 低库存预警",
                                                "status": "completed",
                                                "summary": "当前库存低于安全阈值30%，触发补给预警。",
                                                "children": []
                                            },
                                            {
                                                "id": "shortage_gap_calculation",
                                                "label": "📊 缺口计算",
                                                "status": "completed",
                                                "summary": "计算未来24小时预计缺口量：急救包50个、止血药100支。",
                                                "children": []
                                            }
                                        ]
                                    },
                                    {
                                        "id": "supply_task_construction",
                                        "label": "📋 补给任务构建",
                                        "status": "completed",
                                        "summary": "根据缺口生成补给物资清单、目标位置X区域与时限要求。",
                                        "children": [
                                            {
                                                "id": "material_list_generation",
                                                "label": "📝 物资清单生成",
                                                "status": "completed",
                                                "summary": "生成详细补给清单：急救包50个、止血药100支、绷带200卷。",
                                                "children": []
                                            },
                                            {
                                                "id": "target_location_specification",
                                                "label": "📍 目标位置指定",
                                                "status": "completed",
                                                "summary": "补给目标位置X区域坐标(210,145)，接收单位为前线医疗站。",
                                                "children": []
                                            },
                                            {
                                                "id": "time_constraint_setting",
                                                "label": "⏱️ 时限要求设定",
                                                "status": "completed",
                                                "summary": "要求在6小时内完成补给，紧急度等级：高。",
                                                "children": []
                                            }
                                        ]
                                    },
                                    {
                                        "id": "transport_scheduling_planning",
                                        "label": "🚚 运输与调度规划",
                                        "status": "completed",
                                        "summary": "为补给任务匹配车辆、规划路线并确定补给顺序。",
                                        "children": [
                                            {
                                                "id": "vehicle_matching",
                                                "label": "🚗 车辆匹配",
                                                "status": "completed",
                                                "summary": "匹配2辆中型越野无人车（载重500kg），满足物资运输需求。",
                                                "children": []
                                            },
                                            {
                                                "id": "route_planning",
                                                "label": "🗺️ 路线规划",
                                                "status": "completed",
                                                "summary": "规划最优补给路线，距离120km，预计行驶3小时，规避危险区域。",
                                                "children": []
                                            },
                                            {
                                                "id": "supply_sequence_arrangement",
                                                "label": "📅 补给顺序安排",
                                                "status": "completed",
                                                "summary": "若存在多个补给点，按紧急度排序：X区域（高）→Y区域（中）。",
                                                "children": []
                                            }
                                        ]
                                    },
                                    {
                                        "id": "task_execution_monitoring",
                                        "label": "👁️ 任务执行检测与回传",
                                        "status": "completed",
                                        "summary": "监控补给任务执行情况，完成后确认并更新库存状态。",
                                        "children": [
                                            {
                                                "id": "vehicle_status_monitoring",
                                                "label": "🚗 车辆状态监控",
                                                "status": "completed",
                                                "summary": "实时监控补给车辆位置、速度与健康状态。",
                                                "children": []
                                            },
                                            {
                                                "id": "delivery_confirmation",
                                                "label": "✅ 补给确认",
                                                "status": "completed",
                                                "summary": "到达X区域后，接收单位确认物资清单与数量无误。",
                                "children": []
                            },
                            {
                                                "id": "inventory_status_update",
                                                "label": "🔄 状态更新",
                                "status": "completed",
                                                "summary": "更新源仓库与目标仓库库存，同步至资源管理系统。",
                                "children": []
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "id": "resource_consumption_prediction",
                                "label": "🔮 资源消耗预测与规划",
                                "status": "pending",
                                "summary": "基于历史消耗数据、任务强度与环境因素预测未来资源消耗，并生成补给周期与储备规划建议。",
                                "children": [
                                    {
                                        "id": "historical_data_analysis",
                                        "label": "📈 历史数据分析",
                                        "status": "pending",
                                        "summary": "分析X作业区历史燃料消耗模式与任务类型分布。",
                                        "children": [
                                            {
                                                "id": "consumption_pattern_extraction",
                                                "label": "📊 消耗模式提取",
                                                "status": "pending",
                                                "summary": "统计不同任务类型下单位时间燃料消耗水平。",
                                                "children": []
                                            },
                                            {
                                                "id": "task_type_correlation",
                                                "label": "🔗 任务类型关联",
                                                "status": "pending",
                                                "summary": "识别任务强度与燃料消耗之间的关系模式。",
                                                "children": []
                                            },
                                            {
                                                "id": "seasonal_variation_analysis",
                                                "label": "🌡️ 季节变化分析",
                                                "status": "pending",
                                                "summary": "识别季节、气候变化对消耗模式的影响。",
                                                "children": []
                                            }
                                        ]
                                    },
                                    {
                                        "id": "environment_task_modeling",
                                        "label": "🌍 环境与任务强度建模",
                                        "status": "pending",
                                        "summary": "建模未来72小时内的温度、地形与操作负载等影响因素。",
                                        "children": [
                                            {
                                                "id": "temperature_modeling",
                                                "label": "🌡️ 温度建模",
                                                "status": "pending",
                                                "summary": "引入未来72小时温度预报，低温增加燃料消耗系数15%。",
                                                "children": []
                                            },
                                            {
                                                "id": "terrain_factor_modeling",
                                                "label": "⛰️ 地形因子建模",
                                                "status": "pending",
                                                "summary": "根据作业区地形坡度与路况推估地形影响系数。",
                                                "children": []
                                            },
                                            {
                                                "id": "operation_load_estimation",
                                                "label": "⚙️ 操作负载估算",
                                                "status": "pending",
                                                "summary": "根据任务计划与排班推估车辆与设备启用强度。",
                                                "children": []
                                            }
                                        ]
                                    },
                                    {
                                        "id": "consumption_prediction",
                                        "label": "📊 消耗量预测",
                                        "status": "pending",
                                        "summary": "生成短期/中期燃料消耗预测曲线。",
                                        "children": [
                                            {
                                                "id": "short_term_forecast",
                                                "label": "⏱️ 短期预测（24小时）",
                                                "status": "pending",
                                                "summary": "预测未来24小时燃料消耗：基线1200L，乐观1000L，保守1500L。",
                                                "children": []
                                            },
                                            {
                                                "id": "medium_term_forecast",
                                                "label": "📅 中期预测（72小时）",
                                                "status": "pending",
                                                "summary": "预测未来72小时燃料总消耗：基线3800L，乐观3200L，保守4800L。",
                                                "children": []
                                            },
                                            {
                                                "id": "peak_period_identification",
                                                "label": "📈 高峰期识别",
                                                "status": "pending",
                                                "summary": "识别可能出现消耗高峰的时间窗口：第2天上午与第3天下午。",
                                "children": []
                            }
                        ]
                    },
                    {
                                        "id": "reserve_planning_advice",
                                        "label": "📝 储备规划与建议",
                                        "status": "pending",
                                        "summary": "给出最小库存量、安全冗余与补给周期建议。",
                                        "children": [
                                            {
                                                "id": "minimum_inventory_setting",
                                                "label": "📦 最小库存量设定",
                                                "status": "pending",
                                                "summary": "建议最小安全库存：2000L（满足48小时基线消耗）。",
                                                "children": []
                                            },
                                            {
                                                "id": "safety_redundancy_design",
                                                "label": "🛡️ 安全冗余设计",
                                                "status": "pending",
                                                "summary": "按保守预测设计25%安全冗余，总储备需求2500L。",
                        "children": []
                    },
                    {
                                                "id": "supply_cycle_recommendation",
                                                "label": "🔄 补给周期建议",
                                                "status": "pending",
                                                "summary": "建议每24小时补给一次，每次补给1200-1500L，平衡仓储成本与安全性。",
                                                "children": []
                                            }
                                        ]
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
                    "summary": "将综合资源保障任务描述转化为结构化的资源类型、需求单位与时限要求。",
                    "key_points": [
                        "识别资源类型：急救物资、医疗物资、燃料等多类资源",
                        "提取需求单位：前线单位（物资状态监控）、小队A/B/C（急救物资分配）、X区域（医疗物资补给）、X作业区（燃料需求预测）",
                        "明确时限要求：72小时燃料需求预测、6小时内完成X区域补给"
                    ],
                    "knowledge_trace": "任务文本 → 资源类型/需求单位/时限要素提取 → 形成结构化任务配置。"
                },
                "resource_support_strategy": {
                    "title": "资源保障策略",
                    "summary": "整合资源评估、需求分配、补给调度与消耗预测，生成完整的资源保障执行方案。",
                    "key_points": [
                        "资源评估：实时追踪物资状态，识别异常",
                        "需求分配：基于优先级与可用量生成最优分配方案",
                        "补给调度：自动生成补给任务并规划运输路线",
                        "消耗预测：预测未来资源需求，优化储备规划"
                    ],
                    "knowledge_trace": "任务解析 + 资源评估 + 需求分配 + 补给调度 + 消耗预测 → 形成可执行资源保障策略。"
                },
                "resource_assessment": {
                    "title": "资源评估",
                    "summary": "对各类资源进行实时位置与数量追踪，并在状态变化时保持同步更新。",
                    "key_points": [
                        "资源类别解析：建立统一的资源分类体系（食物、燃料、备件、医疗物资）",
                        "追踪方式匹配：为不同资源选择合适的追踪技术（RFID、二维码、GPS、无人机）",
                        "状态更新机制：实时更新位置、数量、消耗速率",
                        "异常识别：检测资源丢失、库存异常、传感器失联"
                    ],
                    "knowledge_trace": "资源类别解析 → 追踪方式匹配 → 状态更新机制 → 异常识别。",
                    "knowledge_graph": {
                        "nodes": [
                            # 主推理链节点
                            {"id": "category", "label": "资源类别解析", "type": "input"},
                            {"id": "tracking", "label": "追踪方式匹配", "type": "process"},
                            {"id": "status_update", "label": "状态更新机制", "type": "process"},
                            {"id": "anomaly", "label": "异常识别", "type": "output"},
                            
                            # 辅助细节节点（与任务相关但相关性较低）
                            {"id": "history_inventory", "label": "历史库存记录\n(基线参考)", "type": "input"},
                            {"id": "env_condition", "label": "存储环境条件\n(温湿度监控)", "type": "input"},
                            {"id": "manual_verify", "label": "人工校验日志\n(备用验证)", "type": "process"},
                            {"id": "supply_schedule", "label": "补给计划表\n(背景信息)", "type": "input"},
                            {"id": "alert_config", "label": "告警阈值配置\n(参数设置)", "type": "input"}
                        ],
                        "edges": [
                            # 主推理链连接
                            {"source": "category", "target": "tracking"},
                            {"source": "tracking", "target": "status_update"},
                            {"source": "status_update", "target": "anomaly"},
                            
                            # 辅助节点的单向连接（不破坏主链）
                            {"source": "history_inventory", "target": "status_update"},
                            {"source": "env_condition", "target": "status_update"}
                            
                            # 注意：manual_verify、supply_schedule、alert_config 独立存在，不连接到主链
                        ]
                    }
                },
                "resource_category_parsing": {
                    "title": "资源类别解析",
                    "summary": "建立统一的资源分类体系，为后续追踪与统计提供基础。",
                    "key_points": [
                        "将资源划分为食物、燃料、备件、医疗物资等主类",
                        "在每个大类下增加规格、批次与存储位置等子属性",
                        "为每件资源分配全局唯一标识符，便于跨区域追踪"
                    ],
                    "knowledge_trace": "原始物资清单 → 类别与属性抽取 → 形成资源建模字典。"
                },
                "tracking_method_matching": {
                    "title": "追踪方式匹配",
                    "summary": "结合成本、精度与实时性，为不同类别资源选择合适的追踪技术。",
                    "key_points": [
                        "高价值资源：RFID+GPS组合追踪，实时精度高",
                        "大宗低价值物资：二维码盘点或无人机盘库，成本低",
                        "移动资源：GPS追踪，实时更新位置信息"
                    ],
                    "knowledge_trace": "资源类别 + 价值等级 → 追踪技术能力评估 → 选择追踪方案。"
                },
                "status_update_mechanism": {
                    "title": "状态更新机制",
                    "summary": "定义资源位置、数量与消耗速率等关键字段的更新流程。",
                    "key_points": [
                        "位置更新：基于GPS/RFID读取结果实时更新",
                        "数量更新：根据出入库记录与盘点结果同步",
                        "消耗速率追踪：分析历史数据计算实时消耗速率"
                    ],
                    "knowledge_trace": "追踪读数 + 任务数据 → 字段级融合 → 最新资源状态表。"
                },
                "anomaly_identification": {
                    "title": "异常识别",
                    "summary": "识别资源丢失、库存异常和传感器失联等异常情况。",
                    "key_points": [
                        "资源丢失：RFID/GPS信号长时间未更新",
                        "库存异常：账面与实际盘点差异超过阈值",
                        "传感器失联：追踪设备心跳信号超时"
                    ],
                    "knowledge_trace": "期望状态 + 实时状态 → 异常检测 → 告警与处理建议。"
                },
                "demand_allocation_advice": {
                    "title": "需求分配建议",
                    "summary": "基于任务优先级、可用资源和紧急程度，生成最优资源分配建议。",
                    "key_points": [
                        "需求解析：解析数量、紧急度、使用场景",
                        "库存计算：统计可用量，扣除锁定资源",
                        "分配策略推理：综合优先级、满足度、运输成本",
                        "分配方案生成：输出具体分配比例与理由"
                    ],
                    "knowledge_trace": "需求解析 → 库存计算 → 分配策略推理 → 分配方案生成。",
                    "knowledge_graph": {
                        "nodes": [
                            # 主推理链节点
                            {"id": "demand", "label": "需求解析", "type": "input"},
                            {"id": "inventory", "label": "库存与可用量计算", "type": "process"},
                            {"id": "strategy", "label": "分配策略推理", "type": "decision"},
                            {"id": "plan", "label": "分配方案生成", "type": "output"},
                            
                            # 辅助细节节点（与任务相关但相关性较低）
                            {"id": "task_priority", "label": "任务优先级表\n(分配权重)", "type": "input"},
                            {"id": "transport_cost", "label": "运输成本数据\n(距离/时间)", "type": "input"},
                            {"id": "historical_allocation", "label": "历史分配记录\n(参考案例)", "type": "input"},
                            {"id": "unit_feedback", "label": "单位反馈数据\n(满意度)", "type": "input"},
                            {"id": "emergency_reserve", "label": "应急储备要求\n(最低库存)", "type": "input"}
                        ],
                        "edges": [
                            # 主推理链连接
                            {"source": "demand", "target": "inventory"},
                            {"source": "inventory", "target": "strategy"},
                            {"source": "strategy", "target": "plan"},
                            
                            # 辅助节点的单向连接
                            {"source": "task_priority", "target": "strategy"},
                            {"source": "transport_cost", "target": "strategy"}
                            
                            # 注意：historical_allocation、unit_feedback、emergency_reserve 独立存在
                        ]
                    }
                },
                "demand_parsing": {
                    "title": "需求解析",
                    "summary": "将自然语言描述的物资需求转化为结构化的数量、紧急度与应用场景。",
                    "key_points": [
                        "识别各小队的当前任务类型（进攻、防御、救援等）",
                        "根据任务危险度与持续时间评估急救物资紧急度",
                        "将模糊表达转化为可计算区间"
                    ],
                    "knowledge_trace": "任务描述 → 需求字段抽取 → 结构化需求列表。"
                },
                "inventory_calculation": {
                    "title": "库存与可用量计算",
                    "summary": "综合各仓库库存，计算可在指定时间内下发的有效可用量。",
                    "key_points": [
                        "统计各仓库当前库存及在途补给",
                        "扣除已锁定给其他任务的预分配资源",
                        "考虑有效期、环境适应性等约束"
                    ],
                    "knowledge_trace": "库存数据库 + 任务锁定表 → 可用量计算 → 候选可分配资源池。"
                },
                "allocation_strategy_reasoning": {
                    "title": "分配策略推理",
                    "summary": "在资源有限情况下综合任务优先级、需求满足度与运输成本推导分配规则。",
                    "key_points": [
                        "优先级排序：根据任务紧急度与伤亡风险分配权重",
                        "满足度优化：在权重约束下最大化整体需求满足度",
                        "运输成本：选择运输成本更低的方案"
                    ],
                    "knowledge_trace": "需求列表 + 可用量 → 优先级加权优化 → 分配比例矩阵。"
                },
                "allocation_plan_generation": {
                    "title": "分配方案生成",
                    "summary": "将分配结果转化为每个小队的具体物资数量与调配理由。",
                    "key_points": [
                        "量化列出各小队获得的物资数量与占总量的比例",
                        "解释关键决策原因",
                        "输出结构化结果供后续模块使用"
                    ],
                    "knowledge_trace": "分配策略 + 可用资源 → 生成分配清单。"
                },
                "supply_task_generation": {
                    "title": "补给任务生成与调度",
                    "summary": "基于实时资源短缺情况，自动生成补给任务并推理出最佳补给路线与车辆安排。",
                    "key_points": [
                        "短缺资源识别：检测消耗异常与低库存预警",
                        "补给任务构建：生成物资清单、目标位置、时限要求",
                        "运输与调度规划：匹配车辆、规划路线、确定补给顺序",
                        "任务执行检测：监控执行情况，完成后更新状态"
                    ],
                    "knowledge_trace": "短缺资源识别 → 补给任务构建 → 运输与调度规划 → 任务执行检测。",
                    "knowledge_graph": {
                        "nodes": [
                            # 主推理链节点
                            {"id": "shortage", "label": "短缺资源识别", "type": "input"},
                            {"id": "task", "label": "补给任务构建", "type": "process"},
                            {"id": "transport", "label": "运输与调度规划", "type": "decision"},
                            {"id": "execution", "label": "任务执行检测", "type": "output"},
                            
                            # 辅助细节节点（与任务相关但相关性较低）
                            {"id": "weather_forecast", "label": "气象预报信息\n(路况影响)", "type": "input"},
                            {"id": "vehicle_status", "label": "车辆健康状态\n(可用性评估)", "type": "input"},
                            {"id": "road_condition", "label": "道路状况数据\n(通行能力)", "type": "input"},
                            {"id": "fuel_consumption", "label": "燃料消耗模型\n(续航估算)", "type": "process"},
                            {"id": "backup_route", "label": "备用路线库\n(应急预案)", "type": "input"}
                        ],
                        "edges": [
                            # 主推理链连接
                            {"source": "shortage", "target": "task"},
                            {"source": "task", "target": "transport"},
                            {"source": "transport", "target": "execution"},
                            
                            # 辅助节点的单向连接
                            {"source": "weather_forecast", "target": "transport"},
                            {"source": "vehicle_status", "target": "transport"},
                            {"source": "road_condition", "target": "transport"}
                            
                            # 注意：fuel_consumption、backup_route 独立存在
                        ]
                    }
                },
                "shortage_resource_identification": {
                    "title": "短缺资源识别",
                    "summary": "通过对消耗速率与库存阈值的持续监控，提前发现资源短缺。",
                    "key_points": [
                        "分析历史消耗曲线，识别异常加速消耗段",
                        "对比当前库存与安全库存下限，触发低库存预警",
                        "结合任务计划预测未来缺口规模"
                    ],
                    "knowledge_trace": "历史消耗 + 当前库存 + 未来任务 → 短缺预测与告警。"
                },
                "supply_task_construction": {
                    "title": "补给任务构建",
                    "summary": "将缺口信息转化为可执行的补给任务描述。",
                    "key_points": [
                        "生成细化物资清单与数量",
                        "指定补给目标位置、接收单位与完成时限",
                        "分配任务优先级"
                    ],
                    "knowledge_trace": "短缺预测结果 → 物资与时间约束 → 标准化补给任务实体。"
                },
                "transport_scheduling_planning": {
                    "title": "运输与调度规划",
                    "summary": "为补给任务选择合适车辆、规划路线并排序多个补给点。",
                    "key_points": [
                        "车辆匹配：根据物资体积与重量匹配运输车辆",
                        "路线规划：在安全与效率约束下规划补给路线",
                        "补给顺序：设计合理的停靠顺序"
                    ],
                    "knowledge_trace": "补给任务 + 车队资源 → 多目标路径与调度优化 → 运输计划。"
                },
                "task_execution_monitoring": {
                    "title": "任务执行检测与回传",
                    "summary": "在补给执行过程中持续跟踪进度并更新资源数据库。",
                    "key_points": [
                        "监控车辆位置与状态，判断是否按计划到达",
                        "完成装卸后更新库存",
                        "异常中断时生成告警并建议改派"
                    ],
                    "knowledge_trace": "车队执行数据 + 仓储变更记录 → 任务完成度评估与库存同步。"
                },
                "resource_consumption_prediction": {
                    "title": "资源消耗预测与规划",
                    "summary": "基于历史消耗数据、任务强度与环境因素预测未来资源消耗，并生成补给周期与储备规划建议。",
                    "key_points": [
                        "历史数据分析：识别消耗模式与任务类型关系",
                        "环境与任务强度建模：建模温度、地形、操作负载等影响因素",
                        "消耗量预测：生成短期/中期预测曲线",
                        "储备规划与建议：给出最小库存量、安全冗余、补给周期"
                    ],
                    "knowledge_trace": "历史数据分析 → 环境与任务强度建模 → 消耗量预测 → 储备规划与建议。",
                    "knowledge_graph": {
                        "nodes": [
                            # 主推理链节点
                            {"id": "history", "label": "历史数据分析", "type": "input"},
                            {"id": "modeling", "label": "环境与任务强度建模", "type": "process"},
                            {"id": "forecast", "label": "消耗量预测", "type": "process"},
                            {"id": "reserve", "label": "储备规划与建议", "type": "output"},
                            
                            # 辅助细节节点（与任务相关但相关性较低）
                            {"id": "seasonal_pattern", "label": "季节性消耗模式\n(周期规律)", "type": "input"},
                            {"id": "equipment_efficiency", "label": "设备能效数据\n(性能指标)", "type": "input"},
                            {"id": "operation_schedule", "label": "作业排班计划\n(使用强度)", "type": "input"},
                            {"id": "supply_lead_time", "label": "补给前置时间\n(物流周期)", "type": "input"},
                            {"id": "risk_tolerance", "label": "风险容忍度\n(安全系数)", "type": "input"}
                        ],
                        "edges": [
                            # 主推理链连接
                            {"source": "history", "target": "modeling"},
                            {"source": "modeling", "target": "forecast"},
                            {"source": "forecast", "target": "reserve"},
                            
                            # 辅助节点的单向连接
                            {"source": "seasonal_pattern", "target": "modeling"},
                            {"source": "operation_schedule", "target": "modeling"}
                            
                            # 注意：equipment_efficiency、supply_lead_time、risk_tolerance 独立存在
                        ]
                    }
                },
                "historical_data_analysis": {
                    "title": "历史数据分析",
                    "summary": "基于历史记录识别资源消耗与任务强度之间的关系。",
                    "key_points": [
                        "统计不同任务类型下单位时间燃料消耗水平",
                        "识别昼夜、季节或气候变化带来的消耗模式差异",
                        "发现极端任务或异常用油行为对整体曲线的影响"
                    ],
                    "knowledge_trace": "历史任务+用油数据 → 任务/时间/环境维度聚合 → 多场景消耗基线。"
                },
                "environment_task_modeling": {
                    "title": "环境与任务强度建模",
                    "summary": "根据未来任务计划与环境预报构建消耗影响因子模型。",
                    "key_points": [
                        "引入温度、地形坡度、路况等环境变量",
                        "根据排班与任务计划推估车辆与设备启用强度",
                        "将因素映射为燃料消耗系数的动态调整因子"
                    ],
                    "knowledge_trace": "环境预报 + 任务计划 → 强度与环境因子 → 影响系数模型。"
                },
                "consumption_prediction": {
                    "title": "消耗量预测",
                    "summary": "在历史基线与未来因子模型的基础上，生成未来消耗预测。",
                    "key_points": [
                        "对不同时间段分别计算期望消耗区间与置信度",
                        "识别可能出现高峰消耗的时间窗口",
                        "提供多种情景（乐观/基线/保守）下的预测曲线"
                    ],
                    "knowledge_trace": "历史基线 + 影响系数 → 时间序列预测 → 多情景消耗曲线。"
                },
                "reserve_planning_advice": {
                    "title": "储备规划与建议",
                    "summary": "基于预测结果规划最小库存、安全冗余与补给节奏。",
                    "key_points": [
                        "确定任何时间点下不低于的最小安全库存量",
                        "按高峰消耗与补给不确定性设计冗余比例",
                        "给出补给批次与时间间隔建议，平衡仓储成本与安全性"
                    ],
                    "knowledge_trace": "消耗预测曲线 + 补给能力与风险偏好 → 库存与补给策略优化。"
                }
            }
        },
    ),
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