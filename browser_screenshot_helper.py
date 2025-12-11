#!/usr/bin/env python3
"""
使用Cursor的浏览器MCP工具批量截图
注意：这个脚本需要在Cursor环境中通过AI助手执行
"""

import json
from pathlib import Path
from test_scenarios import TEST_SCENARIOS

# 配置
BASE_URL = "http://127.0.0.1:5000"
SCREENSHOT_DIR = "test_screenshots"
BROWSER_WIDTH = 1920
BROWSER_HEIGHT = 1200

# 等待时间配置
WAIT_FOR_LOAD = 3  # 等待页面加载（秒）
WAIT_FOR_GRAPH = 2  # 等待图谱渲染（秒）

def sanitize_filename(text: str) -> str:
    """将文本转换为安全的文件名"""
    safe = text.replace("/", "-").replace("\\", "-").replace(":", "-")
    safe = safe.replace("*", "-").replace("?", "-").replace('"', "-")
    safe = safe.replace("<", "-").replace(">", "-").replace("|", "-")
    return safe.strip()

# 这个脚本需要AI助手来执行浏览器操作
# 打印任务列表供参考
print("="*80)
print("浏览器截图任务列表")
print("="*80)
print(f"\n总计: {len(TEST_SCENARIOS)} 个场景")
print(f"浏览器尺寸: {BROWSER_WIDTH}x{BROWSER_HEIGHT}")
print(f"基础URL: {BASE_URL}")
print(f"输出目录: {SCREENSHOT_DIR}")
print("\n" + "="*80)

for i, scenario in enumerate(TEST_SCENARIOS, 1):
    category_safe = sanitize_filename(scenario["category"])
    test_name_safe = sanitize_filename(scenario["test_name"])
    
    print(f"\n任务 {i}/{len(TEST_SCENARIOS)}")
    print(f"  类别: {scenario['category']}")
    print(f"  名称: {scenario['test_name']}")
    print(f"  输入: {scenario['input'][:60]}...")
    print(f"  文件: {category_safe}/{i:02d}_{scenario['id']}_{test_name_safe}.png")

