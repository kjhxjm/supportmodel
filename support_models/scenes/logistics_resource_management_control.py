from typing import List
from .schema import Scenario

# 六、后勤资源管控支援模型测试
SCENARIOS: List[Scenario] = [
    # 21. 资源入库
    Scenario(
        id="resource_inbound_processing",  # 21. 资源入库
        model_name="后勤资源管控",
        name="资源入库",
        example_input="新到达一批医疗物资X，需要入库保管。",
        reasoning_chain="物资属性解析（类型、数量、体积、保存条件）→ 仓储类型匹配（冷藏区/常温区/危险品区）→ 仓位推荐（按剩余容量、出入库频次、同类物资位置匹配）→ 入库登记（生成标签、记录批次与有效期）",
        prompt=(
            "【后勤资源管控-资源入库专项要求（详细输出版）】\n"
            "\n"
            "=== 一、行为树结构要求 ===\n"
            "1. 行为树必须至少包含以下核心节点，且严格按照推理链条自上而下展开：\n"
            "   - task_analysis（任务分析与解析，根节点）：\n"
            "       * 明确物资名称、数量、来源、入库时间要求等基础信息；\n"
            "       * 至少拆分出\"物资信息提取\"和\"入库需求识别\"两个子层级节点；\n"
            "   - material_attribute_parsing（物资属性解析）：\n"
            "       * 至少包含 type_identification（类型识别）、quantity_volume_analysis（数量体积分析）、storage_condition_analysis（保存条件分析）三个子节点；\n"
            "   - warehouse_type_matching（仓储类型匹配）：\n"
            "       * 根据物资属性匹配对应的仓储区域（冷藏区/常温区/危险品区/特殊存储区）；\n"
            "   - position_recommendation（仓位推荐，核心决策节点）：\n"
            "       * 下方必须细化出 capacity_analysis（剩余容量分析）、frequency_analysis（出入库频次分析）、similar_material_location（同类物资位置匹配）三个子节点；\n"
            "       * 该节点必须包含 knowledge_graph 字段。\n"
            "   - inventory_recording（入库登记）：\n"
            "       * 生成入库标签、记录批次号、有效期、登记时间等信息。\n"
            "\n"
            "2. behavior_tree 中每个节点的格式要求：\n"
            "   - label 字段：必须包含具体数值结果，格式示例：\"📦 物资属性解析：医疗物资X，数量50箱，体积2.5m³\"、\"✅ 仓储类型匹配：常温区\"、\"✅ 仓位推荐：A区-3号货架-2层\"；\n"
            "   - summary 字段：必须包含具体数值、数量、体积、位置等量化信息，不能使用空泛描述。例如：\n"
            "     * 正确示例：\"解析医疗物资X的属性：类型为急救药品，数量50箱，总体积2.5m³，需在常温（15-25℃）条件下保存，有效期至2025年12月。\"\n"
            "     * 错误示例：\"识别物资的基本属性\"（过于空泛，缺少具体数值）\n"
            "\n"
            "=== 二、knowledge_graph 要求 ===\n"
            "position_recommendation 节点的 knowledge_graph 必须体现完整因果链路：\n"
            "物资属性解析(material_parsing) → 仓储类型匹配(warehouse_matching) → 容量分析(capacity_analysis) → 频次分析(frequency_analysis) → 位置匹配(location_matching) → 仓位推荐(position_recommendation)\n"
            "\n"
            "具体要求：\n"
            "- nodes[].label 必须包含具体参数信息，格式：\"节点名称(具体参数1, 具体参数2, ...)\"\n"
            "  示例：\"物资属性解析(医疗物资X, 50箱, 2.5m³, 常温保存)\"、\"仓储类型匹配(常温区)\"、\"仓位推荐(A区-3号货架-2层)\"\n"
            "- nodes[].type 必须明确标注：input（输入）、process（处理）、decision（决策）、output（输出）\n"
            "- edges 必须明确表示推理方向，连接所有相关节点\n"
            "\n"
            "=== 三、node_insights 详细要求 ===\n"
            "为 behavior_tree 中出现的每一个节点（包括所有子节点）提供详细的 node_insights，每个节点包含：\n"
            "\n"
            "1. title：节点标题（简洁明确）\n"
            "\n"
            "2. summary：\n"
            "   - 具体数值（如：50箱、2.5m³、15-25℃、A区-3号货架等）\n"
            "   - 具体对象（如：医疗物资X、常温区、批次号等）\n"
            "   - 具体约束条件（如：有效期至2025年12月、需避光保存等）\n"
            "   - 不能使用\"合适的\"、\"一定的\"、\"若干\"等模糊词汇\n"
            "\n"
            "3. key_points：3-5条关键要点，每条必须：\n"
            "   - 包含具体数值或计算过程\n"
            "   - 对于分析类节点（material_attribute_parsing、warehouse_type_matching、position_recommendation、inventory_recording），必须包含：\n"
            "     * 解析假设（如：\"基于物资标签识别为医疗物资，类型为急救药品\"、\"根据保存条件要求匹配常温区\"）\n"
            "     * 计算或匹配逻辑（如：\"计算剩余容量 = 货架总容量 - 已占用容量\"、\"查询同类物资位置，优先推荐相邻仓位\"）\n"
            "     * 具体结果（如：\"推荐A区-3号货架-2层，剩余容量3.0m³，满足2.5m³需求\"）\n"
            "     * 验证条件（如：\"验证仓位满足温度要求（15-25℃）且距离同类物资较近\"）\n"
            "   - 每条 key_point 应该是一个完整的、可独立理解的句子，避免过于简短的短语\n"
            "\n"
            "4. knowledge_trace：知识追踪路径，必须：\n"
            "   - 使用箭头（→）连接各个推理步骤\n"
            "   - 包含具体的输入、处理过程、输出结果\n"
            "   - 体现完整的推理链条，格式示例：\"物资标签与单据信息 → 类型/数量/体积/保存条件要素提取 → 形成标准化的物资属性描述。\"\n"
            "   - 对于核心决策节点，knowledge_trace 应该体现：输入要素 → 中间推理步骤 → 最终输出结果\n"
            "\n"
            "=== 四、核心节点的特殊要求 ===\n"
            "对以下四个节点（material_attribute_parsing、warehouse_type_matching、position_recommendation、inventory_recording），必须提供可用于教学展示的详细分析/推理细节：\n"
            "\n"
            "- material_attribute_parsing：\n"
            "  * key_points 中必须包含：物资类型识别依据（如\"基于标签识别为医疗物资\"）、数量与体积计算（如\"50箱，单箱体积0.05m³，总体积2.5m³\"）、保存条件要求（如\"需在15-25℃常温保存，避光\"）、有效期信息\n"
            "\n"
            "- warehouse_type_matching：\n"
            "  * key_points 中必须包含：仓储区域选择依据（如\"根据保存条件15-25℃匹配常温区\"）、区域容量与当前占用情况、特殊要求匹配（如\"无需冷藏，无需危险品隔离\"）\n"
            "\n"
            "- position_recommendation：\n"
            "  * key_points 中必须包含：剩余容量计算（如\"A区-3号货架-2层剩余容量3.0m³，满足2.5m³需求\"）、出入库频次分析（如\"该区域月出入库频次15次，属于中等活跃度\"）、同类物资位置（如\"同类医疗物资位于A区-2号货架，推荐相邻位置\"）、最终推荐仓位及理由\n"
            "\n"
            "- inventory_recording：\n"
            "  * summary 和 key_points 必须整合上述三个节点的结果，形成完整的入库登记方案\n"
            "  * key_points 中必须包含：标签生成规则（如\"生成标签：MED-X-20241215-001\"）、批次号记录（如\"批次号：BATCH-20241215-50\"）、有效期记录（如\"有效期至2025年12月\"）、登记时间与操作人员信息\n"
            "  * knowledge_trace 必须体现：\"物资属性与仓储匹配结果 → 仓位推荐结果 → 生成入库标签与登记信息 → 完成入库登记\"\n"
            "\n"
            "=== 五、输出质量检查清单 ===\n"
            "生成内容后，请确保：\n"
            "□ 行为树至少包含两层结构（根节点有子节点，且至少一个子节点有子节点）\n"
            "□ 至少有一个 node_insights 内的节点包含 knowledge_graph\n"
            "□ 所有 label 包含具体数值和位置信息\n"
            "□ 所有 summary 包含具体数值而非空泛描述\n"
            "□ 所有 key_points 包含分析过程或具体参数\n"
            "□ 所有 knowledge_trace 使用箭头连接且包含具体步骤\n"
            "□ knowledge_graph 的 nodes label 包含参数信息\n"
            "□ 核心决策节点包含完整的推理细节"
        ),
        example_output={
            "default_focus": "position_recommendation",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "📦 资源入库：医疗物资X入库处理",
                "status": "completed",
                "summary": "解析任务：新到达一批医疗物资X，需要完成入库保管，包括物资属性识别、仓储区域匹配、仓位推荐与入库登记。",
                "children": [
                    {
                        "id": "material_attribute_parsing",
                        "label": "📋 物资属性解析",
                        "status": "completed",
                        "summary": "解析医疗物资X的属性：识别物资类型、统计数量与体积、分析保存条件（温度、湿度、特殊要求）与有效期。",
                        "children": [
                            {
                                "id": "type_identification",
                                "label": "🏷️ 类型识别",
                                "status": "completed",
                                "summary": "基于物资标签与单据信息，识别物资类别（如急救药品、医疗器械等），判断是否属于危险品或需特殊存储。",
                                "children": []
                            },
                            {
                                "id": "quantity_volume_analysis",
                                "label": "📊 数量体积分析",
                                "status": "completed",
                                "summary": "统计物资数量（箱数或件数）、测量单位体积、计算总体积与重量，为仓位容量匹配提供依据。",
                                "children": []
                            },
                            {
                                "id": "storage_condition_analysis",
                                "label": "🌡️ 保存条件分析",
                                "status": "completed",
                                "summary": "分析保存条件要求：温度范围（常温/冷藏/冷冻）、湿度要求、特殊要求（避光、通风等）与有效期信息。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "warehouse_type_matching",
                        "label": "🏭 仓储类型匹配",
                        "status": "completed",
                        "summary": "根据保存条件匹配仓储区域类型（常温区/冷藏区/危险品区/特殊存储区），验证区域可用容量与环境参数。",
                        "children": []
                    },
                    {
                        "id": "position_recommendation",
                        "label": "✅ 仓位推荐",
                        "status": "active",
                        "summary": "综合剩余容量、出入库频次、同类物资位置等因素，推荐最优仓位，便于统一管理与快速取用。",
                        "children": [
                            {
                                "id": "capacity_analysis",
                                "label": "📦 剩余容量分析",
                                "status": "completed",
                                "summary": "查询候选仓位的总容量、已占用容量，计算剩余容量，验证是否满足入库需求并预留余量。",
                                "children": []
                            },
                            {
                                "id": "frequency_analysis",
                                "label": "📈 出入库频次分析",
                                "status": "completed",
                                "summary": "统计候选区域的历史出入库频次，评估活跃度（低/中/高），选择适合物资使用特性的仓位。",
                                "children": []
                            },
                            {
                                "id": "similar_material_location",
                                "label": "🔍 同类物资位置匹配",
                                "status": "completed",
                                "summary": "查询同类物资的存储位置，推荐相邻仓位以实现统一管理、快速定位与减少查找时间。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "inventory_recording",
                        "label": "📝 入库登记",
                        "status": "completed",
                        "summary": "生成入库标签、记录批次号、有效期、登记时间与操作信息，同步至库存管理系统。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务分析与解析",
                    "summary": "对\"新到达一批医疗物资X，需要入库保管\"的任务进行结构化解析，明确物资名称、数量、入库时间要求等基础信息。",
                    "key_points": [
                        "抽取任务要素：医疗物资X、新到达、需要入库保管",
                        "识别入库紧迫性：常规入库，无紧急时间要求",
                        "为后续物资属性解析与仓储匹配提供统一的数据输入框架"
                    ],
                    "knowledge_trace": "任务文本解析 → 物资名称/数量/时间要素抽取 → 形成可供后续节点复用的标准任务描述。"
                },
                "material_attribute_parsing": {
                    "title": "物资属性解析",
                    "summary": "解析医疗物资X的属性：类型为急救药品，数量50箱，总体积2.5m³，需在常温（15-25℃）条件下保存，有效期至2025年12月，需避光。",
                    "key_points": [
                        "基于物资标签与单据信息识别为医疗物资中的急救药品类别，不属于危险品",
                        "统计物资数量为50箱，单箱体积0.05m³，总体积2.5m³，单箱重量约10kg，总重量约500kg",
                        "分析保存条件：需在15-25℃常温环境下保存，需避光，湿度要求60-70%，有效期至2025年12月",
                        "提取批次信息：生产日期2024年6月，批次号BATCH-20241215-50"
                    ],
                    "knowledge_trace": "物资标签与单据信息 → 类型/数量/体积/保存条件要素提取 → 形成标准化的物资属性描述。"
                },
                "type_identification": {
                    "title": "类型识别",
                    "summary": "基于物资标签与单据信息，识别为医疗物资中的急救药品类别，不属于危险品。",
                    "key_points": [
                        "读取物资标签信息，识别物资类别编码为MED-001（医疗物资）",
                        "进一步识别子类别为急救药品，不属于需要特殊隔离的危险品",
                        "匹配物资分类标准，确定应归类为\"医疗物资-急救药品\"类别"
                    ],
                    "knowledge_trace": "标签信息读取 → 类别编码识别 → 子类别匹配 → 确定物资类型。"
                },
                "quantity_volume_analysis": {
                    "title": "数量体积分析",
                    "summary": "统计物资数量为50箱，单箱体积0.05m³，总体积2.5m³，单箱重量约10kg，总重量约500kg。",
                    "key_points": [
                        "清点物资数量：共50箱，每箱规格统一",
                        "测量单箱体积：长×宽×高 = 0.4m × 0.3m × 0.42m ≈ 0.05m³",
                        "计算总体积：50箱 × 0.05m³/箱 = 2.5m³",
                        "估算重量：单箱约10kg，总重量约500kg"
                    ],
                    "knowledge_trace": "数量清点 → 单箱体积测量 → 总体积计算 → 重量估算。"
                },
                "storage_condition_analysis": {
                    "title": "保存条件分析",
                    "summary": "分析保存条件：需在15-25℃常温环境下保存，需避光，湿度要求60-70%，有效期至2025年12月。",
                    "key_points": [
                        "提取温度要求：15-25℃常温保存，无需冷藏或冷冻",
                        "识别特殊要求：需避光保存，避免阳光直射",
                        "湿度要求：60-70%相对湿度，需在干燥通风环境",
                        "有效期信息：生产日期2024年6月，有效期18个月，有效期至2025年12月"
                    ],
                    "knowledge_trace": "保存条件标签读取 → 温度/湿度/光照要求提取 → 有效期计算 → 形成保存条件规范。"
                },
                "warehouse_type_matching": {
                    "title": "仓储类型匹配",
                    "summary": "根据保存条件15-25℃匹配常温仓储区，该区域当前可用容量充足，温度控制稳定在20±2℃。",
                    "key_points": [
                        "根据保存条件15-25℃匹配常温仓储区（无需冷藏区或危险品区）",
                        "查询常温区当前状态：总容量500m³，已占用300m³，可用容量200m³，容量充足",
                        "验证温度控制：常温区温度稳定在20±2℃，满足15-25℃要求",
                        "确认无需特殊隔离：不属于危险品，无需单独隔离存储"
                    ],
                    "knowledge_trace": "保存条件要求 → 仓储区域类型匹配 → 容量与温度验证 → 确定仓储区域。"
                },
                "position_recommendation": {
                    "title": "仓位推荐",
                    "summary": "推荐A区-3号货架-2层作为入库仓位，该位置剩余容量3.0m³（满足2.5m³需求），月出入库频次15次（中等活跃度），同类医疗物资位于相邻A区-2号货架，便于统一管理。",
                    "key_points": [
                        "计算A区-3号货架-2层剩余容量：总容量5.0m³ - 已占用2.0m³ = 剩余3.0m³，满足2.5m³需求且有0.5m³余量",
                        "分析出入库频次：该区域月出入库频次15次，属于中等活跃度，适合存放常用医疗物资",
                        "查询同类物资位置：同类医疗物资（急救药品）位于A区-2号货架，推荐相邻A区-3号货架便于统一管理",
                        "验证仓位条件：A区-3号货架-2层满足温度（20±2℃）、避光、湿度（65%）要求，距离同类物资较近"
                    ],
                    "knowledge_trace": "物资属性与仓储区域 → 剩余容量计算 → 频次与同类物资位置分析 → 形成仓位推荐方案。",
                    "knowledge_graph": {
                        "nodes": [
                            # 主推理链节点
                            {"id": "material_parsing", "label": "物资属性解析", "type": "input"},
                            {"id": "warehouse_matching", "label": "仓储类型匹配", "type": "process"},
                            {"id": "capacity_analysis", "label": "容量分析", "type": "process"},
                            {"id": "frequency_analysis", "label": "频次分析", "type": "decision"},
                            {"id": "location_matching", "label": "位置匹配", "type": "process"},
                            {"id": "position_recommendation", "label": "仓位推荐", "type": "output"},
                            
                            # 辅助细节节点（与任务相关但相关性较低）
                            {"id": "temperature_monitor", "label": "温度监控数据", "type": "input"},
                            {"id": "humidity_monitor", "label": "湿度监控数据", "type": "input"},
                            {"id": "access_route", "label": "通道可达性", "type": "input"},
                            {"id": "shelf_structure", "label": "货架结构信息", "type": "input"}
                        ],
                        "edges": [
                            # 主推理链连接
                            {"source": "material_parsing", "target": "warehouse_matching"},
                            {"source": "warehouse_matching", "target": "capacity_analysis"},
                            {"source": "capacity_analysis", "target": "frequency_analysis"},
                            {"source": "frequency_analysis", "target": "location_matching"},
                            {"source": "location_matching", "target": "position_recommendation"},
                            
                            # 辅助节点的单向连接
                            {"source": "temperature_monitor", "target": "warehouse_matching"},
                            {"source": "humidity_monitor", "target": "warehouse_matching"}
                            
                            # 注意：access_route、shelf_structure 独立存在，不连接到主链
                        ]
                    }
                },
                "capacity_analysis": {
                    "title": "剩余容量分析",
                    "summary": "分析A区-3号货架-2层：总容量5.0m³，已占用2.0m³，剩余容量3.0m³，满足2.5m³入库需求，且有0.5m³余量。",
                    "key_points": [
                        "查询货架容量：A区-3号货架-2层总容量5.0m³",
                        "统计已占用容量：当前已存放物资占用2.0m³",
                        "计算剩余容量：5.0m³ - 2.0m³ = 3.0m³",
                        "验证容量充足：3.0m³ > 2.5m³，满足入库需求，且有0.5m³余量便于后续调整"
                    ],
                    "knowledge_trace": "货架容量查询 → 已占用容量统计 → 剩余容量计算 → 容量充足性验证。"
                },
                "frequency_analysis": {
                    "title": "出入库频次分析",
                    "summary": "统计该区域月出入库频次为15次，属于中等活跃度，适合存放常用医疗物资，便于快速取用。",
                    "key_points": [
                        "统计历史数据：A区-3号货架区域近3个月平均月出入库频次15次",
                        "活跃度评估：15次/月属于中等活跃度（低活跃<10次，中等10-20次，高活跃>20次）",
                        "适用性判断：中等活跃度适合存放常用医疗物资，既保证快速取用又避免过度频繁操作",
                        "同类物资参考：同类医疗物资所在A区-2号货架月频次18次，活跃度相近"
                    ],
                    "knowledge_trace": "历史出入库数据统计 → 活跃度等级评估 → 适用性判断 → 形成频次分析结论。"
                },
                "similar_material_location": {
                    "title": "同类物资位置匹配",
                    "summary": "查询同类医疗物资（急救药品）位于A区-2号货架，推荐相邻的A区-3号货架，便于统一管理与快速定位。",
                    "key_points": [
                        "查询同类物资：在库存系统中查询同类医疗物资（急救药品）的存储位置",
                        "定位同类物资：发现同类物资主要位于A区-2号货架，共存放约30箱同类急救药品",
                        "推荐相邻位置：推荐相邻的A区-3号货架，距离A区-2号货架仅5米，便于统一管理",
                        "管理优势：同类物资集中存放便于快速定位、统一管理、减少查找时间"
                    ],
                    "knowledge_trace": "同类物资查询 → 位置定位 → 相邻仓位推荐 → 形成位置匹配方案。"
                },
                "inventory_recording": {
                    "title": "入库登记",
                    "summary": "生成入库标签MED-X-20241215-001，记录批次号BATCH-20241215-50，有效期至2025年12月，登记时间2024年12月15日14:30，操作人员系统自动登记。",
                    "key_points": [
                        "生成入库标签：按照规则生成标签MED-X-20241215-001（MED表示医疗物资，X为物资名称，20241215为日期，001为序号）",
                        "记录批次信息：批次号BATCH-20241215-50，生产日期2024年6月，有效期至2025年12月",
                        "登记时间信息：入库登记时间2024年12月15日14:30，操作人员系统自动登记",
                        "同步库存系统：将入库信息同步至库存管理系统，更新库存数量、仓位占用、有效期预警等数据"
                    ],
                    "knowledge_trace": "物资属性与仓储匹配结果 → 仓位推荐结果 → 生成入库标签与登记信息 → 完成入库登记并同步系统。"
                }
            }
        },
    ),
    # 22. 资源盘点
    Scenario(
        id="resource_inventory_check",  # 22. 资源盘点
        model_name="后勤资源管控",
        name="资源盘点",
        example_input="对食品与医疗物资进行周期性盘点，确保数据一致。",
        reasoning_chain="库存数据解析（账面数量、实际传感数量）→ 盘点策略制定（优先检查消耗快的品类）→ 差异检测（短缺、过期、误放）→ 异常定位（原因分析，如运输损耗、登记错误、未记录的应急领取）",
        prompt=(
            "【后勤资源管控-资源盘点专项要求】\n"
            "\n"
            "=== 一、行为树结构要求 ===\n"
            "1. 行为树必须至少包含以下核心节点，且严格按照推理链条自上而下展开：\n"
            "   - task_analysis（任务分析与解析，根节点）：\n"
            "       * 明确盘点范围、盘点类型（周期性/全面/抽查）、时间要求等基础信息；\n"
            "       * 至少拆分出\"盘点范围识别\"和\"盘点类型确定\"两个子层级节点；\n"
            "   - inventory_data_parsing（库存数据解析）：\n"
            "       * 至少包含 book_quantity_analysis（账面数量分析）、sensor_quantity_analysis（实际传感数量分析）、data_comparison（数据对比）三个子节点；\n"
            "   - inventory_strategy_formulation（盘点策略制定）：\n"
            "       * 根据物资类型、消耗速度、重要性等因素制定盘点优先级和策略；\n"
            "   - difference_detection（差异检测，核心决策节点）：\n"
            "       * 下方必须细化出 shortage_detection（短缺检测）、expiry_detection（过期检测）、misplacement_detection（误放检测）三个子节点；\n"
            "       * 该节点必须包含 knowledge_graph 字段。\n"
            "   - anomaly_localization（异常定位）：\n"
            "       * 分析差异原因，如运输损耗、登记错误、未记录的应急领取等。\n"
            "\n"
            "2. behavior_tree 中每个节点的格式要求：\n"
            "   - label 字段：必须包含具体数值结果，格式示例：\"📊 库存数据解析：账面120箱，实际115箱\"、\"✅ 盘点策略制定：优先食品类\"、\"✅ 差异检测：短缺5箱，过期3箱\"；\n"
            "   - summary 字段：必须包含具体数值、数量、差异等量化信息，不能使用空泛描述。例如：\n"
            "     * 正确示例：\"对比账面数量120箱与实际传感数量115箱，发现短缺5箱，差异率4.2%，同时检测到3箱物资已过期。\"\n"
            "     * 错误示例：\"发现库存存在差异\"（过于空泛，缺少具体数值）\n"
            "\n"
            "=== 二、knowledge_graph 要求 ===\n"
            "difference_detection 节点的 knowledge_graph 必须体现完整因果链路：\n"
            "库存数据解析(inventory_parsing) → 盘点策略制定(strategy_formulation) → 短缺检测(shortage_detection) → 过期检测(expiry_detection) → 误放检测(misplacement_detection) → 差异汇总(difference_summary)\n"
            "\n"
            "具体要求：\n"
            "- nodes[].label 必须包含具体参数信息，格式：\"节点名称(具体参数1, 具体参数2, ...)\"\n"
            "  示例：\"库存数据解析(账面120箱, 实际115箱)\"、\"差异检测(短缺5箱, 过期3箱)\"、\"异常定位(运输损耗, 登记错误)\"\n"
            "- nodes[].type 必须明确标注：input（输入）、process（处理）、decision（决策）、output（输出）\n"
            "- edges 必须明确表示推理方向，连接所有相关节点\n"
            "\n"
            "=== 三、node_insights 详细要求 ===\n"
            "为 behavior_tree 中出现的每一个节点（包括所有子节点）提供详细的 node_insights，每个节点包含：\n"
            "\n"
            "1. title：节点标题（简洁明确）\n"
            "\n"
            "2. summary：\n"
            "   - 具体数值（如：120箱、115箱、5箱、4.2%、3箱等）\n"
            "   - 具体对象（如：食品类、医疗物资、A区-3号货架等）\n"
            "   - 具体差异类型（如：短缺、过期、误放等）\n"
            "   - 不能使用\"合适的\"、\"一定的\"、\"若干\"等模糊词汇\n"
            "\n"
            "3. key_points：3-5条关键要点，每条必须：\n"
            "   - 包含具体数值或计算过程\n"
            "   - 对于分析类节点（inventory_data_parsing、inventory_strategy_formulation、difference_detection、anomaly_localization），必须包含：\n"
            "     * 解析假设（如：\"基于库存系统查询账面数量\"、\"通过RFID传感器读取实际数量\"）\n"
            "     * 计算或对比逻辑（如：\"计算差异 = 账面数量 - 实际数量\"、\"差异率 = 差异数量 ÷ 账面数量 × 100%\"）\n"
            "     * 具体结果（如：\"发现短缺5箱，差异率4.2%\"、\"检测到3箱物资已过期\"）\n"
            "     * 验证条件（如：\"验证差异是否在合理范围内（±5%）\"、\"检查过期物资是否已隔离\"）\n"
            "   - 每条 key_point 应该是一个完整的、可独立理解的句子，避免过于简短的短语\n"
            "\n"
            "4. knowledge_trace：知识追踪路径，必须：\n"
            "   - 使用箭头（→）连接各个推理步骤\n"
            "   - 包含具体的输入、处理过程、输出结果\n"
            "   - 体现完整的推理链条，格式示例：\"库存系统数据查询 → 账面数量提取 → 传感器数据读取 → 实际数量统计 → 数据对比分析。\"\n"
            "   - 对于核心决策节点，knowledge_trace 应该体现：输入要素 → 中间推理步骤 → 最终输出结果\n"
            "\n"
            "=== 四、核心节点的特殊要求 ===\n"
            "对以下四个节点（inventory_data_parsing、inventory_strategy_formulation、difference_detection、anomaly_localization），必须提供可用于教学展示的详细分析/推理细节：\n"
            "\n"
            "- inventory_data_parsing：\n"
            "  * key_points 中必须包含：账面数量来源（如\"从库存系统查询账面数量120箱\"）、实际数量获取方式（如\"通过RFID传感器读取实际数量115箱\"）、数据对比方法（如\"计算差异 = 120 - 115 = 5箱\"）、差异率计算（如\"差异率 = 5 ÷ 120 × 100% = 4.2%\"）\n"
            "\n"
            "- inventory_strategy_formulation：\n"
            "  * key_points 中必须包含：盘点优先级排序依据（如\"食品类消耗快，优先盘点\"）、盘点范围确定（如\"重点盘点食品与医疗物资，其他物资抽查\"）、盘点方法选择（如\"全面盘点食品类，抽样盘点其他类\"）\n"
            "\n"
            "- difference_detection：\n"
            "  * key_points 中必须包含：短缺数量计算（如\"账面120箱 - 实际115箱 = 短缺5箱\"）、过期物资检测（如\"检测到3箱物资有效期已过\"）、误放物资识别（如\"发现2箱物资位置与登记不符\"）、差异汇总（如\"总计差异：短缺5箱，过期3箱，误放2箱\"）\n"
            "\n"
            "- anomaly_localization：\n"
            "  * summary 和 key_points 必须整合上述三个节点的结果，形成完整的异常定位分析\n"
            "  * key_points 中必须包含：差异原因分析（如\"短缺5箱可能因运输损耗2箱、登记错误2箱、未记录应急领取1箱\"）、过期原因分析（如\"3箱过期因未及时使用且未设置预警\"）、误放原因分析（如\"2箱误放因入库时登记错误\"）、处理建议（如\"建议加强运输管理、完善登记流程、设置有效期预警\"）\n"
            "  * knowledge_trace 必须体现：\"差异检测结果 → 原因分析（运输损耗/登记错误/应急领取） → 形成异常定位报告与处理建议\"\n"
            "\n"
            "=== 五、输出质量检查清单 ===\n"
            "生成内容后，请确保：\n"
            "□ 行为树至少包含两层结构（根节点有子节点，且至少一个子节点有子节点）\n"
            "□ 至少有一个 node_insights 内的节点包含 knowledge_graph\n"
            "□ 所有 label 包含具体数值和差异信息\n"
            "□ 所有 summary 包含具体数值而非空泛描述\n"
            "□ 所有 key_points 包含分析过程或具体参数\n"
            "□ 所有 knowledge_trace 使用箭头连接且包含具体步骤\n"
            "□ knowledge_graph 的 nodes label 包含参数信息\n"
            "□ 核心决策节点包含完整的推理细节"
        ),
        example_output={
            "default_focus": "difference_detection",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "📊 资源盘点：食品与医疗物资周期性盘点",
                "status": "completed",
                "summary": "解析任务：对食品与医疗物资进行周期性盘点，确保账面数据与实际库存数据一致，识别差异并定位异常原因。",
                "children": [
                    {
                        "id": "inventory_data_parsing",
                        "label": "📋 库存数据解析",
                        "status": "completed",
                        "summary": "对比账面数量与实际传感数量，识别短缺、过期与误放等差异情况，计算差异率并评估合理性。",
                        "children": [
                            {
                                "id": "book_quantity_analysis",
                                "label": "📖 账面数量分析",
                                "status": "completed",
                                "summary": "从库存管理系统查询食品与医疗物资的账面数量，按类别汇总统计。",
                                "children": []
                            },
                            {
                                "id": "sensor_quantity_analysis",
                                "label": "📡 实际传感数量分析",
                                "status": "completed",
                                "summary": "通过RFID传感器或人工清点获取实际库存数量，按类别汇总统计并验证数据准确性。",
                                "children": []
                            },
                            {
                                "id": "data_comparison",
                                "label": "🔍 数据对比",
                                "status": "completed",
                                "summary": "计算账面与实际数量的差异，计算差异率，评估是否在合理范围内。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "inventory_strategy_formulation",
                        "label": "📝 盘点策略制定",
                        "status": "completed",
                        "summary": "根据物资特性、消耗速度与重要性制定盘点策略，确定优先级、盘点方法与重点关注项。",
                        "children": []
                    },
                    {
                        "id": "difference_detection",
                        "label": "✅ 差异检测",
                        "status": "active",
                        "summary": "检测三类差异：短缺（账面与实际数量差）、过期（有效期已过）、误放（位置与登记不符），汇总差异情况。",
                        "children": [
                            {
                                "id": "shortage_detection",
                                "label": "📉 短缺检测",
                                "status": "completed",
                                "summary": "识别账面数量大于实际数量的情况，分析短缺分布、计算短缺率并评估影响。",
                                "children": []
                            },
                            {
                                "id": "expiry_detection",
                                "label": "⏰ 过期检测",
                                "status": "completed",
                                "summary": "检查物资有效期信息，识别已过期物资并分析过期原因，生成隔离与处理建议。",
                                "children": []
                            },
                            {
                                "id": "misplacement_detection",
                                "label": "📍 误放检测",
                                "status": "completed",
                                "summary": "对比登记位置与实际扫描位置，识别位置不符的物资并分析误放原因。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "anomaly_localization",
                        "label": "🔎 异常定位",
                        "status": "completed",
                        "summary": "分析差异原因：运输损耗、登记错误、未记录应急领取、未设置预警等，生成异常定位报告与处理建议。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务分析与解析",
                    "summary": "对盘点任务进行结构化解析，明确盘点范围（食品与医疗物资）、盘点类型（周期性）、目标（确保数据一致）等基础信息。",
                    "key_points": [
                        "抽取任务要素：盘点对象、盘点周期、数据一致性要求",
                        "识别盘点类型：周期性盘点、全面盘点或重点抽查",
                        "为后续库存数据解析与差异检测提供统一的数据输入框架"
                    ],
                    "knowledge_trace": "任务文本解析 → 盘点范围/类型/目标要素抽取 → 形成可供后续节点复用的标准任务描述。"
                },
                "inventory_data_parsing": {
                    "title": "库存数据解析",
                    "summary": "对比库存系统的账面数量与传感器采集的实际数量，计算差异值与差异率，为差异检测提供数据基础。",
                    "key_points": [
                        "查询账面数据：从库存管理系统获取各类物资的账面登记数量",
                        "采集实际数据：通过RFID传感器、条码扫描或人工清点获取实际库存数量",
                        "计算差异指标：差异数量（账面-实际）、差异率（差异÷账面×100%）",
                        "评估差异合理性：判断差异是否在可接受范围内（如±2%），超出则需深入分析"
                    ],
                    "knowledge_trace": "库存系统数据查询 → 账面数量提取 → 传感器数据采集 → 实际数量统计 → 数据对比分析。"
                },
                "book_quantity_analysis": {
                    "title": "账面数量分析",
                    "summary": "从库存管理系统查询各类物资的账面数量，按类别汇总统计并记录数据来源与更新时间。",
                    "key_points": [
                        "查询账面数量：从库存系统按类别（食品类、医疗物资类等）查询账面登记数量",
                        "数量汇总统计：按类别汇总，计算各类别小计与总计",
                        "数据来源记录：记录数据来源系统、查询时间与最后更新时间"
                    ],
                    "knowledge_trace": "库存系统查询 → 分类别数量提取 → 数量汇总 → 数据来源记录。"
                },
                "sensor_quantity_analysis": {
                    "title": "实际传感数量分析",
                    "summary": "通过RFID传感器、条码扫描或人工清点获取实际库存数量，按类别汇总统计并验证数据准确性。",
                    "key_points": [
                        "数据采集方式：RFID传感器扫描、条码扫描或人工清点",
                        "分类别统计：按物资类别读取实际数量并汇总",
                        "数据准确性验证：与人工抽查结果对比，确认传感器数据可靠性"
                    ],
                    "knowledge_trace": "传感器数据采集 → 分类别数量读取 → 数量汇总 → 数据准确性验证。"
                },
                "data_comparison": {
                    "title": "数据对比",
                    "summary": "计算账面与实际数量的差异值与差异率，分析差异分布，评估差异是否在合理范围内。",
                    "key_points": [
                        "差异计算：账面数量 - 实际数量 = 短缺（正值）或盈余（负值）",
                        "差异率计算：差异率 = 差异数量 ÷ 账面数量 × 100%",
                        "分类别差异分析：各类别的短缺或盈余情况",
                        "合理性评估：对比差异容差标准（如±2%），判断是否需要深入分析"
                    ],
                    "knowledge_trace": "账面与实际数量对比 → 差异计算 → 差异率计算 → 合理性评估。"
                },
                "inventory_strategy_formulation": {
                    "title": "盘点策略制定",
                    "summary": "根据物资特性（消耗速度、易过期性、重要性等）制定盘点策略，确定优先级、盘点方法与重点关注项。",
                    "key_points": [
                        "物资特性分析：消耗速度（快/中/慢）、易过期性、重要程度",
                        "盘点优先级排序：消耗快、易过期的品类优先全面盘点",
                        "盘点方法选择：全面盘点、重点抽查或周期性轮盘",
                        "重点关注项设定：数量准确性、有效期、位置准确性等"
                    ],
                    "knowledge_trace": "物资特性分析 → 消耗速度评估 → 盘点优先级排序 → 盘点方法与重点制定。"
                },
                "difference_detection": {
                    "title": "差异检测",
                    "summary": "检测三类差异：短缺（账面大于实际）、过期（有效期已过）、误放（位置与登记不符），汇总差异情况。",
                    "key_points": [
                        "短缺检测：识别账面数量大于实际数量的物资，分析短缺分布与短缺率",
                        "过期检测：查询有效期信息，识别已过期或临近过期的物资",
                        "误放检测：对比登记位置与实际扫描位置，识别位置不符的物资",
                        "差异汇总：汇总各类差异的数量、比例与影响，为异常定位提供依据"
                    ],
                    "knowledge_trace": "库存数据对比 → 短缺检测 → 过期检测 → 误放检测 → 差异汇总。",
                    "knowledge_graph": {
                        "nodes": [
                            # 主推理链节点
                            {"id": "inventory_parsing", "label": "库存数据解析", "type": "input"},
                            {"id": "strategy_formulation", "label": "盘点策略制定", "type": "process"},
                            {"id": "shortage_detection", "label": "短缺检测", "type": "process"},
                            {"id": "expiry_detection", "label": "过期检测", "type": "process"},
                            {"id": "misplacement_detection", "label": "误放检测", "type": "process"},
                            {"id": "difference_summary", "label": "差异汇总", "type": "output"},
                            
                            # 辅助细节节点（与任务相关但相关性较低）
                            {"id": "historical_inventory", "label": "历史盘点记录", "type": "input"},
                            {"id": "consumption_rate", "label": "消耗速率数据", "type": "input"},
                            {"id": "weather_impact", "label": "环境条件影响", "type": "input"}
                        ],
                        "edges": [
                            # 主推理链连接
                            {"source": "inventory_parsing", "target": "strategy_formulation"},
                            {"source": "strategy_formulation", "target": "shortage_detection"},
                            {"source": "strategy_formulation", "target": "expiry_detection"},
                            {"source": "strategy_formulation", "target": "misplacement_detection"},
                            {"source": "shortage_detection", "target": "difference_summary"},
                            {"source": "expiry_detection", "target": "difference_summary"},
                            {"source": "misplacement_detection", "target": "difference_summary"},
                            
                            # 辅助节点的单向连接
                            {"source": "historical_inventory", "target": "strategy_formulation"}
                            
                            # 注意：consumption_rate、weather_impact 独立存在
                        ]
                    }
                },
                "shortage_detection": {
                    "title": "短缺检测",
                    "summary": "识别账面数量大于实际数量的物资，分析短缺分布、计算短缺率并评估对日常供应的影响。",
                    "key_points": [
                        "短缺计算：账面数量 - 实际数量 = 短缺数量（正值）",
                        "短缺率计算：短缺率 = 短缺数量 ÷ 账面数量 × 100%",
                        "短缺分布分析：按类别、货架区域分析短缺集中度",
                        "影响评估：评估短缺对日常供应的影响，提出补充建议"
                    ],
                    "knowledge_trace": "分类别数量对比 → 短缺数量计算 → 短缺率计算 → 影响评估。"
                },
                "expiry_detection": {
                    "title": "过期检测",
                    "summary": "检查物资有效期信息，识别已过期或临近过期的物资，分析过期原因并生成隔离与处理建议。",
                    "key_points": [
                        "有效期查询：从物资标签或系统记录中提取有效期信息",
                        "过期识别：对比当前日期与有效期，识别已过期物资",
                        "过期原因分析：未及时使用、未设置预警、消耗速度低于预期等",
                        "处理建议：立即隔离、设置预警机制、优先使用临近过期物资"
                    ],
                    "knowledge_trace": "有效期信息查询 → 过期物资识别 → 过期原因分析 → 处理建议生成。"
                },
                "misplacement_detection": {
                    "title": "误放检测",
                    "summary": "对比登记位置与实际扫描位置，识别位置不符的物资，分析误放原因并生成位置更新建议。",
                    "key_points": [
                        "位置对比：从系统查询登记位置，通过传感器获取实际位置",
                        "误放识别：识别登记位置与实际位置不一致的物资",
                        "原因分析：入库登记错误、搬运后未更新、人工操作失误等",
                        "处理建议：更新系统位置信息、加强登记准确性、建立位置变更及时更新机制"
                    ],
                    "knowledge_trace": "登记位置查询 → 实际位置扫描 → 位置对比 → 误放原因分析。"
                },
                "anomaly_localization": {
                    "title": "异常定位",
                    "summary": "分析差异原因（运输损耗、登记错误、未记录应急领取、未设置预警等），生成异常定位报告与改进建议。",
                    "key_points": [
                        "短缺原因分析：运输损耗（运输中损坏或丢失）、登记错误（入库多登或出库少登）、未记录应急领取（紧急领用未及时登记）",
                        "过期原因分析：未及时使用（消耗速度低于预期）、未设置预警（系统未提前提醒）",
                        "误放原因分析：入库登记错误（登记与实际位置不一致）、搬运后位置变更未更新",
                        "改进建议：加强运输管理、完善登记流程、设置有效期预警、建立位置变更及时更新机制、加强应急领取登记"
                    ],
                    "knowledge_trace": "差异检测结果 → 原因分析（运输/登记/预警/应急） → 形成异常定位报告与改进建议。"
                }
            }
        },
    ),
    # 23. 资源出库
    Scenario(
        id="resource_outbound_processing",  # 23. 资源出库
        model_name="后勤资源管控",
        name="资源出库",
        example_input="为即将执行任务的医疗小组准备急救包和耗材。",
        reasoning_chain="任务需求解析（急救包、绷带、注射器等）→ 库存匹配（查询可用数量与批次）→ 出库策略（先进先出/保质期优先）→ 装载与交接（生成移交记录并推荐运输车辆）",
        prompt=(
            "【后勤资源管控-资源出库专项要求】\n"
            "\n"
            "=== 一、行为树结构要求 ===\n"
            "1. 行为树必须至少包含两层结构（根节点必须有子节点，且至少有一个子节点还有子节点）：\n"
            "   - task_analysis（任务分析与解析，根节点）：\n"
            "       * 明确出库任务需求、物资类型、数量、时间要求等基础信息；\n"
            "       * 至少拆分出\"任务需求提取\"和\"出库目标识别\"两个子层级节点；\n"
            "   - task_requirement_parsing（任务需求解析）：\n"
            "       * 至少包含 material_type_identification（物资类型识别）、quantity_requirement_analysis（数量需求分析）、priority_analysis（优先级分析）三个子节点；\n"
            "   - inventory_matching（库存匹配）：\n"
            "       * 查询可用数量与批次，匹配库存资源；\n"
            "   - outbound_strategy（出库策略，核心决策节点）：\n"
            "       * 下方必须细化出 fifo_strategy（先进先出策略）、expiry_priority_strategy（保质期优先策略）、batch_selection（批次选择）三个子节点；\n"
            "       * 该节点必须包含 knowledge_graph 字段。\n"
            "   - loading_and_handover（装载与交接）：\n"
            "       * 生成移交记录并推荐运输车辆。\n"
            "\n"
            "2. behavior_tree 中每个节点的格式要求：\n"
            "   - label 字段：必须包含具体数值结果，格式示例：\"📦 任务需求解析：急救包10个，绷带20卷\"、\"✅ 库存匹配：可用15个，批次3个\"、\"✅ 出库策略：保质期优先\"；\n"
            "   - summary 字段：必须包含具体数值、数量、批次等量化信息，不能使用空泛描述。\n"
            "\n"
            "=== 二、knowledge_graph 要求 ===\n"
            "outbound_strategy 节点的 knowledge_graph 必须体现完整因果链路：\n"
            "任务需求解析(requirement_parsing) → 库存匹配(inventory_matching) → 出库策略选择(strategy_selection) → 批次确定(batch_determination) → 出库方案生成(outbound_plan)\n"
            "\n"
            "具体要求：\n"
            "- nodes[].label 必须包含具体参数信息，格式：\"节点名称(具体参数1, 具体参数2, ...)\"\n"
            "- nodes[].type 必须明确标注：input（输入）、process（处理）、decision（决策）、output（输出）\n"
            "- edges 必须明确表示推理方向，连接所有相关节点\n"
            "\n"
            "=== 三、node_insights 详细要求 ===\n"
            "为 behavior_tree 中出现的每一个节点（包括所有子节点）提供详细的 node_insights，每个节点包含：\n"
            "1. title：节点标题（简洁明确）\n"
            "2. summary：必须包含具体数值、数量、批次等量化信息\n"
            "3. key_points：3-5条关键要点，每条必须包含具体数值或计算过程\n"
            "4. knowledge_trace：使用箭头（→）连接各个推理步骤，体现完整的推理链条\n"
            "\n"
            "=== 四、输出质量检查清单 ===\n"
            "生成内容后，请确保：\n"
            "□ 行为树至少包含两层结构（根节点有子节点，且至少一个子节点有子节点）\n"
            "□ 至少有一个 node_insights 内的节点包含 knowledge_graph\n"
            "□ 所有 label 包含具体数值\n"
            "□ 所有 summary 包含具体数值而非空泛描述\n"
            "□ 所有 key_points 包含分析过程或具体参数"
        ),
        example_output={
            "default_focus": "outbound_strategy",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "📦 任务分析：急救包10个，绷带20卷，注射器40支",
                "status": "completed",
                "summary": "解析出库需求：为医疗小组准备急救包10个、绷带20卷、注射器40支，需在1小时内完成出库与交接。",
                "children": [
                    {
                        "id": "task_requirement_parsing",
                        "label": "📑 任务需求解析：3类物资，70件",
                        "status": "completed",
                        "summary": "识别物资类型3类，共70件，并确认急救包优先级最高。",
                        "children": [
                            {
                                "id": "material_type_identification",
                                "label": "物资类型识别：急救包/绷带/注射器",
                                "status": "completed",
                                "summary": "解析文本得到3类物资：急救包、绷带、注射器。",
                                "children": []
                            },
                            {
                                "id": "quantity_requirement_analysis",
                                "label": "数量需求分析：10/20/40",
                                "status": "completed",
                                "summary": "确定需求数量：急救包10个、绷带20卷、注射器40支。",
                                "children": []
                            },
                            {
                                "id": "priority_analysis",
                                "label": "优先级分析：急救包最高",
                                "status": "completed",
                                "summary": "基于任务紧急性，将急救包设为最高优先级，其次绷带，再次注射器。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "inventory_matching",
                        "label": "✅ 库存匹配：急救包12，绷带30，注射器80",
                        "status": "completed",
                        "summary": "库存查询结果：急救包可用12个，绷带30卷，注射器80支，满足需求并可挑选批次。",
                        "children": []
                    },
                    {
                        "id": "outbound_strategy",
                        "label": "✅ 出库策略：保质期优先+FIFO",
                        "status": "active",
                        "summary": "采用保质期优先结合先进先出，选择最早到期批次；急救包批次A(5个,30天)与批次B(5个,45天)，绷带批次C(20卷,60天)，注射器批次D(40支,90天)。",
                        "children": [
                            {
                                "id": "fifo_strategy",
                                "label": "FIFO策略：按入库时间排序",
                                "status": "completed",
                                "summary": "以入库时间从早到晚排序，确保先入先出。",
                                "children": []
                            },
                            {
                                "id": "expiry_priority_strategy",
                                "label": "保质期优先：先用30/45天批次",
                                "status": "completed",
                                "summary": "优先提取剩余保质期30天与45天的急救包，降低过期风险。",
                                "children": []
                            },
                            {
                                "id": "batch_selection",
                                "label": "批次选择：A5+B5，C20，D40",
                                "status": "completed",
                                "summary": "选择急救包批次A 5个+B 5个，绷带批次C 20卷，注射器批次D 40支。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "loading_and_handover",
                        "label": "🚚 装载与交接：生成移交单并推荐厢式车",
                        "status": "pending",
                        "summary": "生成出库与移交记录，推荐1辆小型厢式车进行运输，附上批次与数量明细。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务分析与解析",
                    "summary": "对“为医疗小组准备急救包10个、绷带20卷、注射器40支”进行结构化解析，时限1小时。",
                    "key_points": [
                        "抽取物资类型3类：急救包、绷带、注射器",
                        "数量需求：10/20/40，合计70件",
                        "时限要求1小时内完成出库并交接"
                    ],
                    "knowledge_trace": "任务文本 → 物资与数量抽取 → 时限确认 → 形成出库需求。"
                },
                "task_requirement_parsing": {
                    "title": "任务需求解析",
                    "summary": "解析得到3类物资共70件，并标注急救包最高优先级。",
                    "key_points": [
                        "物资类型识别：急救包/绷带/注射器",
                        "数量需求：10/20/40",
                        "优先级：急救包 > 绷带 > 注射器"
                    ],
                    "knowledge_trace": "任务要素提取 → 数量与优先级标注 → 输出需求清单。"
                },
                "material_type_identification": {
                    "title": "物资类型识别",
                    "summary": "确定需出库物资类型为急救包、绷带、注射器三类。",
                    "key_points": [
                        "从描述中抽取“急救包”“绷带”“注射器”",
                        "归并为3个类别便于后续匹配",
                        "为库存匹配提供类型索引"
                    ],
                    "knowledge_trace": "文本解析 → 实体抽取 → 形成物资类型列表。"
                },
                "quantity_requirement_analysis": {
                    "title": "数量需求分析",
                    "summary": "需求数量：急救包10个、绷带20卷、注射器40支。",
                    "key_points": [
                        "读取需求量：10/20/40",
                        "汇总总件数70件便于容量核验",
                        "为库存差额和批次选择做输入"
                    ],
                    "knowledge_trace": "任务需求 → 数量提取 → 形成数量矩阵。"
                },
                "priority_analysis": {
                    "title": "优先级分析",
                    "summary": "急救包最高，其次绷带，再次注射器，依据任务紧急性排序。",
                    "key_points": [
                        "按救治关键度排序：急救包 > 绷带 > 注射器",
                        "优先级用于冲突或不足时的选择依据",
                        "与批次选择的保质期策略组合使用"
                    ],
                    "knowledge_trace": "任务紧急性判断 → 物资关键度排序 → 输出优先级表。"
                },
                "inventory_matching": {
                    "title": "库存匹配",
                    "summary": "库存结果：急救包12个(批次A/B)，绷带30卷(批次C)，注射器80支(批次D)，满足需求。",
                    "key_points": [
                        "查询库存：急救包A(5个,30天), B(7个,45天)",
                        "绷带C(30卷,60天)，注射器D(80支,90天)",
                        "可覆盖需求量并支持保质期优先"
                    ],
                    "knowledge_trace": "库存查询 → 按类型汇总数量与批次 → 输出可用清单。"
                },
                "outbound_strategy": {
                    "title": "出库策略",
                    "summary": "采用保质期优先+FIFO，选择急救包A 5个+B 5个，绷带C 20卷，注射器D 40支。",
                    "key_points": [
                        "策略组合：保质期优先 + 先进先出",
                        "急救包：A(30天)5个 + B(45天)5个满足10个需求",
                        "绷带：C(60天)提取20/30卷；注射器：D(90天)提取40/80支",
                        "留存余量便于后续任务：A余0，B余2，C余10，D余40"
                    ],
                    "knowledge_trace": "需求清单 → 库存批次 → 保质期与FIFO排序 → 批次锁定并生成出库方案。",
                    "knowledge_graph": {
                        "nodes": [
                            # 主推理链节点
                            {"id": "requirement_parsing", "label": "任务需求解析", "type": "input"},
                            {"id": "inventory_matching", "label": "库存匹配", "type": "process"},
                            {"id": "strategy_selection", "label": "出库策略选择", "type": "decision"},
                            {"id": "batch_determination", "label": "批次确定", "type": "process"},
                            {"id": "outbound_plan", "label": "出库方案生成", "type": "output"},
                            
                            # 辅助细节节点（与任务相关但相关性较低）
                            {"id": "historical_usage", "label": "历史出库记录", "type": "input"},
                            {"id": "batch_quality", "label": "批次质量检验", "type": "input"},
                            {"id": "transport_capacity", "label": "运输能力评估", "type": "input"},
                            {"id": "urgency_level", "label": "任务紧急度", "type": "input"}
                        ],
                        "edges": [
                            # 主推理链连接
                            {"source": "requirement_parsing", "target": "inventory_matching"},
                            {"source": "inventory_matching", "target": "strategy_selection"},
                            {"source": "strategy_selection", "target": "batch_determination"},
                            {"source": "batch_determination", "target": "outbound_plan"},
                            
                            # 辅助节点的单向连接
                            {"source": "urgency_level", "target": "strategy_selection"}
                            
                            # 注意：historical_usage、batch_quality、transport_capacity 独立存在
                        ]
                    }
                },
                "fifo_strategy": {
                    "title": "先进先出策略",
                    "summary": "批次按入库时间排序，先出库A(最早)再B。",
                    "key_points": [
                        "入库时间：A最早，B次之",
                        "优先取A 5个，再取B满足剩余需求",
                        "避免后入库批次先出，减少库存倒挂"
                    ],
                    "knowledge_trace": "入库时间排序 → 先取早批次 → 输出提取顺序。"
                },
                "expiry_priority_strategy": {
                    "title": "保质期优先策略",
                    "summary": "优先选择剩余保质期短的批次，降低过期风险。",
                    "key_points": [
                        "急救包：A(30天)优先于B(45天)",
                        "绷带/注射器当前批次剩余期均充足，无需拆分",
                        "策略与FIFO一致性校验通过"
                    ],
                    "knowledge_trace": "保质期排序 → 短期批次优先 → 输出批次优先级。"
                },
                "batch_selection": {
                    "title": "批次选择",
                    "summary": "锁定批次：急救包A5+B5，绷带C20，注射器D40，满足需求量。",
                    "key_points": [
                        "按需求锁定数量：10/20/40",
                        "批次映射：A5+B5，C20，D40",
                        "记录批次号与剩余量方便追溯"
                    ],
                    "knowledge_trace": "策略结果 → 批次数量映射 → 生成批次清单。"
                },
                "loading_and_handover": {
                    "title": "装载与交接",
                    "summary": "生成出库移交单，记录批次A5/B5/C20/D40，推荐1辆小型厢式车运输。",
                    "key_points": [
                        "创建移交记录含批次与数量明细",
                        "绑定运输方式：小型厢式车一次装载70件",
                        "交接时间窗口：1小时内完成"
                    ],
                    "knowledge_trace": "批次清单 → 装载与移交单生成 → 运输车辆推荐 → 下发执行。"
                }
            }
        },
    ),
    # 24. 资源维护
    Scenario(
        id="resource_maintenance",  # 24. 资源维护
        model_name="后勤资源管控",
        name="资源维护",
        example_input="对现有无人机电池与医用设备进行例行维护。",
        reasoning_chain="资源状态解析（使用时长、损耗程度、有效期）→ 维护需求判断（需检测/需校准/易损件更换）→ 维护调度策略（优先级排序、资源替换方案）→ 维护记录更新（生成日志并同步至库存系统）",
        prompt=(
            "【后勤资源管控-资源维护专项要求】\n"
            "\n"
            "=== 一、行为树结构要求 ===\n"
            "1. 行为树必须至少包含两层结构（根节点必须有子节点，且至少有一个子节点还有子节点）：\n"
            "   - task_analysis（任务分析与解析，根节点）：\n"
            "       * 明确维护任务范围、资源类型、维护类型等基础信息；\n"
            "       * 至少拆分出\"维护范围识别\"和\"维护类型确定\"两个子层级节点；\n"
            "   - resource_status_parsing（资源状态解析）：\n"
            "       * 至少包含 usage_duration_analysis（使用时长分析）、wear_degree_analysis（损耗程度分析）、expiry_analysis（有效期分析）三个子节点；\n"
            "   - maintenance_requirement_judgment（维护需求判断）：\n"
            "       * 判断需检测/需校准/易损件更换等维护需求；\n"
            "   - maintenance_scheduling_strategy（维护调度策略，核心决策节点）：\n"
            "       * 下方必须细化出 priority_sorting（优先级排序）、resource_replacement_plan（资源替换方案）、schedule_arrangement（调度安排）三个子节点；\n"
            "       * 该节点必须包含 knowledge_graph 字段。\n"
            "   - maintenance_record_update（维护记录更新）：\n"
            "       * 生成日志并同步至库存系统。\n"
            "\n"
            "2. behavior_tree 中每个节点的格式要求：\n"
            "   - label 字段：必须包含具体数值结果，格式示例：\"🔧 资源状态解析：电池使用500小时，损耗30%\"、\"✅ 维护需求判断：需检测\"、\"✅ 维护调度策略：优先级高\"；\n"
            "   - summary 字段：必须包含具体数值、使用时长、损耗程度等量化信息，不能使用空泛描述。\n"
            "\n"
            "=== 二、knowledge_graph 要求 ===\n"
            "maintenance_scheduling_strategy 节点的 knowledge_graph 必须体现完整因果链路：\n"
            "资源状态解析(status_parsing) → 维护需求判断(requirement_judgment) → 优先级排序(priority_sorting) → 资源替换方案(replacement_plan) → 调度安排(schedule_arrangement) → 维护方案生成(maintenance_plan)\n"
            "\n"
            "具体要求：\n"
            "- nodes[].label 必须包含具体参数信息，格式：\"节点名称(具体参数1, 具体参数2, ...)\"\n"
            "- nodes[].type 必须明确标注：input（输入）、process（处理）、decision（决策）、output（输出）\n"
            "- edges 必须明确表示推理方向，连接所有相关节点\n"
            "\n"
            "=== 三、node_insights 详细要求 ===\n"
            "为 behavior_tree 中出现的每一个节点（包括所有子节点）提供详细的 node_insights，每个节点包含：\n"
            "1. title：节点标题（简洁明确）\n"
            "2. summary：必须包含具体数值、使用时长、损耗程度等量化信息\n"
            "3. key_points：3-5条关键要点，每条必须包含具体数值或计算过程\n"
            "4. knowledge_trace：使用箭头（→）连接各个推理步骤，体现完整的推理链条\n"
            "\n"
            "=== 四、输出质量检查清单 ===\n"
            "生成内容后，请确保：\n"
            "□ 行为树至少包含两层结构（根节点有子节点，且至少一个子节点有子节点）\n"
            "□ 至少有一个 node_insights 内的节点包含 knowledge_graph\n"
            "□ 所有 label 包含具体数值\n"
            "□ 所有 summary 包含具体数值而非空泛描述\n"
            "□ 所有 key_points 包含分析过程或具体参数"
        ),
        example_output={
            "default_focus": "maintenance_scheduling_strategy",
            "behavior_tree": {
                "id": "task_analysis",
                "label": "🔧 任务分析：无人机电池/医用设备例行维护",
                "status": "completed",
                "summary": "解析任务：对无人机电池与医用设备开展例行维护，时间窗口48小时，需区分检测/校准/更换。",
                "children": [
                    {
                        "id": "resource_status_parsing",
                        "label": "📊 资源状态解析",
                        "status": "completed",
                        "summary": "统计无人机电池累计使用500小时，健康度70%；医用设备使用800小时，校准周期1000小时。",
                        "children": [
                            {
                                "id": "usage_duration_analysis",
                                "label": "⏱️ 使用时长分析",
                                "status": "completed",
                                "summary": "电池使用500小时，医用设备使用800小时。",
                                "children": []
                            },
                            {
                                "id": "wear_degree_analysis",
                                "label": "📉 损耗程度分析",
                                "status": "completed",
                                "summary": "电池健康度约70%（损耗30%），预计剩余循环200次；设备机械部件轻微磨损。",
                                "children": []
                            },
                            {
                                "id": "expiry_analysis",
                                "label": "📅 有效期分析",
                                "status": "completed",
                                "summary": "电池设计寿命1000小时，现已用500小时；设备校准周期1000小时，剩余200小时缓冲。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "maintenance_requirement_judgment",
                        "label": "✅ 维护需求判断",
                        "status": "completed",
                        "summary": "电池健康度70%需做容量检测与均衡；设备距校准阈值200小时，建议提前校准。",
                        "children": []
                    },
                    {
                        "id": "maintenance_scheduling_strategy",
                        "label": "🎯 维护调度策略",
                        "status": "active",
                        "summary": "排序优先级：1) 电池容量检测与均衡；2) 医用设备校准；3) 电池易损件检查。48小时内完成并预留备份资源。",
                        "children": [
                            {
                                "id": "priority_sorting",
                                "label": "🏆 优先级排序",
                                "status": "completed",
                                "summary": "按剩余寿命与任务风险排序：电池检测 > 设备校准 > 易损件更换，电池检测最先执行。",
                                "children": []
                            },
                            {
                                "id": "resource_replacement_plan",
                                "label": "🔄 资源替换方案",
                                "status": "completed",
                                "summary": "准备2块备用电池、1套备用设备以防检测或校准失败。",
                                "children": []
                            },
                            {
                                "id": "schedule_arrangement",
                                "label": "📅 调度安排",
                                "status": "completed",
                                "summary": "T+4h启动电池检测，T+12h设备校准，T+36h完成复检，T+48h收尾，48小时内完成。",
                                "children": []
                            }
                        ]
                    },
                    {
                        "id": "maintenance_record_update",
                        "label": "🗂️ 维护记录更新",
                        "status": "pending",
                        "summary": "生成维护日志，记录检测/校准结果与替换批次，同步至库存与任务派发系统。",
                        "children": []
                    }
                ]
            },
            "node_insights": {
                "task_analysis": {
                    "title": "任务分析与解析",
                    "summary": "任务范围：无人机电池与医用设备；时间窗48小时；维护类型含检测/校准/更换。",
                    "key_points": [
                        "资源范围：电池×若干，医用设备×1套",
                        "时间要求：48小时内闭环",
                        "需要区分检测、校准与易损件检查"
                    ],
                    "knowledge_trace": "任务描述解析 → 资源与时间窗确认 → 维护类型清单输出。"
                },
                "resource_status_parsing": {
                    "title": "资源状态解析",
                    "summary": "电池使用500h健康度70%，设备使用800h距校准阈值1000h还差200h。",
                    "key_points": [
                        "电池：累计500h/设计1000h，健康度70%",
                        "设备：累计800h，校准周期1000h",
                        "为需求判断提供寿命与健康度基线"
                    ],
                    "knowledge_trace": "使用时长/寿命数据 → 健康度评估 → 输出状态基线。"
                },
                "usage_duration_analysis": {
                    "title": "使用时长分析",
                    "summary": "电池使用500h，设备800h，距离寿命/校准阈值剩余500h/200h。",
                    "key_points": [
                        "电池：500/1000h，剩余500h",
                        "设备：800/1000h，剩余200h至校准",
                        "时长接近阈值需提前调度"
                    ],
                    "knowledge_trace": "时长数据 → 与阈值比对 → 输出剩余裕度。"
                },
                "wear_degree_analysis": {
                    "title": "损耗程度分析",
                    "summary": "电池健康度70%（损耗30%），设备机械磨损轻微。",
                    "key_points": [
                        "电池SOH≈70%，需容量检测与均衡",
                        "损耗水平提示更换风险，中期需备份",
                        "设备无显著磨损，但随校准同步检查"
                    ],
                    "knowledge_trace": "传感/检测数据 → 损耗估计 → 输出健康评级。"
                },
                "expiry_analysis": {
                    "title": "有效期分析",
                    "summary": "电池寿命1000h已用500h；设备校准周期1000h已用800h，需200h内执行校准。",
                    "key_points": [
                        "电池剩余寿命50%，需进入加强检测阶段",
                        "设备距校准阈值200h，宜提前安排",
                        "为调度提供时间优先级依据"
                    ],
                    "knowledge_trace": "设计寿命/周期 → 剩余寿命计算 → 提醒即将到期。"
                },
                "maintenance_requirement_judgment": {
                    "title": "维护需求判断",
                    "summary": "电池需做容量检测与均衡；设备需提前校准；电池易损件需检查。",
                    "key_points": [
                        "SOH 70%触发检测与均衡流程",
                        "设备距阈值200h，安排校准",
                        "同时检查电池连接件/散热片等易损件"
                    ],
                    "knowledge_trace": "状态基线 → 阈值规则 → 判定检测/校准/更换需求。"
                },
                "maintenance_scheduling_strategy": {
                    "title": "维护调度策略",
                    "summary": "优先执行电池检测与均衡，其次设备校准；准备2块备用电池与1套备用设备，48小时内完成并复检。",
                    "key_points": [
                        "优先级：电池检测(高) > 设备校准(中) > 易损件检查(中)",
                        "资源替换：备用电池2块，设备备用1套",
                        "时间表：T+4h检测，T+12h校准，T+36h复检，T+48h收尾"
                    ],
                    "knowledge_trace": "状态与需求 → 优先级排序 → 备份与替换准备 → 排期落表 → 输出维护方案。",
                    "knowledge_graph": {
                        "nodes": [
                            # 主推理链节点
                            {"id": "status_parsing", "label": "资源状态解析", "type": "input"},
                            {"id": "requirement_judgment", "label": "维护需求判断", "type": "process"},
                            {"id": "priority_sorting", "label": "优先级排序", "type": "decision"},
                            {"id": "replacement_plan", "label": "资源替换方案", "type": "process"},
                            {"id": "schedule_arrangement", "label": "调度安排", "type": "process"},
                            {"id": "maintenance_plan", "label": "维护方案生成", "type": "output"},
                            
                            # 辅助细节节点（与任务相关但相关性较低）
                            {"id": "historical_maintenance", "label": "历史维护记录", "type": "input"},
                            {"id": "spare_parts_inventory", "label": "备件库存状态", "type": "input"},
                            {"id": "technician_schedule", "label": "技术人员排班", "type": "input"},
                            {"id": "equipment_downtime", "label": "停机时间成本", "type": "input"}
                        ],
                        "edges": [
                            # 主推理链连接
                            {"source": "status_parsing", "target": "requirement_judgment"},
                            {"source": "requirement_judgment", "target": "priority_sorting"},
                            {"source": "priority_sorting", "target": "replacement_plan"},
                            {"source": "replacement_plan", "target": "schedule_arrangement"},
                            {"source": "schedule_arrangement", "target": "maintenance_plan"},
                            
                            # 辅助节点的单向连接
                            {"source": "historical_maintenance", "target": "requirement_judgment"},
                            {"source": "spare_parts_inventory", "target": "replacement_plan"}
                            
                            # 注意：technician_schedule、equipment_downtime 独立存在
                        ]
                    }
                },
                "priority_sorting": {
                    "title": "优先级排序",
                    "summary": "电池检测与均衡置于最高优先级，其次设备校准，再次易损件检查。",
                    "key_points": [
                        "依据寿命余量与任务影响排序：电池检测 > 设备校准 > 易损件检查",
                        "高优先项在前12小时完成",
                        "降低关键资源失效风险"
                    ],
                    "knowledge_trace": "需求列表 → 风险/剩余寿命评估 → 输出排序结果。"
                },
                "resource_replacement_plan": {
                    "title": "资源替换方案",
                    "summary": "准备2块备用电池和1套备用设备，若检测或校准失败可即时替换。",
                    "key_points": [
                        "备用电池2块覆盖一架次调度需求",
                        "备用设备1套用于校准失败或停机备援",
                        "预留更换记录字段供追溯"
                    ],
                    "knowledge_trace": "优先级结果 → 备份需求评估 → 生成替换与备份配置。"
                },
                "schedule_arrangement": {
                    "title": "调度安排",
                    "summary": "T+4h启动电池检测，T+12h设备校准，T+36h复检，T+48h完成记录更新。",
                    "key_points": [
                        "时间表：4h/12h/36h/48h节点",
                        "确保在主任务前完成校准与检测",
                        "复检结果写回记录以闭环"
                    ],
                    "knowledge_trace": "优先级与资源约束 → 排期与时间节点 → 下发执行计划。"
                },
                "maintenance_record_update": {
                    "title": "维护记录更新",
                    "summary": "将检测/校准结果与替换批次写入日志，并同步库存系统与任务派发系统。",
                    "key_points": [
                        "记录批次、SOH结果、校准时间",
                        "同步库存与派发系统保持一致",
                        "形成可审计的维护链路"
                    ],
                    "knowledge_trace": "执行结果收集 → 记录与同步 → 状态闭环。"
                }
            }
        },
    )   
]