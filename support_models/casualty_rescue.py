CASUALTY_RESCUE_BLUEPRINT = {
    "default_focus": "priority_plan",
    "behavior_tree": {
        "id": "task_parse",
        "label": "救援指令解析",
        "status": "completed",
        "summary": "解析任务描述并对接伤员/队伍清单。",
        "children": [
            {
                "id": "data_clean",
                "label": "多源数据清洗",
                "status": "completed",
                "summary": "融合穿戴传感器、语音回传与无人机观察数据。",
                "children": [
                    {
                        "id": "sync_time",
                        "label": "时间轴对齐",
                        "status": "completed",
                        "summary": "对不同来源数据进行时间戳对齐和缺失插值。",
                        "children": [
                            {
                                "id": "sync_sensor",
                                "label": "传感器流对齐",
                                "status": "completed",
                                "summary": "对心率、血压、血氧等体征曲线做时间同步。",
                                "children": []
                            },
                            {
                                "id": "sync_manual",
                                "label": "人工记录对齐",
                                "status": "pending",
                                "summary": "将语音/手工记录与传感器时间线映射。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "noise_filter",
                        "label": "噪声与异常过滤",
                        "status": "completed",
                        "summary": "识别并剔除传感器抖动和明显错误值。",
                        "children": [
                            {
                                "id": "hard_outlier",
                                "label": "硬异常剔除",
                                "status": "completed",
                                "summary": "去除不可能出现的极端数值点。",
                                "children": []
                            },
                            {
                                "id": "soft_outlier",
                                "label": "软异常标记",
                                "status": "pending",
                                "summary": "对存在争议的数据打上低置信度标记。",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            {
                "id": "vital_assess",
                "label": "体征阈值判定",
                "status": "active",
                "summary": "将心率、血压、血氧等体征映射至休克阈值。",
                "children": [
                    {
                        "id": "anomaly_detect",
                        "label": "体征异常识别",
                        "status": "active",
                        "summary": "识别“体征异常→休克/危重症”语义链。",
                        "children": []
                    },
                    {
                        "id": "shock_alert",
                        "label": "休克预警输出",
                        "status": "pending",
                        "summary": "生成黄色/红色预警节点并标记风险。",
                        "children": [
                            {
                                "id": "shock_prob",
                                "label": "休克概率估计",
                                "status": "pending",
                                "summary": "基于多指标计算每名伤员的休克概率。",
                                "children": []
                            },
                            {
                                "id": "shock_grade",
                                "label": "预警等级划分",
                                "status": "pending",
                                "summary": "将概率映射为黄色/红色等离散预警等级。",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            {
                "id": "priority_plan",
                "label": "优先救援排序",
                "status": "pending",
                "summary": "综合危急指数与资源约束，确定救援顺序。",
                "children": [
                    {
                        "id": "score_compute",
                        "label": "危急指数计算",
                        "status": "pending",
                        "summary": "融合体征异常、意识状态和任务价值计算危急指数。",
                        "children": [
                            {
                                "id": "score_physio",
                                "label": "生理指标评分",
                                "status": "pending",
                                "summary": "根据体征异常程度生成基础生理风险分。",
                                "children": []
                            },
                            {
                                "id": "score_mission",
                                "label": "任务价值修正",
                                "status": "pending",
                                "summary": "考虑伤员在当前任务中的关键程度进行加权。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "resource_constraint",
                        "label": "资源约束评估",
                        "status": "pending",
                        "summary": "评估医疗小队、担架和运力等资源瓶颈。",
                        "children": [
                            {
                                "id": "resource_local",
                                "label": "现场资源评估",
                                "status": "pending",
                                "summary": "统计当前可直接使用的医疗与转运资源。",
                                "children": []
                            },
                            {
                                "id": "resource_reachable",
                                "label": "可调入资源评估",
                                "status": "pending",
                                "summary": "评估在限定时间内可增援的后续资源。",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            {
                "id": "evacuation_sync",
                "label": "转运方案与反馈",
                "status": "pending",
                "summary": "匹配可用运力并回传执行状态。",
                "children": [
                    {
                        "id": "evac_match",
                        "label": "转运方式匹配",
                        "status": "pending",
                        "summary": "为不同等级伤员匹配空中/地面/无人转运方式。",
                        "children": [
                            {
                                "id": "evac_critical",
                                "label": "危重伤员转运",
                                "status": "pending",
                                "summary": "为危重伤员选择最快、最稳的转运链路。",
                                "children": []
                            },
                            {
                                "id": "evac_stable",
                                "label": "稳定伤员转运",
                                "status": "pending",
                                "summary": "为相对稳定伤员安排批量转运流程。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "evac_feedback",
                        "label": "执行反馈与复评",
                        "status": "pending",
                        "summary": "跟踪转运执行情况，必要时重新调整优先级。",
                        "children": [
                            {
                                "id": "evac_status_track",
                                "label": "转运状态跟踪",
                                "status": "pending",
                                "summary": "实时记录各批次转运进度和异常情况。",
                                "children": []
                            },
                            {
                                "id": "evac_re_prioritize",
                                "label": "优先级重排",
                                "status": "pending",
                                "summary": "根据最新体征和资源状态重新排序队列。",
                                "children": []
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "node_insights": {
        "task_parse": {
            "title": "救援指令解析",
            "summary": "抽取任务地点、伤员数量与通联方式，构建统一任务面板。",
            "key_points": [
                "语义解析识别“伤员 ID+症状”结构",
                "与知识库比对既往伤情标签",
                "向下游节点广播标准化任务包"
            ],
            "knowledge_trace": "通过“任务文本→标准任务模板”链路定位到支援模型的救援场景入口。"
        },
        "data_clean": {
            "title": "多源数据清洗",
            "summary": "标准化传感器、语音与图像节点，剔除噪声并插值缺失值。",
            "key_points": [
                "同步时间戳确保数据对齐",
                "异常值剔除防止误判",
                "结构化结果推送至体征判定节点"
            ],
            "knowledge_trace": "“原始数据→清洗节点→体征库”链路高亮展示数据治理逻辑。"
        },
        "vital_assess": {
            "title": "体征阈值判定",
            "summary": "调用阈值节点，将实时体征映射到风险等级。",
            "key_points": [
                "匹配心率/血压/血氧等阈值表",
                "与历史病例子图比对趋势",
                "输出“异常体征节点”供预警节点引用"
            ],
            "knowledge_trace": "高亮“体征数值→阈值库→休克/危重症”链路，解释风险来源。"
        },
        "anomaly_detect": {
            "title": "体征异常识别",
            "summary": "将清洗后的体征与“休克/危重症”概念相连，输出告警。",
            "key_points": [
                "定位异常体征来源",
                "映射至休克/危重症概念节点",
                "向优先级节点推送危急指数因子"
            ],
            "knowledge_trace": "高亮“体征数值”指向“休克/危重症”的语义映射链路，显示异常来源。"
        },
        "shock_alert": {
            "title": "休克预警输出",
            "summary": "根据异常体征与倒排规则生成预警颜色，并提示干预建议。",
            "key_points": [
                "聚合多指标异常信号",
                "推断可能的生理机能受损节点",
                "输出黄色/红色预警"
            ],
            "knowledge_trace": "“异常体征→生理机能受损→黄色/红色预警状态”链路用于说明预警结果。"
        },
        "priority_plan": {
            "title": "优先救援排序",
            "summary": "结合危急指数与资源约束动态生成“先救谁”列表。",
            "key_points": [
                "危急指数：体征异常、意识状态与任务价值加权",
                "资源约束：担架、救援队与行进距离实时评估",
                "动态重排：任一体征或资源变动即刻刷新序列"
            ],
            "knowledge_trace": "综合危急指数与资源匹配逻辑，输出实时救援顺序。",
            "knowledge_graph": {
                "nodes": [
                    {"id": "vital_signs", "label": "体征数据", "type": "input"},
                    {"id": "resource_status", "label": "资源状态", "type": "input"},
                    {"id": "urgency_calculation", "label": "危急指数计算", "type": "process"},
                    {"id": "resource_constraint_check", "label": "资源约束评估", "type": "process"},
                    {"id": "priority_sorting", "label": "优先级排序", "type": "decision"},
                    {"id": "rescue_sequence", "label": "救援序列", "type": "output"}
                ],
                "edges": [
                    {"source": "vital_signs", "target": "urgency_calculation"},
                    {"source": "resource_status", "target": "resource_constraint_check"},
                    {"source": "urgency_calculation", "target": "priority_sorting"},
                    {"source": "resource_constraint_check", "target": "priority_sorting"},
                    {"source": "priority_sorting", "target": "rescue_sequence"}
                ]
            }
        },
        "evacuation_sync": {
            "title": "转运方案与反馈",
            "summary": "匹配空地协同转运能力，并实时同步执行状态。",
            "key_points": [
                "选择最优转运方式（空中/地面/无人）",
                "推送执行节点至指挥终端",
                "回收执行反馈闭环调度"
            ],
            "knowledge_trace": "“救援顺序→转运资源→执行反馈”链路佐证方案来源。"
        },
        "sync_time": {
            "title": "时间轴对齐",
            "summary": "对不同来源数据进行时间戳对齐和缺失插值，确保多源数据同步。",
            "key_points": [
                "时间戳标准化处理",
                "缺失数据插值算法",
                "数据同步验证"
            ],
            "knowledge_trace": "时间对齐确保数据一致性，为后续体征分析提供可靠基础。"
        },
        "sync_sensor": {
            "title": "传感器流对齐",
            "summary": "对心率、血压、血氧等体征曲线做时间同步。",
            "key_points": [
                "多传感器数据同步",
                "时间戳精确匹配",
                "数据完整性检查"
            ],
            "knowledge_trace": "传感器数据同步是体征监测的基础。"
        },
        "sync_manual": {
            "title": "人工记录对齐",
            "summary": "将语音/手工记录与传感器时间线映射。",
            "key_points": [
                "语音识别与时间标记",
                "人工输入数据整合",
                "跨模态数据对齐"
            ],
            "knowledge_trace": "人工记录补充传感器数据盲区。"
        },
        "noise_filter": {
            "title": "噪声与异常过滤",
            "summary": "识别并剔除传感器抖动和明显错误值。",
            "key_points": [
                "异常值检测算法",
                "噪声过滤技术",
                "数据质量评估"
            ],
            "knowledge_trace": "数据清洗确保体征判定的准确性。"
        },
        "hard_outlier": {
            "title": "硬异常剔除",
            "summary": "去除不可能出现的极端数值点。",
            "key_points": [
                "物理极限阈值检查",
                "极端值自动识别",
                "异常数据标记"
            ],
            "knowledge_trace": "硬异常剔除防止误判。"
        },
        "soft_outlier": {
            "title": "软异常标记",
            "summary": "对存在争议的数据打上低置信度标记。",
            "key_points": [
                "统计异常检测",
                "置信度评估",
                "数据质量分级"
            ],
            "knowledge_trace": "软异常标记保留潜在有用信息。"
        },
        "shock_prob": {
            "title": "休克概率估计",
            "summary": "基于多指标计算每名伤员的休克概率。",
            "key_points": [
                "多指标综合评估",
                "概率模型计算",
                "风险量化"
            ],
            "knowledge_trace": "休克概率是优先排序的关键指标。"
        },
        "shock_grade": {
            "title": "预警等级划分",
            "summary": "将概率映射为黄色/红色等离散预警等级。",
            "key_points": [
                "概率到等级映射",
                "预警阈值设置",
                "等级标准化"
            ],
            "knowledge_trace": "预警等级指导救援优先级。"
        },
        "score_compute": {
            "title": "危急指数计算",
            "summary": "融合体征异常、意识状态和任务价值计算危急指数。",
            "key_points": [
                "多维度指标融合",
                "加权计算算法",
                "指数标准化"
            ],
            "knowledge_trace": "危急指数决定救援顺序。"
        },
        "score_physio": {
            "title": "生理指标评分",
            "summary": "根据体征异常程度生成基础生理风险分。",
            "key_points": [
                "体征异常量化",
                "生理风险评估",
                "评分标准化"
            ],
            "knowledge_trace": "生理评分反映伤员紧急程度。"
        },
        "score_mission": {
            "title": "任务价值修正",
            "summary": "考虑伤员在当前任务中的关键程度进行加权。",
            "key_points": [
                "任务角色评估",
                "价值权重计算",
                "综合评分调整"
            ],
            "knowledge_trace": "任务价值影响救援优先级。"
        },
        "resource_constraint": {
            "title": "资源约束评估",
            "summary": "评估医疗小队、担架和运力等资源瓶颈。",
            "key_points": [
                "资源可用性检查",
                "瓶颈识别",
                "约束条件分析"
            ],
            "knowledge_trace": "资源约束影响救援方案可行性。"
        },
        "resource_local": {
            "title": "现场资源评估",
            "summary": "统计当前可直接使用的医疗与转运资源。",
            "key_points": [
                "现场资源清点",
                "可用性验证",
                "即时资源状态"
            ],
            "knowledge_trace": "现场资源是第一响应能力基础。"
        },
        "resource_reachable": {
            "title": "可调入资源评估",
            "summary": "评估在限定时间内可增援的后续资源。",
            "key_points": [
                "增援资源规划",
                "时间窗口评估",
                "后备资源动员"
            ],
            "knowledge_trace": "可调入资源扩展救援能力。"
        },
        "evac_match": {
            "title": "转运方式匹配",
            "summary": "为不同等级伤员匹配空中/地面/无人转运方式。",
            "key_points": [
                "转运方式选择",
                "伤员分级匹配",
                "运力优化配置"
            ],
            "knowledge_trace": "匹配转运方式提高效率和安全性。"
        },
        "evac_critical": {
            "title": "危重伤员转运",
            "summary": "为危重伤员选择最快、最稳的转运链路。",
            "key_points": [
                "紧急转运路径",
                "生命支持保障",
                "快速响应机制"
            ],
            "knowledge_trace": "危重伤员优先使用最优转运方式。"
        },
        "evac_stable": {
            "title": "稳定伤员转运",
            "summary": "为相对稳定伤员安排批量转运流程。",
            "key_points": [
                "批量转运组织",
                "资源利用优化",
                "流程标准化"
            ],
            "knowledge_trace": "稳定伤员采用高效批量转运。"
        },
        "evac_feedback": {
            "title": "执行反馈与复评",
            "summary": "跟踪转运执行情况，必要时重新调整优先级。",
            "key_points": [
                "执行状态监控",
                "实时反馈收集",
                "动态调整机制"
            ],
            "knowledge_trace": "反馈闭环确保救援效果。"
        },
        "evac_status_track": {
            "title": "转运状态跟踪",
            "summary": "实时记录各批次转运进度和异常情况。",
            "key_points": [
                "进度实时更新",
                "异常情况记录",
                "状态可视化"
            ],
            "knowledge_trace": "状态跟踪支持决策调整。"
        },
        "evac_re_prioritize": {
            "title": "优先级重排",
            "summary": "根据最新体征和资源状态重新排序队列。",
            "key_points": [
                "动态优先级计算",
                "队列实时调整",
                "资源重新分配"
            ],
            "knowledge_trace": "重排确保最优救援顺序。"
        }
    }
}

__all__ = ["CASUALTY_RESCUE_BLUEPRINT"]
