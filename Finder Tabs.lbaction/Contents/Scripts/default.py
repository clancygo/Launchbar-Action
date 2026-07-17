#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""List each currently open Finder location as a LaunchBar item."""

import json
import os
import subprocess


APPLE_SCRIPT = r'''
tell application "Finder"
	set rows to {}
	set finderWindows to (get every Finder window)
	repeat with finderWindow in finderWindows
		try
			set folderPath to POSIX path of ((target of finderWindow) as alias)
			set windowTitle to name of finderWindow
			set end of rows to windowTitle & (ASCII character 30) & folderPath
		end try
	end repeat
end tell
set AppleScript's text item delimiters to ASCII character 31
return rows as text
'''


def finder_windows():
    result = subprocess.run(
        ["/usr/bin/osascript", "-e", APPLE_SCRIPT],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        return []

    windows = []
    for row in result.stdout.rstrip("\n").split("\x1f"):
        if not row or "\x1e" not in row:
            continue
        title, path = row.split("\x1e", 1)
        windows.append((title, path))
    return windows


def folder_children(folder_path):
    """Return the immediate contents for LaunchBar's right-arrow browsing."""
    try:
        with os.scandir(folder_path) as scan:
            entries = list(scan)
    except OSError:
        return [{
            "title": "无法读取此文件夹",
            "subtitle": folder_path,
            "icon": "font-awesome:fa-exclamation-triangle",
        }]

    # Keep Finder-like navigation pleasant: folders first, then names.
    entries.sort(
        key=lambda entry: (
            not entry.is_dir(follow_symlinks=False),
            entry.name.casefold(),
        )
    )

    children = []
    for entry in entries[:300]:
        is_folder = entry.is_dir(follow_symlinks=False)
        children.append({
            "title": entry.name,
            "subtitle": "文件夹" if is_folder else entry.path,
            "path": entry.path,
            "icon": (
                "font-awesome:fa-folder"
                if is_folder
                else "font-awesome:fa-file-o"
            ),
        })

    if len(entries) > 300:
        children.append({
            "title": "仅显示前 300 项",
            "subtitle": "请在 Finder 中缩小范围，或用名称继续筛选。",
            "icon": "font-awesome:fa-ellipsis-h",
        })
    return children


items = []
for title, path in finder_windows():
    items.append({
        "title": title,
        "subtitle": "↩ 聚焦窗口  ·  → 浏览文件  ·  " + path,
        "path": path,
        "quickLookURL": path,
        "action": "activate_window.sh",
        "actionArgument": path,
        # Enter invokes the action above. Right Arrow enters these children,
        # turning the selected Finder window into its actual folder listing.
        "children": folder_children(path),
        "icon": "font-awesome:fa-window-restore",
    })

if not items:
    items.append({
        "title": "没有打开的 Finder 窗口",
        "subtitle": "先在 Finder 中打开一个文件夹后再试。",
        "icon": "font-awesome:fa-folder-open",
    })

print(json.dumps(items, ensure_ascii=False))
