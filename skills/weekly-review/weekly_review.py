#!/usr/bin/env python3
"""Vigil weekly review: done vs. missed in the last 7 days, and the load in the next 7 days."""
import re
from collections import Counter
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))
LINE = re.compile(r"^- \[([ x!])\] (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) IST \| (.+?) \| (.+?) \| (.*?) \| src: (.*?) \| id: ([a-z0-9-]+)\s*$")
FILE = "/sandbox/.openclaw/workspace/deadlines.md"

now = datetime.now(IST)
done, missed, ahead = [], [], []
for line in open(FILE, encoding="utf-8"):
    m = LINE.match(line.strip())
    if not m:
        continue
    due = datetime.strptime(m[2], "%Y-%m-%d %H:%M").replace(tzinfo=IST)
    if now - timedelta(7) <= due < now:
        (done if m[1] == "x" else missed).append((due, m[3]))
    elif now <= due <= now + timedelta(7) and m[1] == " ":
        ahead.append((due, m[3]))

out = [f"📊 Weekly review — {now - timedelta(7):%d %b} to {now:%d %b}"]
out.append(f"✅ Done: {len(done)}" + (f" — {', '.join(t for _, t in sorted(done))}" if done else ""))
out.append(f"❌ Not marked done: {len(missed)}" + (f" — {', '.join(t for _, t in sorted(missed))}" if missed else ""))
if done or missed:
    out.append(f"📈 Completion: {round(100 * len(done) / (len(done) + len(missed)))}%")
if ahead:
    load = Counter(d.date() for d, _ in ahead)
    day, n = min(load.items(), key=lambda kv: (-kv[1], kv[0]))
    out.append(f"📅 Next 7 days: {len(ahead)} deadlines · busiest {day:%a %d %b} ({n})")
else:
    out.append("📅 Next 7 days: nothing due 🎉")
print("\n".join(out))