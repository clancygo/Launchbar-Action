#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""List each currently open Finder location as a LaunchBar item."""

import json
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
        "icon": "font-awesome:fa-window-restore",
    })

if not items:
    items.append({
        "title": "没有打开的 Finder 窗口",
        "subtitle": "先在 Finder 中打开一个文件夹后再试。",
        "icon": "font-awesome:fa-folder-open",
    })

print(json.dumps(items, ensure_ascii=False))
