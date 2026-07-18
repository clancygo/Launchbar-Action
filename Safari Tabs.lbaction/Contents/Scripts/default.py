#!/usr/bin/env python3
"""Search open Safari tabs by title, URL, and available page text."""
import json
import subprocess
import sys

RS = "\x1e"
US = "\x1f"
QUERY = sys.argv[1] if len(sys.argv) > 1 else ""

SCRIPT = r'''
on run argv
    set needle to item 1 of argv
    set oldDelimiters to AppleScript's text item delimiters
    set AppleScript's text item delimiters to {character id 30}
    set outputLines to {}
    tell application "Safari"
        repeat with w in every window
            set tabNumber to 0
            repeat with t in every tab of w
                set tabNumber to tabNumber + 1
                set tabTitle to name of t as text
                set tabURL to URL of t as text
                set tabText to ""
                try
                    set tabText to text of t as text
                end try
                ignoring case
                    set matches to needle is "" or tabTitle contains needle or tabURL contains needle or tabText contains needle
                end ignoring
                if matches then
                    set tabTitle to my cleanText(tabTitle)
                    set tabURL to my cleanText(tabURL)
                    set end of outputLines to ((id of w as text) & (character id 31) & (tabNumber as text) & (character id 31) & tabTitle & (character id 31) & tabURL)
                end if
            end repeat
        end repeat
    end tell
    set AppleScript's text item delimiters to oldDelimiters
    return outputLines as text
end run

on cleanText(theText)
    set theText to my replaceText(theText, return, " ")
    set theText to my replaceText(theText, linefeed, " ")
    set theText to my replaceText(theText, character id 30, " ")
    set theText to my replaceText(theText, character id 31, " ")
    return theText
end cleanText

on replaceText(theText, findText, replacementText)
    set oldDelimiters to AppleScript's text item delimiters
    set AppleScript's text item delimiters to findText
    set theItems to text items of theText
    set AppleScript's text item delimiters to replacementText
    set theText to theItems as text
    set AppleScript's text item delimiters to oldDelimiters
    return theText
end replaceText
'''

try:
    completed = subprocess.run(
        ["/usr/bin/osascript", "-", QUERY], input=SCRIPT, text=True,
        capture_output=True, timeout=12, check=True,
    )
    records = [line for line in completed.stdout.split(RS) if line]
except (subprocess.SubprocessError, OSError) as error:
    print(json.dumps([{"title": "Safari 标签读取失败", "subtitle": str(error), "icon": "font-awesome:fa-exclamation-triangle"}], ensure_ascii=False))
    raise SystemExit

items = []
for record in records[:80]:
    parts = record.split(US)
    if len(parts) != 4:
        continue
    window_id, tab_index, title, url = parts
    items.append({
        "title": title or url,
        "subtitle": url,
        "icon": "font-awesome:fa-safari",
        "label": "↩ 切换标签页",
        "action": "activate_tab.sh",
        "actionArgument": window_id + RS + tab_index,
        "actionRunsInBackground": True,
    })

if not items:
    items.append({"title": "未找到 Safari 标签页", "subtitle": "可输入标题、网址或页面正文", "icon": "font-awesome:fa-search"})
print(json.dumps(items, ensure_ascii=False))
