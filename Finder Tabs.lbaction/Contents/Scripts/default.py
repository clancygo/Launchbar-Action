#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""List each currently open Finder location as a LaunchBar item."""

import json
import itertools
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
		set windowID to (id of finderWindow) as text
		set end of rows to windowID & (ASCII character 30) & windowTitle & (ASCII character 30) & folderPath
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
        if not row or row.count("\x1e") < 2:
            continue
        window_id, title, path = row.split("\x1e", 2)
        windows.append((window_id, title, path))
    return windows


def display_title(title, path):
    """Disambiguate same-named folders without sacrificing path navigation."""
    parent = path.rstrip("/").rsplit("/", 2)
    if len(parent) == 3 and parent[1]:
        return f"{title} — {parent[1]}"
    return title


def folder_children(folder_path):
    """Build an explicit browse list without scanning an entire large folder."""
    try:
        with os.scandir(folder_path) as scan:
            # Read one extra entry so we can signal a truncated list. This keeps
            # launching Finder Tabs fast even if another window shows a huge
            # evidence or download directory.
            entries = list(itertools.islice(scan, 301))
    except OSError:
        return [{
            "title": "无法读取此文件夹",
            "subtitle": folder_path,
            "icon": "font-awesome:fa-exclamation-triangle",
        }]

    truncated = len(entries) > 300
    entries = [entry for entry in entries[:300] if not entry.name.startswith(".")]
    entries.sort(
        key=lambda entry: (
            not entry.is_dir(follow_symlinks=False),
            entry.name.casefold(),
        )
    )

    children = []
    for entry in entries:
        is_folder = entry.is_dir(follow_symlinks=False)
        children.append({
            "title": entry.name,
            "subtitle": "文件夹" if is_folder else entry.path,
            "path": entry.path,
            "icon": "font-awesome:fa-folder" if is_folder else "font-awesome:fa-file-o",
        })

    if truncated:
        children.append({
            "title": "仅显示前 300 项",
            "subtitle": "此目录项目较多；请用 Finder 进一步定位。",
            "icon": "font-awesome:fa-ellipsis-h",
        })
    return children


items = []
for window_id, title, path in finder_windows():
    items.append({
        "title": display_title(title, path),
        "subtitle": path,
        "alwaysShowsSubtitle": True,
        "label": "↩ 聚焦  ·  → 浏览",
        "path": path,
        "action": "activate_window.sh",
        # Keep the ID so two windows showing the same folder remain distinct.
        "actionArgument": window_id + "\x1e" + path,
        # An explicit children array makes Right Arrow browse files instead of
        # showing generic item information for this action-backed result.
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
