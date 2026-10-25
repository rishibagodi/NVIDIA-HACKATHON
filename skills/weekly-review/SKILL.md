---
name: weekly-review
description: ALWAYS use this skill when the user asks for a weekly review, "how did my week go", "week summary" or "review my week". Runs the weekly review script and adds one suggestion.
---

# Weekly Review
1. Run exactly: `python3 {baseDir}/weekly_review.py 2>/dev/null`
2. Reply with its standard output exactly as printed.
3. Add one final line: "💡 Next week: <one concrete suggestion> — <short reason>". The suggestion must be about UPCOMING deadlines only (e.g. start early for the busiest day). Items under "Not marked done" are already past: never suggest completing them.
4. No other text before or after.