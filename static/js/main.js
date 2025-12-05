// 全局状态
let currentState = {
    task_description: '',
    node_insights: {}  // 缓存后端一次性返回的所有节点洞察
};

let selectedNodeId = null;
let currentTreeScale = 1;
let graphObj = null; // G6图实例
let insightGraphObj = null; // 右侧知识图谱G6实例

document.addEventListener('DOMContentLoaded', () => {
    initializeControls();
    registerShortcuts();
    
    // 检查URL参数，如果有input参数则自动填充并触发推理
    const urlParams = new URLSearchParams(window.location.search);
    const inputParam = urlParams.get('input');
    const controlPanel = document.querySelector('.control-panel');
    const header = document.querySelector('.header');
    
    if (inputParam) {
        const taskInput = document.getElementById('taskInput');
        if (taskInput) {
            // 解码URL参数（处理URL编码）
            const decodedInput = decodeURIComponent(inputParam);
            taskInput.value = decodedInput;
            // 自动触发推理
            currentState.task_description = decodedInput.trim();
            updateStatus(true);
            updateDisplay();
        }

        // 如果通过URL携带了 input 参数，则隐藏任务输入面板
        if (controlPanel) controlPanel.style.display = 'none';
        if (header) header.style.display = 'none';
    } else {
        // 没有URL参数时，正常更新显示
        updateDisplay();
    }
});

