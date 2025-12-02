from .base import build_generic_blueprint


BLUEPRINT = build_generic_blueprint(
    root_label="设备投放指令解析",
    root_summary="围绕投放窗口、投放方式与回补节奏生成行动计划。",
    node_insight_overrides={
        "environment_scan": {
            "summary": "识别投放区域的地形开阔度、天气窗口与潜在干扰源。",
            "key_points": [
                "结合卫星/无人机影像评估落点安全等级",
                "计算风场/降水对空投/无人机投放的影响",
                "标注禁止投放区并输出候选区域"
            ],
            "knowledge_trace": "环境标签驱动“落点选址→投放方式”筛选逻辑。"
        },
        "resource_match": {
            "summary": "对接可投放装备清单，匹配吊舱/机型/地面机器人组合。",
            "key_points": [
                "根据载荷与能耗约束选择空投或地面投送方式",
                "自动分配投放批次与装载模板",
                "生成回补周期与库存预警"
            ],
            "knowledge_trace": "装备规格与投放窗口对齐后输出批次计划。"
        },
        "plan_output": {
            "summary": "生成“装载→飞行/行进路径→落点校核→回传确认”流程。",
            "key_points": [
                "把投放脚本转换为行为树节点供监控系统使用",
                "绑定实时回执，确保物资落点可追踪",
                "若落点不达标自动触发备选方案"
            ],
            "knowledge_trace": "策略输出节点衔接落点监控与回补迭代链路。"
        }
    }
)

__all__ = ["BLUEPRINT"]



