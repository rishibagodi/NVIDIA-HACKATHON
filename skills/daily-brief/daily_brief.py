#!/usr/bin/env python3
"""Vigil daily brief: today's / tomorrow's / this week's deadlines + Bengaluru weather."""
import re, subprocess
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))
LINE = re.compile(r"^- \[([ x!])\] (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) IST \| (.+?) \| (.+?) \| (.*?) \| src: (.*?) \| id: ([a-z0-9-]+)\s*$")
FILE = "/sandbox/.openclaw/workspace/deadlines.md"

now = datetime.now(IST)
today = now.date()
items = []
for line in open(FILE, encoding="utf-8"):
    m = LINE.match(line.strip())
    if m and m[1] == " ":
        due = datetime.strptime(m[2], "%Y-%m-%d %H:%M").replace(tzinfo=IST)
        if due >= now:
            items.append((due, m[3], m[4]))
items.sort()

try:
    weather = subprocess.run(["curl", "-s", "-m", "10", "https://wttr.in/Bengaluru?format=3"], capture_output=True, text=True).stdout.strip().split(": ", 1)[-1] or "unavailable"
except Exception:
    weather = "unavailable"

sections = [
    ("📌 Today", [i for i in items if i[0].date() == today], False),
    ("⏭️ Tomorrow", [i for i in items if i[0].date() == today + timedelta(1)], False),
    ("🗓️ Later this week", [i for i in items if today + timedelta(1) < i[0].date() <= today + timedelta(7)], True),
]
out = [f"☀️ Good morning, Rishi — {now:%a %d %b}", f"Bengaluru: {weather}"]
for title, group, show_day in sections:
    if group:
        out += ["", title] + [f"• {t} — {d:%a %d %b, %H:%M}" if show_day else f"• {t} — {d:%H:%M} ({typ})" for d, t, typ in group]
if not items or not any(g for _, g, _ in sections):
    out += ["", "✅ Nothing due in the next 7 days."]
print("\n".join(out))