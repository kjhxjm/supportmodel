# 支援模型可视化演示系统

一个基于Flask和G6的支援模型推理可视化平台，支持动态任务解析和知识图谱展示。

## 🚀 快速开始

### 环境要求
- Python 3.6+
- Flask
- 现代浏览器

### 安装运行
```bash
# 安装依赖
pip3 install flask

# 启动服务
python3 app.py

# 访问应用
# http://localhost:5000
```

## 📋 接口设计

### 核心架构

```
📁 support_models/          # 支援模型核心
├── __init__.py            # 模型注册中心
├── base.py                # 基础框架和接口规范
├── offroad_logistics.py   # 越野物流模型 ⭐ 推荐参考
├── casualty_rescue.py     # 伤员救助模型
└── ...                   # 其他模型

📁 templates/              # 前端模板
📁 static/                 # 静态资源
└── app.py                # Flask应用主入口
```

### API接口

#### GET /api/models
获取所有可用支援模型列表
```json
{
  "models": ["越野物流", "设备投放", "伤员救助", ...]
}
```

#### POST /api/update
根据任务描述生成行为树和策略依据
```json
// 请求
{
  "model_name": "越野物流",
  "task_description": "向位置X运输资源Y，道路存在不确定损毁风险，要求2小时内送达。"
}

// 响应
{
  "model_name": "越野物流",
  "task_description": "向位置X运输资源Y，道路存在不确定损毁风险，要求2小时内送达。",
  "behavior_tree": {...},
  "insight": {...},
  "default_node_id": "fleet_formation"
}
```

#### POST /api/node_insight
获取特定节点的详细洞察信息
```json
// 请求
{
  "model_name": "越野物流",
  "node_id": "fleet_formation",
  "task_description": "向位置X运输资源Y..."
}

// 响应
{
  "node_id": "fleet_formation",
  "model_name": "越野物流",
  "title": "车队编成推理结果",
  "summary": "✅ 最终方案：使用2辆中型越野无人车...",
  "key_points": [...],
  "knowledge_trace": "...",
  "knowledge_graph": {...}
}
```

## 🛠️ 开发新模型

### 1. 创建模型文件

在 `support_models/` 目录下创建新文件：

```python
# support_models/your_model.py
from .base import build_generic_blueprint

# 方式1: 使用通用模板（推荐新手）
YOUR_BLUEPRINT = build_generic_blueprint(
    root_label="你的模型名称",
    root_summary="模型功能描述",
    node_insight_overrides={
        "environment_scan": {
            "summary": "你的环境分析逻辑",
            "key_points": ["要点1", "要点2"],
            "knowledge_trace": "推理过程"
        }
    }
)

# 方式2: 完全自定义（高级用户）
def generate_dynamic_blueprint(task_description):
    """动态生成蓝图"""
    parsed_info = parse_task_description(task_description)
    # 自定义逻辑...
    return customized_blueprint

# 导出
__all__ = ["YOUR_BLUEPRINT"]
```

### 2. 注册模型

在 `support_models/__init__.py` 中注册：

```python
# 添加导入
from .your_model import YOUR_BLUEPRINT

# 添加到模型列表
SUPPORT_MODELS.append("你的模型名称")

# 添加到蓝图字典
_BLUEPRINTS["你的模型名称"] = YOUR_BLUEPRINT
```

### 3. 蓝图数据结构

```python
BLUEPRINT = {
    "default_focus": "main_node_id",  # 默认聚焦节点

    "behavior_tree": {                # 行为树结构
        "id": "root_node",
        "label": "根节点名称",
        "status": "active",
        "summary": "节点描述",
        "children": [
            {
                "id": "child_node",
                "label": "子节点名称",
                "status": "pending",
                "summary": "子节点描述",
                "children": []
            }
        ]
    },

    "node_insights": {                 # 节点洞察信息
        "root_node": {
            "title": "节点标题",
            "summary": "详细描述",
            "key_points": ["关键要点1", "关键要点2"],
            "knowledge_trace": "推理过程说明",
            "knowledge_graph": {       # 可选：知识图谱
                "nodes": [
                    {"id": "node1", "label": "节点1", "type": "input"},
                    {"id": "node2", "label": "节点2", "type": "process"}
                ],
                "edges": [
                    {"source": "node1", "target": "node2"}
                ]
            }
        }
    }
}
```

## 🎨 高级功能

### 动态任务解析

```python
def parse_task_description(task_description):
    """解析自然语言任务描述"""
    parsed_info = {
        "destination": None,
        "cargo": None,
        "time_limit": None,
        "road_conditions": [],
        "special_requirements": []
    }
    # 正则表达式解析逻辑...
    return parsed_info
```

### 知识图谱可视化

支持在节点洞察中嵌入交互式知识图谱：

```python
"knowledge_graph": {
    "nodes": [
        {"id": "input", "label": "输入数据", "type": "input"},
        {"id": "process", "label": "推理过程", "type": "process"},
        {"id": "decision", "label": "决策点", "type": "decision"},
        {"id": "output", "label": "输出结果", "type": "output"}
    ],
    "edges": [
        {"source": "input", "target": "process"},
        {"source": "process", "target": "decision"},
        {"source": "decision", "target": "output"}
    ]
}
```

## 📚 学习资源

1. **基础模型**: 查看 `base.py` 了解核心数据结构
2. **动态模型**: 参考 `offroad_logistics.py` 学习动态生成
3. **静态模型**: 参考 `casualty_rescue.py` 学习静态配置
4. **前端交互**: 查看 `static/js/main.js` 了解UI逻辑

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

💡 **提示**: 从 `offroad_logistics.py` 开始学习，它展示了最完整的动态模型开发模式！</content>
</xai:function_call">README.md
