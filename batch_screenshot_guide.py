#!/usr/bin/env python3
"""
批量截图脚本 - 需要在Cursor AI助手环境中执行
此脚本生成MCP浏览器工具调用指令
"""

from test_scenarios import TEST_SCENARIOS
from urllib.parse import quote

def sanitize_filename(text: str) -> str:
    """将文本转换为安全的文件名"""
    safe = text.replace("/", "-").replace("\\", "-").replace(":", "-")
    safe = safe.replace("*", "-").replace("?", "-").replace('"', "-")
    safe = safe.replace("<", "-").replace(">", "-").replace("|", "-")
    safe = safe.replace(".", "").replace(" ", "_")
    return safe.strip()

# 生成所有截图任务
print("请AI助手执行以下浏览器操作:\n")
print("="*80)

for i, scenario in enumerate(TEST_SCENARIOS, 1):
    category_safe = sanitize_filename(scenario["category"])
    test_name_safe = sanitize_filename(scenario["test_name"])
   encoded_input = quote(scenario["input"])
    url = f"http://127.0.0.1:5000/?input={encoded_input}"
    filename = f"test_screenshots/{category_safe}/{i:02d}_{scenario['id']}.png"
    
    print(f"\n# 任务 {i}/{len(TEST_SCENARIOS)}: {scenario['test_name']}")
    print(f"# 类别: {scenario['category']}")
    print(f"# 输入: {scenario['input']}")
    print(f"\n1. 导航到URL:")
    print(f"   {url}")
    print(f"\n2. 等待5秒让页面加载完成")
    print(f"\n3. 截图并保存到:")
    print(f"   {filename}")
    print("\n" + "-"*80)

print("\n" + "="*80)
print(f"总计: {len(TEST_SCENARIOS)} 个截图任务")

