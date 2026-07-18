#!/bin/zsh

# Focus the Preview window and select the exact tab supplied by default.py.
/usr/bin/osascript - "$1" <<'APPLESCRIPT'
on run argv
	set actionArgument to item 1 of argv
	set AppleScript's text item delimiters to ASCII character 30
	set parts to text items of actionArgument
	set AppleScript's text item delimiters to ""
	if (count of parts) is not 2 then return
	set targetWindowIndex to (item 1 of parts) as integer
	set targetTabIndex to (item 2 of parts) as integer

	tell application "System Events"
		tell process "Preview"
			set frontmost to true
			set previewWindow to window targetWindowIndex
			perform action "AXRaise" of previewWindow
			set tabGroup to first UI element of previewWindow whose role is "AXTabGroup"
			click radio button targetTabIndex of tabGroup
		end tell
	end tell
end run
APPLESCRIPT
