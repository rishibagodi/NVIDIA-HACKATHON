---
name: daily-brief
description: ALWAYS use this skill when the user asks for a brief, briefing, "my day", "morning brief" or a summary of the day, including typos like "breif" or "brif". Runs the daily brief script and adds one priority suggestion.
---

# Daily Brief
1. Run exactly: `python3 {baseDir}/daily_brief.py 2>/dev/null`
2. Reply with its standard output exactly as printed.
3. Add one final line: "🎯 Do first: <action> — <one short reason>". Pick the most urgent item; if nothing is due today but a heavy day is listed, suggest starting one of that day's items early.
4. No other text before or after.