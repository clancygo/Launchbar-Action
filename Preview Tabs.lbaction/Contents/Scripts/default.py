#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""List all tabs currently visible in macOS Preview windows."""

import json
import subprocess


APPLE_SCRIPT = r'''
tell application "System Events"
	if not (exists process "Preview") then return ""
	tell process "Preview"
		set outputText to ""
		set windowIndex to 0
		repeat with previewWindow in windows
			set windowIndex to windowIndex + 1
			try
				set windowTitle to name of previewWindow
				set tabGroup to first UI element of previewWindow whose role is "AXTabGroup"
				set tabIndex to 0
				repeat with tabItem in radio buttons of tabGroup
					set tabIndex to tabIndex + 1
					set tabTitle to name of tabItem
					set isSelected to value of tabItem as text
					if outputText is not "" then set outputText to outputText & (ASCII character 31)
					set outputText to outputText & (windowIndex as text) & (ASCII character 30) & (tabIndex as text) & (ASCII character 30) & tabTitle & (ASCII character 30) & windowTitle & (ASCII character 30) & isSelected
				end repeat
			end try
		end repeat
		return outputText
	end tell
end tell
'''


def preview_tabs():
    result = subprocess.run(
        ["/usr/bin/osascript", "-e", APPLE_SCRIPT],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        return []

    tabs = []
    for row in result.stdout.rstrip("\n").split("\x1f"):
        if not row or row.count("\x1e") < 4:
            continue
        window_index, tab_index, title, window_title, selected = row.split("\x1e", 4)
        tabs.append((window_index, tab_index, title, window_title, selected == "true"))
    return tabs


items = []
for window_index, tab_index, title, window_title, selected in preview_tabs():
    items.append({
        "title": title,
        "subtitle": window_title,
        "alwaysShowsSubtitle": True,
        "label": "当前" if selected else "Preview",
        "action": "activate_tab.sh",
        "actionArgument": window_index + "\x1e" + tab_index,
        "icon": "font-awesome:fa-file-pdf",
    })

if not items:
    items.append({
        "title": "没有打开的 Preview 标签页",
        "subtitle": "请先在预览中打开 PDF 或图片。",
        "icon": "font-awesome:fa-file-pdf",
    })

print(json.dumps(items, ensure_ascii=False))
