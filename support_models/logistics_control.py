from .base import build_generic_blueprint


BLUEPRINT = build_generic_blueprint(
    root_label="后勤资源管控任务解析",
    root_summary="管理多级库存、资产状态与指挥规则，防止断供与浪费。",
    node_insight_overrides={
        "environment_scan": {
            "summary": "聚焦资源态势，包括库存健康度、资金占用与任务优先级。",
            "key_points": [
                "整合财务、仓储与任务数据生成资源雷达图",
                "识别库存积压/缺口并输出告警等级",
                "同步合规策略与权限配置"
            ],
            "knowledge_trace": "资源态势评估为后勤决策提供可追溯依据。"
        },
        "resource_match": {
            "summary": "根据策略上限、预算与资产寿命制定调控方案。",
            "key_points": [
                "自动核对报废/维护周期，防止违规使用",
                "结合预算与战备等级调整资源配额",
                "输出审批节点与执行人"
            ],
            "knowledge_trace": "政策与资产数据双向印证，保障调控透明。"
        },
        "plan_output": {
            "summary": "形成“审批流程→执行指令→可视化监管”闭环。",
            "key_points": [
                "生成多级审批链与时间承诺",
                "自动落库到资产管理系统，记录追溯日志",
                "异常时触发问责与备份调配方案"
            ],
            "knowledge_trace": "调控行为可在审计链路中完整还原。"
        }
    }
)

__all__ = ["BLUEPRINT"]



