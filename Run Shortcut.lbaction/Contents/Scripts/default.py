#!/usr/bin/env python3
"""List Shortcuts actions and filter them without shell interpolation."""
import json
import subprocess
import sys

query = (sys.argv[1] if len(sys.argv) > 1 else "").casefold().strip()
try:
    result = subprocess.run(["/usr/bin/shortcuts", "list"], capture_output=True, text=True, timeout=15, check=True)
except (subprocess.SubprocessError, OSError) as error:
    print(json.dumps([{
        "title": "无法读取快捷指令", "subtitle": "请打开‘快捷指令’App 后再试：" + str(error),
        "icon": "font-awesome:fa-exclamation-triangle",
    }], ensure_ascii=False))
    raise SystemExit

names = [name.strip() for name in result.stdout.splitlines() if name.strip()]
if query:
    names = [name for name in names if query in name.casefold()]
items = [{
    "title": name,
    "subtitle": "运行快捷指令",
    "icon": "font-awesome:fa-magic",
    "label": "↩ 运行",
    "action": "run.py",
    "actionArgument": name,
    "actionRunsInBackground": True,
} for name in names[:100]]
if not items:
    items.append({"title": "未找到快捷指令", "subtitle": "可输入中文或英文名称筛选", "icon": "font-awesome:fa-search"})
print(json.dumps(items, ensure_ascii=False))
