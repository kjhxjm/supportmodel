// 全局状态
let currentState = {
    model_name: '越野物流',
    task_description: ''
};

let selectedNodeId = null;
let currentTreeScale = 1;
let graphObj = null; // G6图实例
let insightGraphObj = null; // 右侧知识图谱G6实例

document.addEventListener('DOMContentLoaded', () => {
    initializeControls();
    updateDisplay();
});

function initializeControls() {
    const modelSelect = document.getElementById('modelSelect');
    const taskInput = document.getElementById('taskInput');
    const startReasoning = document.getElementById('startReasoning');
    const zoomInBtn = document.getElementById('treeZoomIn');
    const zoomOutBtn = document.getElementById('treeZoomOut');
    const behaviorTree = document.getElementById('behaviorTree');

    if (modelSelect) {
        currentState.model_name = modelSelect.value;
        modelSelect.addEventListener('change', () => {
            currentState.model_name = modelSelect.value;
            currentState.task_description = taskInput ? taskInput.value.trim() : currentState.task_description;
            updateStatus(true);
            updateDisplay();
        });
    }

    if (startReasoning) {
        startReasoning.addEventListener('click', () => {
            currentState.task_description = taskInput ? taskInput.value.trim() : '';
            updateStatus(true);
            updateDisplay();
        });
    }

    // 缩放按钮
    if (zoomInBtn) {
        zoomInBtn.addEventListener('click', () => {
            setTreeScale(currentTreeScale + 0.1);
        });
    }

    if (zoomOutBtn) {
        zoomOutBtn.addEventListener('click', () => {
            setTreeScale(currentTreeScale - 0.1);
        });
    }

    // Ctrl + 滚轮缩放
    if (behaviorTree) {
        behaviorTree.addEventListener('wheel', (e) => {
            if (!e.ctrlKey) return;
            e.preventDefault();
            const delta = e.deltaY < 0 ? 0.05 : -0.05;
            setTreeScale(currentTreeScale + delta);
        }, { passive: false });

        // === 新增：树形结构拖动功能 ===
        let isDragging = false;
        let startX, startY;
        let initialLeft, initialTop;
        const treeInner = behaviorTree.querySelector('#treeInner');

        // 初始化拖动样式
        behaviorTree.style.cursor = 'grab';
        treeInner.style.position = 'absolute';

        behaviorTree.addEventListener('mousedown', (e) => {
            if (e.ctrlKey || e.target !== behaviorTree) return;
            e.preventDefault();
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            initialLeft = parseFloat(treeInner.style.left) || 0;
            initialTop = parseFloat(treeInner.style.top) || 0;
            behaviorTree.style.cursor = 'grabbing';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            e.preventDefault();
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            treeInner.style.left = `${initialLeft + dx}px`;
            treeInner.style.top = `${initialTop + dy}px`;
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
            behaviorTree.style.cursor = 'grab';
        });
    }

    updateStatus(false);
}

function updateStatus(isRunning) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');

    if (!indicator || !statusText) return;

    if (isRunning) {
        indicator.classList.add('active');
        statusText.textContent = '模型在线 | 推理中...';
    } else {
        indicator.classList.remove('active');
        statusText.textContent = '待机中 | 常规逻辑';
    }
}

function updateDisplay() {
    fetch('/api/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentState)
    })
        .then(res => res.json())
        .then(data => {
            renderBehaviorTree(data.behavior_tree);
            selectedNodeId = data.default_node_id;
            updateInsightPanel(data.insight);
            highlightSelectedNode(selectedNodeId);
            autoScaleTree(data.behavior_tree);
            updateStatus(false);
        })
        .catch(err => {
            console.error('update error:', err);
            updateStatus(false);
        });
}

