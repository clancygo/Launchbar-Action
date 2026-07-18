#!/bin/zsh
argument="$1"
window_id="${argument%%$'\x1e'*}"
tab_index="${argument#*$'\x1e'}"
/usr/bin/osascript - "$window_id" "$tab_index" <<'APPLESCRIPT'
on run argv
    set targetWindowID to item 1 of argv as integer
    set targetTabIndex to item 2 of argv as integer
    tell application "Safari"
        activate
        set targetWindow to first window whose id is targetWindowID
        set current tab of targetWindow to tab targetTabIndex of targetWindow
    end tell
end run
APPLESCRIPT
