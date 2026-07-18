#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Live Safari bookmark/history lookup plus direct web-search entries."""

import json
import plistlib
import sqlite3
import sys
from pathlib import Path
from urllib.parse import quote_plus


SAFARI_DIR = Path.home() / "Library" / "Safari"
BOOKMARKS_PATH = SAFARI_DIR / "Bookmarks.plist"
HISTORY_PATH = SAFARI_DIR / "History.db"
MAX_PER_SOURCE = 8


def matches(text, query):
    return query.casefold() in text.casefold()


def safari_bookmarks(query):
    try:
        with BOOKMARKS_PATH.open("rb") as source:
            tree = plistlib.load(source)
    except (OSError, plistlib.InvalidFileException):
        return []

    results = []

    def visit(node):
        if len(results) >= MAX_PER_SOURCE:
            return
        if isinstance(node, dict):
            url = node.get("URLString")
            title = node.get("URIDictionary", {}).get("title") or node.get("Title") or url
            if url and title and (matches(title, query) or matches(url, query)):
                results.append((title, url))
            for child in node.get("Children", []):
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(tree)
    return results


def safari_history(query):
    if not HISTORY_PATH.exists():
        return []
    try:
        connection = sqlite3.connect(f"file:{HISTORY_PATH}?mode=ro&immutable=1", uri=True)
        connection.execute("PRAGMA query_only = ON")
        like_query = "%" + query + "%"
        rows = connection.execute(
            """
            SELECT COALESCE(NULLIF(v.title, ''), i.url), i.url
            FROM history_items AS i
            JOIN history_visits AS v ON v.history_item = i.id
            WHERE v.title LIKE ? COLLATE NOCASE OR i.url LIKE ? COLLATE NOCASE
            GROUP BY i.id
            ORDER BY MAX(v.visit_time) DESC
            LIMIT ?
            """,
            (like_query, like_query, MAX_PER_SOURCE),
        ).fetchall()
        connection.close()
        return [(title, url) for title, url in rows if url]
    except sqlite3.Error:
        return []


def url_item(title, subtitle, url, label, icon):
    return {
        "title": title,
        "subtitle": subtitle,
        "alwaysShowsSubtitle": True,
        "url": url,
        "label": label,
        "icon": icon,
    }


query = sys.argv[1].strip() if len(sys.argv) > 1 else ""
if not query:
    print("[]")
    raise SystemExit

items = []
for title, url in safari_bookmarks(query):
    items.append(url_item(title, url, url, "书签", "font-awesome:fa-bookmark"))
for title, url in safari_history(query):
    items.append(url_item(title, url, url, "历史", "font-awesome:fa-history"))

encoded_query = quote_plus(query)
items.extend([
    url_item("Google 搜索：" + query, "在网页中搜索", "https://www.google.com/search?q=" + encoded_query, "网页", "font-awesome:fa-google"),
    url_item("DuckDuckGo 搜索：" + query, "在网页中搜索", "https://duckduckgo.com/?q=" + encoded_query, "网页", "font-awesome:fa-search"),
])

print(json.dumps(items, ensure_ascii=False))
