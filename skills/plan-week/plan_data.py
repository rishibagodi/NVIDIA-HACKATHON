#!/usr/bin/env python3
"""Vigil plan-week data: unfinished deadlines for the next 10 days, grouped by day, with heavy-day flags."""
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))
LINE = re.compile(r"^- \[([ x!])\] (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) IST \| (.+?) \| (.+?) \| (.*?) \| src: (.*?) \| id: ([a-z0-9-]+)\s*$")
FILE = "/sandbox/.openclaw/workspace/deadlines.md"

now = datetime.now(IST)
days = defaultdict(list)
for line in open(FILE, encoding="utf-8"):
    m = LINE.match(line.strip())
    if m and m[1] == " ":
        due = datetime.strptime(m[2], "%Y-%m-%d %H:%M").replace(tzinfo=IST)
        if now <= due <= now + timedelta(10):
            days[due.date()].append((due, m[3], m[4]))

print(f"Today: {now:%A %d %b %Y, %H:%M} IST")
for day in sorted(days):
    items = sorted(days[day])
    exams = sum(1 for _, _, t in items if t == "exam")
    flag = " ⚠️ HEAVY" if len(items) >= 3 or (len(items) >= 2 and exams) else ""
    print(f"\n{day:%a %d %b} ({(day - now.date()).days} days away){flag}")
    for due, title, typ in items:
        print(f"  - {due:%H:%M} {title} [{typ}]")
if not days:
    print("\nNothing due in the next 10 days.")