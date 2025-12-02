import copy

from .base import DEFAULT_BLUEPRINT, DEFAULT_NODE_INSIGHT
from .offroad_logistics import BLUEPRINT as OFFROAD_LOGISTICS_BLUEPRINT
from .equipment_deployment import BLUEPRINT as EQUIPMENT_DEPLOYMENT_BLUEPRINT
from .casualty_rescue import CASUALTY_RESCUE_BLUEPRINT
from .personnel_transport import BLUEPRINT as PERSONNEL_TRANSPORT_BLUEPRINT
from .resource_support import BLUEPRINT as RESOURCE_SUPPORT_BLUEPRINT
from .logistics_control import BLUEPRINT as LOGISTICS_CONTROL_BLUEPRINT


SUPPORT_MODELS = [
    "越野物流",
    "设备投放",
    "伤员救助",
    "人员输送",
    "资源保障",
    "后勤资源管控"
]

_BLUEPRINTS = {
    "越野物流": OFFROAD_LOGISTICS_BLUEPRINT,
    "设备投放": EQUIPMENT_DEPLOYMENT_BLUEPRINT,
    "伤员救助": CASUALTY_RESCUE_BLUEPRINT,
    "人员输送": PERSONNEL_TRANSPORT_BLUEPRINT,
    "资源保障": RESOURCE_SUPPORT_BLUEPRINT,
    "后勤资源管控": LOGISTICS_CONTROL_BLUEPRINT
}


def get_model_blueprint(model_name: str):
    blueprint = _BLUEPRINTS.get(model_name)
    if blueprint is None:
        return copy.deepcopy(DEFAULT_BLUEPRINT)
    return copy.deepcopy(blueprint)


__all__ = [
    "SUPPORT_MODELS",
    "get_model_blueprint",
    "DEFAULT_NODE_INSIGHT"
]