function renderBehaviorTree(treeData) {
    const container = document.getElementById('behaviorTree');
    if (!container) return;

    if (!treeData || !treeData.id) {
        container.innerHTML = '<p class="placeholder">暂未生成行为树，请输入任务描述并开始推理。</p>';
        if (graphObj) {
            graphObj.destroy();
            graphObj = null;
        }
        return;
    }

    // 转换数据格式为G6所需的格式
    const graphData = convertToG6Format(treeData);

    if (!graphObj) {
        // 初始化G6树图
        graphObj = new G6.TreeGraph({
            container: container,
            width: container.offsetWidth,
            height: container.offsetHeight,
            linkCenter: true,
            modes: {
                default: [
                    'drag-canvas',
                    'zoom-canvas',
                ],
            },
            defaultNode: {
                size: 60,
                anchorPoints: [
                    [0, 0.5],
                    [1, 0.5],
                ],
                style: {
                    stroke: '#E0E0E0',
                    lineWidth: 2,
                }
            },
            defaultEdge: {
                type: 'cubic-vertical',
                style: {
                    stroke: '#90CAF9',
                    lineWidth: 2,
                }
            },
            layout: {
                type: 'compactBox',
                direction: 'TB',
                getId: function getId(d) {
                    return d.id;
                },
                getHeight: function getHeight() {
                    return 60;
                },
                getWidth: function getWidth() {
                    return 120;
                },
                getVGap: function getVGap() {
                    return 80;
                },
                getHGap: function getHGap() {
                    return 30;
                },
            },
        });

        // 自定义节点渲染
        graphObj.node((node) => {
            const nodeType = getNodeType(node);
            const nodeColor = getNodeColor(node.status);

            // 检查是否有子节点
            const nodeData = node.data || {};
            const hasChildren = nodeData.children && nodeData.children.length > 0;

            return {
                label: node.label || node.id,
                style: {
                    fill: nodeColor.background,
                    stroke: nodeColor.border,
                    lineWidth: 3,
                    cursor: hasChildren ? 'pointer' : 'default', // 有子节点时显示pointer光标
                },
                labelCfg: {
                    position: 'center',
                    style: {
                        fill: '#37474F',
                        fontSize: 12,
                        fontWeight: 600,
                        textAlign: 'center',
                    },
                },
                // 添加节点类型徽章 - 暂时禁用图标以避免404错误
                // icon: {
                //     show: true,
                //     img: getNodeTypeIcon(nodeType),
                //     width: 20,
                //     height: 20,
                //     offset: [0, -25]
                // },
            };
        });

        // 绑定节点点击事件 - 单次点击查看详情
        graphObj.on('node:click', (evt) => {
            const node = evt.item;
            const model = node.getModel();
            fetchNodeInsight(model.id);
        });

        // 绑定节点鼠标事件
        let clickTimer = null;

        // 鼠标悬停显示提示
        graphObj.on('node:mouseenter', (evt) => {
            const node = evt.item;
            const model = node.getModel();
            const nodeData = model.data || {};
            const hasChildren = nodeData.children && nodeData.children.length > 0;

            // 改变边框颜色表示可交互
            model.style = model.style || {};
            model.style.stroke = '#2196F3'; // 蓝色边框
            model.style.lineWidth = 4;
            graphObj.updateItem(node, model);

            // 更新鼠标样式
            evt.target.style.cursor = hasChildren ? 'pointer' : 'default';
        });

        graphObj.on('node:mouseleave', (evt) => {
            const node = evt.item;
            const model = node.getModel();
            const nodeColor = getNodeColor(model.status);

            // 恢复原始边框
            model.style = model.style || {};
            model.style.stroke = nodeColor.border;
            model.style.lineWidth = 3;
            graphObj.updateItem(node, model);
        });

        // 单次点击查看详情
        graphObj.on('node:click', (evt) => {
            // 清除之前的定时器
            if (clickTimer) {
                clearTimeout(clickTimer);
            }

            // 设置延迟，区分单双击
            clickTimer = setTimeout(() => {
                const node = evt.item;
                const model = node.getModel();
                fetchNodeInsight(model.id);
            }, 200); // 200ms延迟
        });

        // 双击展开/折叠
        graphObj.on('node:dblclick', (evt) => {
            // 清除单击定时器
            if (clickTimer) {
                clearTimeout(clickTimer);
                clickTimer = null;
            }

            const node = evt.item;
            const model = node.getModel();

            // 检查节点是否有子节点
            const hasChildren = model.children && model.children.length > 0;

            if (!hasChildren) {
                return; // 叶子节点不需要展开/折叠
            }

            // 使用G6的collapseExpand方法
            const currentCollapsed = model.collapsed;
            graphObj.collapseExpand(node, !currentCollapsed);

            // 重新布局
            setTimeout(() => {
                graphObj.fitView();
            }, 200);
        });

        graphObj.data(graphData);
        graphObj.render();
        graphObj.fitView();
    } else {
        // 更新数据
        graphObj.data(graphData);
        graphObj.render();
        graphObj.fitView();
    }
}

