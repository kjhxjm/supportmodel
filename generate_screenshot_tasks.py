#!/usr/bin/env python3
"""
浏览器截图脚本：为所有测试场景生成可视化截图
"""

import json
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import quote

# 从 test_scenarios.py 导入测试场景
from test_scenarios import TEST_SCENARIOS

# 配置
BASE_URL = "http://127.0.0.1:5000"
SCREENSHOT_DIR = "test_screenshots"
BROWSER_WIDTH = 1920  # 较大的宽度以完整展示图谱
BROWSER_HEIGHT = 1200

def sanitize_filename(text: str) -> str:
    """将文本转换为安全的文件名"""
    # 移除或替换不安全的字符
    safe = text.replace("/", "-").replace("\\", "-").replace(":", "-")
    safe = safe.replace("*", "-").replace("?", "-").replace('"', "-")
    safe = safe.replace("<", "-").replace(">", "-").replace("|", "-")
    return safe.strip()

def generate_screenshot_tasks():
    """生成所有截图任务"""
    tasks = []
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        # URL编码输入参数
        encoded_input = quote(scenario["input"])
        url = f"{BASE_URL}/?input={encoded_input}"
        
        # 生成截图文件名
        category_safe = sanitize_filename(scenario["category"])
        test_name_safe = sanitize_filename(scenario["test_name"])
        filename = f"{i:02d}_{scenario['id']}_{test_name_safe}.png"
        
        tasks.append({
            "index": i,
            "total": len(TEST_SCENARIOS),
            "scenario_id": scenario["id"],
            "category": scenario["category"],
            "test_name": scenario["test_name"],
            "input": scenario["input"],
            "url": url,
            "filename": filename,
            "subdir": category_safe
        })
    
    return tasks

def save_screenshot_manifest(tasks, output_dir: Path):
    """保存截图清单"""
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "total_screenshots": len(tasks),
        "browser_size": f"{BROWSER_WIDTH}x{BROWSER_HEIGHT}",
        "tasks": [
            {
                "index": t["index"],
                "scenario_id": t["scenario_id"],
                "category": t["category"],
                "test_name": t["test_name"],
                "input": t["input"],
                "filename": f"{t['subdir']}/{t['filename']}"
            }
            for t in tasks
        ]
    }
    
    manifest_file = output_dir / "screenshot_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 截图清单已保存到: {manifest_file}")

def generate_markdown_index(tasks, output_dir: Path):
    """生成Markdown索引文件"""
    md_file = output_dir / "README.md"
    
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# 测试场景截图索引\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**浏览器尺寸**: {BROWSER_WIDTH}x{BROWSER_HEIGHT}\n\n")
        f.write(f"**总计截图**: {len(tasks)}\n\n")
        f.write("---\n\n")
        
        current_category = None
        for task in tasks:
            if task["category"] != current_category:
                current_category = task["category"]
                f.write(f"\n## {current_category}\n\n")
            
            f.write(f"### {task['index']}. {task['test_name']}\n\n")
            f.write(f"**输入**: {task['input']}\n\n")
            f.write(f"**场景ID**: `{task['scenario_id']}`\n\n")
            f.write(f"![{task['test_name']}](./{task['subdir']}/{task['filename']})\n\n")
            f.write("---\n\n")
    
    print(f"✅ Markdown索引已保存到: {md_file}")

def print_browser_commands(tasks, output_dir: Path):
    """打印需要在浏览器中执行的命令清单"""
    commands_file = output_dir / "browser_commands.txt"
    
    with open(commands_file, "w", encoding="utf-8") as f:
        f.write("# 浏览器自动化命令清单\n\n")
        f.write("# 以下是需要执行的步骤，可以手动执行或使用浏览器自动化工具\n\n")
        f.write(f"## 1. 设置浏览器窗口大小\n")
        f.write(f"宽度: {BROWSER_WIDTH}px\n")
        f.write(f"高度: {BROWSER_HEIGHT}px\n\n")
        
        for task in tasks:
            f.write(f"\n## 截图 {task['index']}/{task['total']}: {task['test_name']}\n")
            f.write(f"URL: {task['url']}\n")
            f.write(f"截图文件: {task['subdir']}/{task['filename']}\n")
            f.write(f"等待: 等待页面加载完成，确保图谱渲染完成\n")
            f.write(f"截图元素: .main-layout\n")
            f.write("-" * 80 + "\n")
    
    print(f"✅ 浏览器命令清单已保存到: {commands_file}")

def main():
    """主函数"""
    print("="*80)
    print("支援模型截图任务生成器")
    print("="*80)
    
    # 创建输出目录
    output_dir = Path(SCREENSHOT_DIR)
    output_dir.mkdir(exist_ok=True)
    
    # 生成所有任务
    tasks = generate_screenshot_tasks()
    
    # 为每个类别创建子目录
    for task in tasks:
        subdir = output_dir / task["subdir"]
        subdir.mkdir(exist_ok=True)
    
    print(f"\n生成了 {len(tasks)} 个截图任务")
    print(f"输出目录: {output_dir.absolute()}")
    
    # 保存清单和索引
    save_screenshot_manifest(tasks, output_dir)
    generate_markdown_index(tasks, output_dir)
    print_browser_commands(tasks, output_dir)
    
    print("\n" + "="*80)
    print("任务清单生成完成！")
    print("="*80)
    print("\n接下来我将使用浏览器自动化工具执行截图任务...")
    
    return tasks, output_dir

if __name__ == "__main__":
    main()

