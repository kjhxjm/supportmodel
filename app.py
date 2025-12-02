from flask import Flask, render_template, jsonify, request
from typing import Optional
import copy
import os

from support_models import SUPPORT_MODELS, get_model_blueprint, DEFAULT_NODE_INSIGHT
from support_models.offroad_logistics import generate_dynamic_blueprint
from support_models.llm_client import BlueprintResult, generate_blueprint_with_llm

app = Flask(__name__)


def _normalize_model_name(model_name):
    if model_name in SUPPORT_MODELS:
        return model_name
    return SUPPORT_MODELS[0]


def _maybe_use_llm_blueprint(
    model_name: str, task_description: str, base_blueprint: dict
) -> dict:
    """
    在保持现有输入输出结构不变的前提下，按需调用大模型生成蓝图。

    - 通过环境变量 USE_LLM_BLUEPRINT 控制是否启用（值为 "1" 或 "true" 时启用）。
    - 若 LLM 生成失败，则回退到传入的 base_blueprint。
    """
    use_llm = os.environ.get("USE_LLM_BLUEPRINT", "").lower() in {"1", "true", "yes"}
    if not use_llm or not task_description.strip():
        return base_blueprint

    try:
        result: BlueprintResult = generate_blueprint_with_llm(
            model_name=model_name, task_description=task_description
        )
        blueprint = result.blueprint
        # 简单校验关键字段，避免前端崩溃
        if not isinstance(blueprint, dict):
            return base_blueprint
        if "behavior_tree" not in blueprint or "node_insights" not in blueprint:
            return base_blueprint
        return blueprint
    except Exception:
        # 出现任何异常都不影响原有逻辑，直接回退
        return base_blueprint


def build_behavior_tree(
    blueprint: dict, task_description: str, model_name: Optional[str] = None
):
    """根据蓝图和任务描述构建行为树"""
    # 对于越野物流模型，优先使用现有的规则动态生成
    if model_name == "越野物流" and task_description.strip():
        blueprint = generate_dynamic_blueprint(task_description)

    # 可选：使用大模型生成/替换蓝图（例如当正则解析能力不足时）
    blueprint = _maybe_use_llm_blueprint(
        model_name=model_name or "",
        task_description=task_description,
        base_blueprint=blueprint,
    )

    tree = copy.deepcopy(blueprint.get("behavior_tree", {}))
    description = (task_description or "等待输入的任务描述").strip()

    def _inject_summary(node):
        if not node:
            return
        if node.get("id") == tree.get("id"):
            node["summary"] = f"解析任务描述：{description}"
        for child in node.get("children", []):
            _inject_summary(child)

    _inject_summary(tree)
    return tree


def extract_node_insight(
    model_name: str,
    node_id: str,
    blueprint: Optional[dict] = None,
    task_description: Optional[str] = None,
):
    """从蓝图中提取节点描述"""
    if not node_id:
        node_id = "task_ingest"

    blueprint = blueprint or get_model_blueprint(model_name)

    # 对于越野物流模型，使用规则生成的蓝图作为基础
    if model_name == "越野物流" and task_description and task_description.strip():
        blueprint = generate_dynamic_blueprint(task_description)

    # 可选：在节点洞察请求场景下也允许通过 LLM 调整蓝图
    if task_description:
        blueprint = _maybe_use_llm_blueprint(
            model_name=model_name,
            task_description=task_description,
            base_blueprint=blueprint,
        )

    node_info = copy.deepcopy(
        blueprint.get("node_insights", {}).get(node_id, DEFAULT_NODE_INSIGHT)
    )

    return {
        "node_id": node_id,
        "model_name": model_name,
        "title": node_info.get("title", node_id),
        "summary": node_info.get("summary", ""),
        "key_points": node_info.get("key_points", []),
        "knowledge_trace": node_info.get("knowledge_trace", ""),
        "knowledge_graph": node_info.get("knowledge_graph")
    }


@app.route('/')
def index():
    """主页面"""
    return render_template('index.html', models=SUPPORT_MODELS)


@app.route('/api/models', methods=['GET'])
def get_models():
    """获取支援模型列表"""
    return jsonify({'models': SUPPORT_MODELS})


@app.route('/api/update', methods=['POST'])
def update():
    """根据任务描述生成行为树与策略依据"""
    data = request.json or {}
    model_name = _normalize_model_name(data.get('model_name', SUPPORT_MODELS[0]))
    task_description = data.get('task_description', '').strip()

    blueprint = get_model_blueprint(model_name)
    behavior_tree = build_behavior_tree(blueprint, task_description, model_name)
    default_node_id = blueprint.get('default_focus', behavior_tree.get('id'))
    node_insight = extract_node_insight(model_name, default_node_id, blueprint, task_description)

    return jsonify({
        'model_name': model_name,
        'task_description': task_description,
        'behavior_tree': behavior_tree,
        'insight': node_insight,
        'default_node_id': default_node_id
    })


@app.route('/api/node_insight', methods=['POST'])
def node_insight():
    """返回行为树节点对应的策略说明"""
    data = request.json or {}
    model_name = _normalize_model_name(data.get('model_name', SUPPORT_MODELS[0]))
    node_id = data.get('node_id')
    task_description = data.get('task_description', '')

    if not node_id:
        return jsonify({'error': 'node_id is required'}), 400

    return jsonify(extract_node_insight(model_name, node_id, task_description=task_description))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
