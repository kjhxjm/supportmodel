from difflib import SequenceMatcher
from typing import List, Optional, Tuple
from .scenes.schema import Scenario
from .scenes import off_road_logistics, equipment_deployment, casualty_rescue, personnel_transport, logistics_resource_management_control, resource_support

SCENARIOS: List[Scenario] = [
    *[s for s in [
        off_road_logistics,
        equipment_deployment,
        casualty_rescue,
        personnel_transport,
        logistics_resource_management_control,
        resource_support
    ] for s in s.SCENARIOS]
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
    candidates: List[Scenario] = [
        s for s in SCENARIOS if s.model_name == model_name]
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
