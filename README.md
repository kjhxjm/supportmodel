## 支援模型可视化演示系统

一个基于 Flask 和 G6 的支援模型推理可视化平台，支持动态任务解析、知识图谱展示，并可选接入大模型按测试大纲生成行为树蓝图。

### 🚀 快速开始

#### 环境要求
- Python 3.8+
- Flask
- 现代浏览器

#### 安装依赖

推荐使用虚拟环境：

```bash
pip install -r requirements.txt
```

#### 运行后端

```bash
python app.py

# 访问应用
# http://localhost:5000

gunicorn -w 2 -b 0.0.0.0:5000 app:app --daemon

```




#### （可选）启用大模型生成蓝图

如果希望让系统根据《测试任务说明书》（`instruction/outline.md` + `instruction/task.md`）中 20 条测试项目自动生成行为树，并结合真实任务描述自动补全推理链条，可以配置以下环境变量：

```bash
# 必选：大模型服务地址和 API Key（示例为 GLM）
export GLM_BASE_URL="https://xxx"      # 你的 GLM / OpenAI 兼容接口地址
export GLM_API_KEY="sk-xxx"            # 你的 API Key

# 可选：模型名称，缺省为 glm-4-flash
export GLM_MODEL_NAME="glm-4-flash"

# 开启 LLM 蓝图生成（不配置则完全沿用现有规则/静态蓝图）
export USE_LLM_BLUEPRINT=1
```

> 未配置上述变量时，系统仍按原有静态/规则蓝图正常工作，接口结构不变。

### 📋 接口设计

#### 核心架构

```text
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

#### API 接口

##### GET /api/models
获取所有可用支援模型列表
```json
{
  "models": ["越野物流", "设备投放", "伤员救助", ...]
}
```

##### POST /api/update
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

##### POST /api/node_insight
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

### 🧠 LLM 集成与测试场景 one-shot

系统内置了对《测试大纲》中 20 条支援模型测试项目的结构化描述，位于：

- `instruction/outline.md`：给出 5 类支援模型 × 20 个测试项目的结构化表格
- `instruction/task.md`：对每个测试项目给出 **测试目标 + 示例输入 + 期望推理链条**
- `support_models/scenarios.py`：将上述内容编码为 `Scenario` 对象（`model_name + example_input + reasoning_chain`）

当环境变量 `USE_LLM_BLUEPRINT=1` 时，后端会在不改变接口入参/出参结构的前提下，按以下流程可选接入大模型：

- 根据前端传入的 `model_name` 与 `task_description`，在 `SCENARIOS` 中找到语义上最相近的测试任务条目（基于 `example_input` 相似度）
- 将匹配到的条目（示例输入 + 期待的推理链条）作为 **one-shot 提示** 合并进大模型的 system / user 提示词
- 要求大模型直接输出一个合法的 `BLUEPRINT` JSON（含 `behavior_tree` + `node_insights`），结构与 `base.py` 中定义的完全一致
- 如果解析失败或结果不完整，则自动回退到原有蓝图逻辑（静态/规则生成），对前端透明

当前已覆盖的 30 条测试项目包括（示例）：

- **越野物流**：任务编组、动态路径规划与重规划、货物状态监控与保全、车队协同与效率调度
- **设备投放**：任务编组、高精度目标定位、自主装卸控制、投放确认
- **伤员救助**：任务编组、远程伤情初步评估与分类、近程伤情评估、伤情数据同步
- **人员输送**：任务编组、舒适连续导航路径规划、人员与环境安全监控、多目的地协同调度
- **资源保障**：资源追踪、需求分配建议、补给任务生成与调度、资源消耗预测与规划
- **后勤物资管控**：资源入库、资源盘点、资源出库、资源维护

前端仍然只需调用 `/api/update` 和 `/api/node_insight`，无需感知是否启用了大模型。

### 🛠️ 开发新模型

#### 1. 创建模型文件

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

#### 2. 注册模型

在 `support_models/__init__.py` 中注册：

```python
# 添加导入
from .your_model import YOUR_BLUEPRINT

# 添加到模型列表
SUPPORT_MODELS.append("你的模型名称")

# 添加到蓝图字典
_BLUEPRINTS["你的模型名称"] = YOUR_BLUEPRINT
```

#### 3. 蓝图数据结构

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

### 🎨 高级功能

#### 动态任务解析

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

#### 知识图谱可视化

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

### 📚 学习资源

1. **基础模型**: 查看 `base.py` 了解核心数据结构
2. **动态模型**: 参考 `offroad_logistics.py` 学习动态生成
3. **静态模型**: 参考 `casualty_rescue.py` 学习静态配置
4. **前端交互**: 查看 `static/js/main.js` 了解UI逻辑

### 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

💡 **提示**: 从 `offroad_logistics.py` 开始学习，它展示了最完整的动态模型开发模式！</content>
</xai:function_call">README.md