// 数据转换：将现有格式转换为G6格式
function convertToG6Format(node) {
    return {
        id: node.id,
        label: node.label || node.id,
        status: node.status || 'pending',
        summary: node.summary || '',
        collapsed: false,  // 默认展开
        children: node.children ? node.children.map(convertToG6Format) : []
    };
}

function getNodeType(node) {
    // 根据节点ID或位置确定节点类型
    if (node.id === 'task_ingest') return 'root';
    if (node.children && node.children.length > 1) return 'selector'; // 多分支选择
    if (node.children && node.children.length === 1) return 'sequence'; // 单分支序列
    if (!node.children || node.children.length === 0) return 'action'; // 叶子节点动作
    return 'composite'; // 复合节点
}

function getNodeTypeIcon(type) {
    // 返回节点类型对应的图标URL或SVG
    // 这里暂时使用文字图标，后续可以替换为实际的图标
    const icons = {
        'root': '⚡',
        'selector': '🔀',
        'sequence': '➡️',
        'action': '🎯',
        'composite': '🔧'
    };
    return icons[type] || '📋';
}

function getNodeColor(status) {
    const colors = {
        'completed': { background: '#E8F5E8', border: '#4CAF50' },
        'active': { background: '#E3F2FD', border: '#1976D2' },
        'pending': { background: '#FFF3E0', border: '#FF9800' },
        'selected': { background: '#FFEBEE', border: '#FF5722' }
    };
    return colors[status] || { background: '#FAFAFA', border: '#E0E0E0' };
}

function fetchNodeInsight(nodeId) {
    if (!nodeId) return;
    highlightSelectedNode(nodeId);
    fetch('/api/node_insight', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            model_name: currentState.model_name,
            node_id: nodeId,
            task_description: currentState.task_description
        })
    })
        .then(res => res.json())
        .then(data => {
            selectedNodeId = nodeId;
            updateInsightPanel(data);
        })
        .catch(err => console.error('node insight error:', err));
}

function highlightSelectedNode(nodeId) {
    if (!graphObj) return;

    // 清除所有节点的选中状态
    const nodes = graphObj.getNodes();
    nodes.forEach(node => {
        const model = node.getModel();
        model.style = model.style || {};
        model.style.stroke = getNodeColor(model.status).border;
        model.style.lineWidth = 3;
        graphObj.updateItem(node, model);
    });

    // 高亮选中的节点
    const selectedNode = nodes.find(node => node.getModel().id === nodeId);
    if (selectedNode) {
        const model = selectedNode.getModel();
        model.style = model.style || {};
        model.style.stroke = '#FF5722';
        model.style.lineWidth = 4;
        graphObj.updateItem(selectedNode, model);
    }
}

function updateInsightPanel(insight) {
    const graphContainer = document.getElementById('insightGraphContainer');
    const textContainer = document.getElementById('insightTextContainer');

    // 渲染知识图谱
    if (insight && insight.knowledge_graph) {
        renderInsightGraph(insight.knowledge_graph);
    } else {
        if (graphContainer) graphContainer.style.display = 'none';
    }

    // 渲染文本内容
    if (!insight || insight.error) {
        textContainer.innerHTML = '<p class="placeholder">未找到该节点的策略依据，请重新选择。</p>';
        return;
    }

    const keyPoints = (insight.key_points || [])
        .map(item => `<li>${item}</li>`)
        .join('');

    textContainer.innerHTML = `
        <div class="insight-title">${insight.title}</div>
        <p class="insight-summary">${insight.summary || ''}</p>
        ${keyPoints ? `<ul class="key-points">${keyPoints}</ul>` : ''}
        <div class="insight-trace">${insight.knowledge_trace || ''}</div>
    `;
}

// ===== 缩放相关 =====

function setTreeScale(scale) {
    if (!graphObj) return;

    currentTreeScale = Math.max(0.3, Math.min(scale, 1.6));
    graphObj.zoomTo(currentTreeScale);

    const label = document.getElementById('treeZoomLabel');
    if (label) {
        label.textContent = `${Math.round(currentTreeScale * 100)}%`;
    }
}

