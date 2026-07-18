#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Open a web search when the user presses Return without choosing a suggestion."""

import subprocess
import sys
from urllib.parse import quote_plus


query = sys.argv[1].strip() if len(sys.argv) > 1 else ""
if query:
    subprocess.run(["/usr/bin/open", "https://www.google.com/search?q=" + quote_plus(query)], check=False)
