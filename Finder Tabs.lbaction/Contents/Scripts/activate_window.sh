#!/bin/zsh

# Focus the Finder window already displaying this folder; otherwise open it.
/usr/bin/osascript - "$1" <<'APPLESCRIPT'
on run argv
	set targetPath to item 1 of argv
	tell application "Finder"
		activate
		set finderWindows to (get every Finder window)
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
