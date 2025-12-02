from .base import build_generic_blueprint


BLUEPRINT = build_generic_blueprint(
    root_label="资源保障任务解析",
    root_summary="聚焦油料、弹药、医疗等多类物资的统筹调拨。",
    node_insight_overrides={
        "environment_scan": {
            "summary": "以任务区域需求峰值、消耗趋势与通路畅通度为核心。",
            "key_points": [
                "读取数字孪生或仓储系统的库存/消耗曲线",
                "识别受阻节点（天气、敌情等）并标注风险",
                "为补给批次提供时间与空间窗口"
            ],
            "knowledge_trace": "需求预测与通路状态共同决定保障优先级。"
        },
        "resource_match": {
            "summary": "对接多级仓储与运输方式，生成最优供应链组合。",
            "key_points": [
                "自动匹配前沿-节点-后方三级仓储冗余",
                "选择铁路、空投、无人车等补给方式组合",
                "输出批次、数量与到达时间"
            ],
            "knowledge_trace": "供应链节点依赖关系用于证明调度结果的可靠性。"
        },
        "plan_output": {
            "summary": "将保障计划转化为调拨指令、监控指标与预警阈值。",
            "key_points": [
                "生成可视化补给甘特图/表格",
                "绑定预警阈值，实时检测库存异常",
                "提供调整建议与备选方案"
            ],
            "knowledge_trace": "策略输出节点与保障监控看板保持同步更新。"
        }
    }
)

__all__ = ["BLUEPRINT"]