function autoScaleTree(treeData) {
    // G6有自己的fitView功能，这里主要确保图表正确适应容器
    if (graphObj && treeData && treeData.id) {
        // 延迟执行以确保渲染完成
        setTimeout(() => {
            graphObj.fitView();
        }, 100);
    }
}

function getTreeDepth(node) {
    if (!node || !node.children || node.children.length === 0) return 1;
    let maxChild = 0;
    node.children.forEach(child => {
        maxChild = Math.max(maxChild, getTreeDepth(child));
    });
    return 1 + maxChild;
}

function getMaxBreadth(root) {
    if (!root) return 0;
    let maxBreadth = 0;
    const queue = [root];

    while (queue.length) {
        const levelSize = queue.length;
        maxBreadth = Math.max(maxBreadth, levelSize);
        for (let i = 0; i < levelSize; i++) {
            const node = queue.shift();
            if (node.children && node.children.length) {
                node.children.forEach(child => queue.push(child));
            }
        }
    }
    return maxBreadth;
}

// ===== 右侧知识图谱相关 =====

function renderInsightGraph(graphData) {
    const container = document.getElementById('insightGraphContainer');
    if (!container) return;

    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
        container.style.display = 'none';
        return;
    }

    container.style.display = 'block';

    // 转换数据格式为G6所需的格式
    const g6Data = convertInsightToG6Format(graphData);

    if (!insightGraphObj) {
        // 初始化G6知识图谱
        insightGraphObj = new G6.Graph({
            container: container,
            width: container.offsetWidth - 10, // 留边距避免滚动条
            height: container.offsetHeight - 10, // 留边距
            linkCenter: true,
            modes: {
                default: ['drag-canvas', 'zoom-canvas'],
            },
            defaultNode: {
                size: 80,
                anchorPoints: [
                    [0, 0.5],
                    [1, 0.5],
                ],
                style: {
                    stroke: '#E0E0E0',
                    lineWidth: 2,
                }
            },
            defaultEdge: {
                type: 'cubic-horizontal',
                style: {
                    stroke: '#90CAF9',
                    lineWidth: 2,
                    endArrow: true,
                }
            },
            layout: {
                type: 'force',
                linkDistance: 120,  // 边长度 - 适当减小让布局更紧凑
                nodeStrength: -300, // 节点排斥力 - 减小让布局更快稳定
                edgeStrength: 0.6,  // 边吸引力 - 增强让节点更快就位
                preventOverlap: true, // 防止重叠
                nodeSize: 80, // 节点大小
                gravity: 20, // 增强重力让布局更快收敛到中心
                maxIteration: 1000, // 增加最大迭代次数确保收敛
            },
        });

        // 自定义节点渲染
        insightGraphObj.node((node) => {
            const nodeType = node.type || 'process';
            const nodeColor = getInsightNodeColor(nodeType);

            return {
                label: node.label || node.id,
                style: {
                    fill: nodeColor.background,
                    stroke: nodeColor.border,
                    lineWidth: 2,
                },
                labelCfg: {
                    position: 'center',
                    style: {
                        fill: '#37474F',
                        fontSize: 12,
                        fontWeight: 500,
                        textAlign: 'center',
                    },
                },
            };
        });
    }

    insightGraphObj.data(g6Data);
    insightGraphObj.render();

    // 力导向布局需要时间来稳定，延迟执行fitView
    setTimeout(() => {
        insightGraphObj.fitView({
            padding: 20,  // 添加内边距
            includeEdges: true  // 包含边框计算
        });
    }, 500);  // 等待500ms让布局稳定
}

function convertInsightToG6Format(graphData) {
    return {
        nodes: graphData.nodes.map(node => ({
            id: node.id,
            label: node.label,
            type: node.type || 'process',
        })),
        edges: graphData.edges.map(edge => ({
            source: edge.source,
            target: edge.target,
        }))
    };
}

function getInsightNodeColor(type) {
    const colors = {
        'input': { background: '#E8F5E8', border: '#4CAF50' },
        'process': { background: '#E3F2FD', border: '#1976D2' },
        'decision': { background: '#FFF3E0', border: '#FF9800' },
        'output': { background: '#F3E5F5', border: '#9C27B0' }
    };
    return colors[type] || { background: '#FAFAFA', border: '#E0E0E0' };
}
