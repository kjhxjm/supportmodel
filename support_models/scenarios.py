from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple


@dataclass
class Scenario:
    """
    预设的测试任务场景，用于为大模型提供 one-shot 示例。
    """

    id: str
    model_name: str
    name: str
    example_input: str
    reasoning_chain: str


# 基于 instruction/task.md 中的描述，为表1的 20 条测试项目补齐 one-shot 场景。
SCENARIOS: List[Scenario] = [
    # 一、越野物流支援模型测试（1~4）
    Scenario(
        id="offroad_fleet_formation",  # 1. 任务编组
        model_name="越野物流",
        name="任务编组",
        example_input="向X位置运输资源Y，道路可能受损",
        reasoning_chain="任务解析（运输、重量、时限、路况）→ 车辆类型匹配（选择中型越野无人车，理由：载重能力与地形适应性）→ 数量计算（基于单车载重和冗余要求推导车辆数量）→ 装载方案（物资分配与固定方式）",
    ),
    Scenario(
        id="offroad_dynamic_routing",  # 2. 动态路径规划与重规划
        model_name="越野物流",
        name="动态路径规划与重规划",
        example_input="向X位置运输资源Y，道路可能受损",
        reasoning_chain="路径规划（读取地图与路况信息生成初始路径）→ 异常感知与处理（感知数据异常，派遣无人机/机器狗抵近观察）→ 路径重规划（综合车队状态、地图与异常信息重新规划可行路径）",
    ),
    Scenario(
        id="offroad_cargo_monitor",  # 3. 货物状态监控
        model_name="越野物流",
        name="货物状态监控与保全",
        example_input="向X位置运输冷冻食品Y",
        reasoning_chain="货物运输要求（温度等约束）→ 车辆匹配（选择具备温度传感器和保温/制冷能力的车辆）→ 异常感知与处理（设定温度采集频率，登记并上报温度异常，触发保全策略）",
    ),
    Scenario(
        id="offroad_convoy_coordination",  # 4. 车队协同
        model_name="越野物流",
        name="车队协同与效率调度",
        example_input="向X位置运输4车食品和水",
        reasoning_chain="行进编队规划（依据道路宽度选择单列或并行队列）→ 协同动作管理（依据道路宽度组织依序掉头或队列整体倒置等动作）",
    ),

    # 二、设备投放支援模型测试（5~8）
    Scenario(
        id="equipment_fleet_formation",  # 5. 任务编组
        model_name="设备投放",
        name="任务编组",
        example_input="向X前沿阵地投放侦察装置Y，需要多架无人机协同运输",
        reasoning_chain="任务解析（物资类型、重量与体积、投放精度需求、环境风险）→ 设备匹配（匹配适用的无人机或无人车类型）→ 数量推断（根据载荷能力与冗余策略推算所需设备数量）→ 投放方式生成（悬停投放/抛投/着陆放置等）",
    ),
    Scenario(
        id="equipment_precision_location",  # 6. 高精度目标定位
        model_name="设备投放",
        name="高精度目标定位",
        example_input="向X区域精确投放传感器Y",
        reasoning_chain="环境解析（读取地图、地物特征、遮挡信息）→ 传感器融合定位（无人机视觉、激光雷达、深度感知等多源数据融合）→ 误差纠正（基于航迹、风场、地面标志物进行偏差修正）→ 定位结果生成（输出目标区域精确坐标）",
    ),
    Scenario(
        id="equipment_auto_loading",  # 7. 自主装卸控制
        model_name="设备投放",
        name="自主装卸控制",
        example_input="将设备Y通过无人车运输至X点，并由机械臂自主卸载",
        reasoning_chain="装卸需求解析（重量、尺寸、抓取方式）→ 动作规划（机械臂抓取路径、姿态调整、力控策略）→ 安全检测（防倾倒、防滑落、力反馈监测）→ 装卸完成确认（识别设备是否已稳定装载/完成卸载）",
    ),
    Scenario(
        id="equipment_delivery_confirmation",  # 8. 效效确认 / 投放确认
        model_name="设备投放",
        name="投放确认",
        example_input="将侦察节点Y投放至X点并确认部署成功",
        reasoning_chain="结果感知（投放后图像、姿态信息、设备回传信号）→ 落点偏差分析（比较实际坐标与目标坐标）→ 功能状态检查（是否正常通电、是否建立通信链路）→ 投放成功判定（成功/失败/需重投）",
    ),

    # 三、伤员救助支援模型测试（9~12）
    Scenario(
        id="casualty_team_formation",  # 9. 任务编组
        model_name="伤员救助",
        name="任务编组",
        example_input="在X区域发现两名伤员，需要无人救援设备前往救助并运回安全点",
        reasoning_chain="任务解析（伤员数量、地形环境、救助紧急度）→ 设备类型匹配（医疗无人机、担架无人车或机器人）→ 数量计算（根据伤员人数与运载能力推算设备数量）→ 救援方式规划（空投急救包/无人机抵近观察/无人车运送）",
    ),
    Scenario(
        id="casualty_remote_triage",  # 10. 远程伤情初步评估与分类
        model_name="伤员救助",
        name="远程伤情初步评估与分类",
        example_input="对X位置可能受伤的人员进行远程伤情初判",
        reasoning_chain="环境与风险解析（烟尘、水流、危险源）→ 视觉识别与姿态判断（倒地、出血、意识状态）→ 生命体征远程检测（基于远红外/毫米波估计呼吸和心率）→ 伤情分类与优先救援级别标注",
    ),
    Scenario(
        id="casualty_near_field_assessment",  # 11. 过程/近程伤情评估
        model_name="伤员救助",
        name="近程伤情评估",
        example_input="无人救援车抵近X点后对伤员进行详细伤情检查",
        reasoning_chain="近距感知初始化（高清视觉、深度、红外）→ 重点部位识别（出血点、骨折可疑部位、胸腹部异常）→ 生命体征精细测量（血氧、心率、呼吸、体温）→ 伤情诊断与建议（止血、固定、搬运姿势调整等）",
    ),
    Scenario(
        id="casualty_data_sync",  # 12. 伤情数据同步
        model_name="伤员救助",
        name="伤情数据同步",
        example_input="将X伤员的最新伤情数据同步至后方指挥所",
        reasoning_chain="数据结构整理（生命体征、伤情分级、位置）→ 通信链路选择（点对点、组网中继、卫星链路）→ 数据同步策略（周期同步、事件触发、异常加密传输）→ 同步确认（指挥端数据校验与时间戳比对）",
    ),

    # 四、人员输送支援模型测试（13~16）
    Scenario(
        id="personnel_transport_formation",  # 13. 任务编组
        model_name="人员输送",
        name="任务编组",
        example_input="向X区域输送8名人员，需确保途中安全与舒适性",
        reasoning_chain="任务解析（乘员数量、随行物资、路况风险）→ 车辆类型匹配（选择人员运输无人车或越野运输平台）→ 数量计算（依据单车载员数推导需要的车辆数量）→ 搭载方案规划（座位分配、随行物资固定）",
    ),
    Scenario(
        id="personnel_comfort_routing",  # 14. 舒适性导向路径规划
        model_name="人员输送",
        name="舒适连续导航路径规划",
        example_input="将人员运送至X点，优先选择颠簸最小的路线",
        reasoning_chain="路况综合解析（坡度、崎岖度、障碍密度）→ 舒适度模型评估（振动预测、加速度变化分析）→ 路径优选（选择起伏小、加减速稳定的路线）→ 动态调整（根据实时振动/颠簸感知进行微调）",
    ),
    Scenario(
        id="personnel_safety_monitor",  # 15. 人员与环境安全监控
        model_name="人员输送",
        name="人员与环境安全监控",
        example_input="运输途中需实时监控人员状态和外界潜在危险",
        reasoning_chain="乘员状态监控（安全带状态、姿态监测、体征波动）→ 环境风险感知（落石、积水、滑坡风险、车辆周界异常）→ 异常识别与处理（减速避让、停车保护、告警回传）→ 安全策略更新（基于实时风险调整行驶参数）",
    ),
    Scenario(
        id="personnel_multi_destination_dispatch",  # 16. 多目的地协同调度
        model_name="人员输送",
        name="多目的地协同调度",
        example_input="需将人员A送至X点，人员B送至Y点，人员C送至Z点",
        reasoning_chain="任务拆解（人员与目的地映射）→ 路径代价计算（距离、时间、路况）→ 停靠顺序规划（基于总体效率的最优顺序）→ 多车协同（车辆分工、同步与交叉任务处理）",
    ),

    # 五、资源保障支援模型测试（17~20）
    Scenario(
        id="resource_tracking",  # 17. 资源追踪 / 资源建模
        model_name="资源保障",
        name="资源追踪",
        example_input="监控当前所有前线单位的物资状态",
        reasoning_chain="资源类别解析（弹药、食物、燃料、备件等）→ 追踪方式匹配（RFID、二维码、GPS、无人机盘点）→ 状态更新机制（位置、数量、消耗速率）→ 异常识别（资源丢失、库存异常、传感器失联）",
    ),
    Scenario(
        id="resource_allocation",  # 18. 需求分配建议
        model_name="资源保障",
        name="需求分配建议",
        example_input="为A、B、C三个小队分配现有急救物资",
        reasoning_chain="需求解析（数量、紧急度、使用场景）→ 库存与可用量计算 → 分配策略推理（优先级分级、需求满足度、运输成本）→ 分配方案生成（分配比例与对应理由）",
    ),
    Scenario(
        id="resource_replenishment_dispatch",  # 19. 补给任务生成与调度
        model_name="资源保障",
        name="补给任务生成与调度",
        example_input="对X区域缺乏医疗物资，生成补给任务并安排运输",
        reasoning_chain="短缺资源识别（消耗异常、低库存预警）→ 补给任务构建（物资清单、目标位置、时限要求）→ 运输与调度规划（车辆匹配、路线规划、补给顺序）→ 任务执行检测与回传（补给确认、状态更新）",
    ),
    Scenario(
        id="resource_consumption_forecast",  # 20. 资源消耗预测与规划
        model_name="资源保障",
        name="资源消耗预测与规划",
        example_input="预测未来72小时内X作业区的燃料需求",
        reasoning_chain="历史数据分析（消耗模式、任务类型）→ 环境与任务强度建模（温度、地形、操作负载）→ 消耗量预测（短期/中期预测曲线）→ 储备规划与建议（最小库存量、安全冗余、补给周期）",
    ),
]


def _similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def find_best_scenario(model_name: str, query: str) -> Tuple[Optional[Scenario], float]:
    """
    在给定模型下，根据用户任务描述找到最相近的预设场景。

    返回 (Scenario 或 None, 相似度 0~1)。
    """
    candidates: List[Scenario] = [s for s in SCENARIOS if s.model_name == model_name]
    if not candidates:
        return None, 0.0

    best: Optional[Scenario] = None
    best_score = 0.0
    for scenario in candidates:
        score = _similarity(query, scenario.example_input)
        if score > best_score:
            best = scenario
            best_score = score

    return best, best_score


__all__ = ["Scenario", "SCENARIOS", "find_best_scenario"]


