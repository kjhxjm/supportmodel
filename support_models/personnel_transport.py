from .base import build_generic_blueprint


BLUEPRINT = build_generic_blueprint(
    root_label="人员输送任务解析",
    root_summary="对接队员状态、运力与路线，输出安全高效的输送编组。",
    node_insight_overrides={
        "environment_scan": {
            "summary": "关注路线安全等级、交通节点拥堵与潜在袭扰风险。",
            "key_points": [
                "融合情报、路况与气象，筛选可用通道",
                "标记易受伏击/干扰路段并生成警戒节点",
                "为编组计划输出安全等级标签"
            ],
            "knowledge_trace": "安全等级驱动输送路线选择与护航策略。"
        },
        "resource_match": {
            "summary": "匹配运输工具（有人/无人）、护航力量与医疗备份。",
            "key_points": [
                "按载员、航程与维护状态筛选运力",
                "结合任务优先级动态调整护航队列",
                "嵌入医疗模块与应急补给"
            ],
            "knowledge_trace": "运力与任务权重映射后形成输送编组。"
        },
        "plan_output": {
            "summary": "输出“上客→路线推进→途中监测→卸载反馈”全流程节点。",
            "key_points": [
                "生成带时间戳的里程碑计划",
                "接入车/机载监测，实时更新状态",
                "异常情况触发自动改线/撤离预案"
            ],
            "knowledge_trace": "行为树节点与输送监控平台双向同步，确保队员安全。"
        }
    }
)

__all__ = ["BLUEPRINT"]



