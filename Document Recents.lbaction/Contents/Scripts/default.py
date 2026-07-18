#!/usr/bin/env python3
"""List Word recent files plus recently modified local documents."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".docm", ".pages", ".rtf", ".txt", ".md",
    ".xls", ".xlsx", ".numbers", ".ppt", ".pptx", ".key",
}
SEARCH_FOLDERS = [Path.home() / name for name in ("Documents", "Desktop", "Downloads")]
QUERY = " || ".join(f'kMDItemFSName == "*{suffix}"cd' for suffix in sorted(EXTENSIONS))
needle = (sys.argv[1] if len(sys.argv) > 1 else "").casefold().strip()
word_list = Path(__file__).with_name("word_recents.txt")

paths = set()
for folder in SEARCH_FOLDERS:
    if not folder.is_dir():
        continue
    try:
        result = subprocess.run(
            ["/usr/bin/mdfind", "-onlyin", str(folder), QUERY],
            capture_output=True, text=True, timeout=12, check=True,
        )
        paths.update(Path(line) for line in result.stdout.splitlines() if line)
    except (subprocess.SubprocessError, OSError):
        continue

documents = []
seen = set()

# Keyboard Maestro refreshes this file from Word's native "recent file" list.
try:
    word_paths = [Path(line.strip()) for line in word_list.read_text(encoding="utf-8").splitlines() if line.strip()]
except OSError:
    word_paths = []
for path in word_paths:
    try:
        stat = path.stat()
    except OSError:
        continue
    if needle and needle not in f"{path.name} {path.parent}".casefold():
        continue
    seen.add(path)
    documents.append((stat.st_mtime, path, "Word 最近打开"))

for path in paths:
    try:
        if not path.is_file() or path.name.startswith("~$") or path.suffix.casefold() not in EXTENSIONS:
            continue
        stat = path.stat()
    except OSError:
        continue
    searchable = f"{path.name} {path.parent}".casefold()
    if needle and needle not in searchable:
        continue
    if path not in seen:
        documents.append((stat.st_mtime, path, "最近修改"))

documents.sort(key=lambda item: (item[2] != "Word 最近打开", -item[0]))
items = []
for modified, path, source in documents[:100]:
    timestamp = datetime.datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M")
    items.append({
        "title": path.name,
        "subtitle": f"{source} {timestamp}  ·  {path.parent}",
        "path": str(path),
        "icon": "font-awesome:fa-file-text-o",
        "label": "↩ 打开 · → 浏览所在位置",
    })

if not items:
    items.append({
        "title": "未找到文档",
        "subtitle": "搜索 Documents、Desktop 和 Downloads 中的 PDF、Word、Pages 等文件",
        "icon": "font-awesome:fa-search",
    })
print(json.dumps(items, ensure_ascii=False))
