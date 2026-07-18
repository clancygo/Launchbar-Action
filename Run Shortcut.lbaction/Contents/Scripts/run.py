#!/usr/bin/env python3
import subprocess
import sys

if len(sys.argv) > 1:
    subprocess.Popen(["/usr/bin/shortcuts", "run", sys.argv[1]])
