#!/usr/bin/env python3
"""
设备投放支援模型 - 批量浏览器自动化测试脚本

功能：
- 自动生成所有设备投放场景的测试清单
- 支持自定义服务器地址
- 输出标准化的测试信息供浏览器自动化工具使用

用法：
  python3 batch_test.py                        # 使用默认地址 http://127.0.0.1:5000
  python3 batch_test.py http://192.168.1.100:5000  # 指定服务器地址

输出：
  - 控制台输出测试清单
  - 生成 screenshots/equipment_delivery/test_manifest.json
  
配合使用：
  在 Cursor 中告诉 AI 助手：
  "请使用浏览器工具（1440x900窗口），按照 batch_test.py 生成的清单，
   依次访问每个 URL，等待'推理中...'消失后截图保存"
"""

import os
import sys
import json
from urllib.parse import quote

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from support_models.scenarios import SCENARIOS

# 配置
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5000"
SCREENSHOT_DIR = "screenshots/equipment_delivery"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# 获取设备投放场景
equipment_scenarios = [s for s in SCENARIOS if s.model_name == "设备投放"]

# 生成测试清单
test_manifest = []
for idx, scenario in enumerate(equipment_scenarios, 1):
    encoded_input = quote(scenario.example_input)
    test_manifest.append({
        "index": idx,
        "id": scenario.id,
        "name": scenario.name,
        "input": scenario.example_input,
        "url": f"{BASE_URL}/?input={encoded_input}",
        "screenshot": f"{SCREENSHOT_DIR}/{idx:02d}_{scenario.id}.png"
    })

# 保存测试清单
manifest_file = f"{SCREENSHOT_DIR}/test_manifest.json"
with open(manifest_file, "w", encoding="utf-8") as f:
    json.dump(test_manifest, f, ensure_ascii=False, indent=2)

print("=" * 80)
print("设备投放支援模型 - 批量测试")
print("=" * 80)
print(f"服务器地址: {BASE_URL}")
print(f"测试场景数: {len(test_manifest)}")
print(f"截图保存: {os.path.abspath(SCREENSHOT_DIR)}")
print(f"测试清单: {manifest_file}")
print("=" * 80)
print()

for item in test_manifest:
    print(f"{item['index']}. {item['name']}")
    print(f"   URL: {item['url']}")
    print(f"   截图: {item['screenshot']}")
    print()

print("=" * 80)
print("在 Cursor 中使用浏览器自动化测试:")
print("=" * 80)
print("1. 确保服务器运行在上述地址")
print("2. 告诉 AI 助手:")
print("   '使用浏览器工具（1440x900窗口），按照上述清单，")
print("   依次访问每个 URL，等待'推理中...'消失后全页截图保存'")
print("=" * 80)

# 输出测试清单供 AI 助手使用
print("\n[TEST_MANIFEST_FOR_AI]")
print(json.dumps(test_manifest, ensure_ascii=False, indent=2))
