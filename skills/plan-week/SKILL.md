---
name: plan-week
description: ALWAYS use this skill when the user asks to "plan my week", "make a study plan", "how should I prepare", "schedule my week" or similar (including typos).
---

# Plan My Week
1. Run exactly: `python3 {baseDir}/plan_data.py 2>/dev/null` (unfinished deadlines for the next 10 days, heavy days flagged).
2. Build a realistic plan for the next 7 days, starting today:
   - One line per day: "<Day DD>: <1–2 concrete blocks with times, e.g. 6–8 PM DBMS viva prep>". Skip days with nothing to do.
   - Exams: prep blocks on 2 different days before the exam. Assignments/reports: start at least 1 day before the due day. Registrations/fees: do them early on a light day (15 min).
   - Before a ⚠️ HEAVY day, move work to earlier days so that day is lighter.
   - Assume college 9 AM–4 PM on weekdays; schedule blocks after 5 PM on weekdays and anytime on weekends; max 3 hours of blocks per day; nothing after 10 PM.
   - Never schedule prep after its deadline.
3. End with one line: "⚠️ Watch: <riskiest day and why>".
4. Reply format: start with "🗓️ Your plan for <date range>:", at most 10 lines, no tables, no commentary.