function initializeControls() {
    const taskInput = document.getElementById('taskInput');
    const startReasoning = document.getElementById('startReasoning');
    const zoomInBtn = document.getElementById('treeZoomIn');
    const zoomOutBtn = document.getElementById('treeZoomOut');
    const behaviorTree = document.getElementById('behaviorTree');

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

// 快捷键：Ctrl + 数字键填充示例任务并自动推理
function registerShortcuts() {
    const taskInput = document.getElementById('taskInput');
    const shortcutInputs = {
        '1': '向位置X运输资源Y，道路存在不确定损毁风险，要求Z小时内送达。',
        '2': '向X位置运输资源Y，道路可能受损',
        '3': '向X位置运输冷冻食品Y',
        '4': '向X位置运输4车食品和水',
        '5': '向X前沿阵地投放侦察装置Y，需要多架无人机协同运输',
        '6': '向X区域精确投放传感器Y',
        '7': '将设备Y通过无人车运输至X点，并由机械臂自主卸载',
        '8': '将侦察节点Y投放至X点并确认部署成功',
        '9': '在X区域发现两名伤员，需要无人救援设备前往救助并运回安全点',
        '0': '对X位置可能受伤的人员进行远程伤情初判',
    };

    document.addEventListener('keydown', (e) => {
        if (!e.ctrlKey || e.altKey || e.metaKey) return;
        const key = e.key;
        if (!shortcutInputs[key]) return;

        e.preventDefault();
        e.stopPropagation();

        const presetText = shortcutInputs[key];
        if (taskInput) {
            taskInput.value = presetText;
        }
        currentState.task_description = presetText.trim();
        updateStatus(true);
        updateDisplay();
    });
}

function updateStatus(isRunning) {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    const loadingMask = document.getElementById('loadingMask');
    const startReasoningBtn = document.getElementById('startReasoning');

    if (!indicator || !statusText) return;

    if (isRunning) {
        indicator.classList.add('active');
        statusText.textContent = '推理中...';
        if (loadingMask) loadingMask.style.display = 'flex';
        if (startReasoningBtn) {
            startReasoningBtn.disabled = true;
            startReasoningBtn.textContent = '推理中...';
        }
    } else {
        indicator.classList.remove('active');
        statusText.textContent = '';
        if (loadingMask) loadingMask.style.display = 'none';
        if (startReasoningBtn) {
            startReasoningBtn.disabled = false;
            startReasoningBtn.textContent = '开始推理';
        }
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
            // ===== 调试输出：后端返回的整体数据 =====
            console.log('[updateDisplay] response data:', data);

            // 缓存节点洞察，后续点击节点时不再请求后端
            currentState.node_insights = data.node_insights || {};

            // ===== 调试输出：行为树与节点洞察 =====
            console.log('[updateDisplay] behavior_tree:', data.behavior_tree);
            console.log('[updateDisplay] node_insights:', currentState.node_insights);

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

    // 转换数据格式为G6所需的格式（带是否有知识图谱的标记）
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
                    'drag-node',
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

            const hasKnowledgeGraph = !!node.hasKnowledgeGraph;

            return {
                label: node.label || node.id,
                size: hasKnowledgeGraph ? 80 : 60, // 带知识图谱的节点放大显示
                style: {
                    fill: nodeColor.background,
                    stroke: hasKnowledgeGraph ? '#FF5722' : nodeColor.border,
                    lineWidth: hasKnowledgeGraph ? 4 : 3,
                    cursor: hasKnowledgeGraph ? 'pointer' : 'default',
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
            };
        });

        // 绑定节点鼠标事件
        let clickTimer = null;

        // 鼠标悬停高亮（仅对有知识图谱的节点）
        graphObj.on('node:mouseenter', (evt) => {
            const node = evt.item;
            const model = node.getModel();
            const hasKnowledgeGraph = !!model.hasKnowledgeGraph;

            if (!hasKnowledgeGraph) {
                return;
            }

            model.style = model.style || {};
            model.style.stroke = '#FF7043'; // 橙色高亮
            model.style.lineWidth = 5;
            graphObj.updateItem(node, model);
        });

        graphObj.on('node:mouseleave', (evt) => {
            const node = evt.item;
            const model = node.getModel();
            const nodeColor = getNodeColor(model.status);
            const hasKnowledgeGraph = !!model.hasKnowledgeGraph;

            model.style = model.style || {};
            model.style.stroke = hasKnowledgeGraph ? '#FF5722' : nodeColor.border;
            model.style.lineWidth = hasKnowledgeGraph ? 4 : 3;
            graphObj.updateItem(node, model);
        });

        // 单次点击查看详情（仅对带知识图谱的节点生效）
        graphObj.on('node:click', (evt) => {
            // 清除之前的定时器
            if (clickTimer) {
                clearTimeout(clickTimer);
            }

            clickTimer = setTimeout(() => {
                const node = evt.item;
                const model = node.getModel();
                const hasKnowledgeGraph = !!model.hasKnowledgeGraph;
                if (!hasKnowledgeGraph) {
                    return; // 无知识图谱时不支持点击
                }
                showNodeInsightFromCache(model.id);
            }, 200);
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
    const nodeId = node.id;
    const insight = (currentState.node_insights || {})[nodeId];
    const hasKnowledgeGraph = !!(insight && insight.knowledge_graph);

    return {
        id: nodeId,
        label: node.label || nodeId,
        status: node.status || 'pending',
        summary: node.summary || '',
        hasKnowledgeGraph: hasKnowledgeGraph,
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

// 使用本地缓存的节点洞察展示策略依据与知识图谱
function showNodeInsightFromCache(nodeId) {
    if (!nodeId) return;
    const insight = (currentState.node_insights || {})[nodeId];
    if (!insight || !insight.knowledge_graph) {
        return; // 没有知识图谱则不响应点击
    }
    selectedNodeId = nodeId;
    highlightSelectedNode(nodeId);
    updateInsightPanel(insight);
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

    // ===== 调试输出：当前节点洞察 =====
    console.log('[updateInsightPanel] insight:', insight);

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

    // ===== 调试输出：原始知识图谱数据 =====
    console.log('[renderInsightGraph] raw graphData:', graphData);

    if (!graphData || !graphData.nodes || graphData.nodes.length === 0) {
        console.warn('[renderInsightGraph] empty knowledge_graph, skip render.');
        container.style.display = 'none';
        return;
    }

    container.style.display = 'block';

    // 转换数据格式为G6所需的格式
    const g6Data = convertInsightToG6Format(graphData);

    // ===== 调试输出：转换后的G6数据 =====
    console.log('[renderInsightGraph] g6Data for G6:', g6Data);

    if (!insightGraphObj) {
        // 初始化G6知识图谱
        insightGraphObj = new G6.Graph({
            container: container,
            width: container.offsetWidth - 10, // 留边距避免滚动条
            height: container.offsetHeight - 10, // 留边距
            linkCenter: true,
            modes: {
                // 允许拖动画布、缩放画布，以及直接拖动节点
                default: ['drag-canvas', 'zoom-canvas', 'drag-node'],
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
    const nodes = Array.isArray(graphData.nodes) ? graphData.nodes : [];
    const edges = Array.isArray(graphData.edges) ? graphData.edges : [];

    return {
        nodes: nodes.map(node => ({
            id: node.id,
            label: node.label,
            type: node.type || 'process',
        })),
        edges: edges.map(edge => ({
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
