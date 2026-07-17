#!/bin/zsh

# Focus the Finder window already displaying this folder; otherwise open it.
/usr/bin/osascript - "$1" <<'APPLESCRIPT'
on run argv
	set actionArgument to item 1 of argv
	set AppleScript's text item delimiters to ASCII character 30
	set argumentParts to text items of actionArgument
	set AppleScript's text item delimiters to ""
	if (count of argumentParts) is greater than 1 then
		set targetWindowID to item 1 of argumentParts
		set targetPath to item 2 of argumentParts
	else
		-- Backward-compatible fallback for paths emitted by older versions.
		set targetWindowID to ""
		set targetPath to actionArgument
	end if
	tell application "Finder"
		activate
		set finderWindows to (get every Finder window)
		repeat with finderWindow in finderWindows
			try
				if targetWindowID is not "" and ((id of finderWindow) as text) is targetWindowID then
					set index of finderWindow to 1
					return
				end if
			end try
		end repeat
		-- The window may have been closed since the list was displayed. In that
		-- case focus any matching folder, otherwise open the folder normally.
		repeat with finderWindow in finderWindows
			try
				if POSIX path of ((target of finderWindow) as alias) is targetPath then
					set index of finderWindow to 1
					return
				end if
			end try
		end repeat
		open (POSIX file targetPath)
	end tell
end run
APPLESCRIPT
