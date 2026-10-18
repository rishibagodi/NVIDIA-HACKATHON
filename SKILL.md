---
name: deadline-catcher
description: Extract deadlines from forwarded notices, messages or screenshots, save them to deadlines.md, and schedule reminders 24h and 2h before each one. Also lists upcoming deadlines and marks them done.
---

# Deadline Catcher

Use this skill whenever the user sends or forwards text, a screenshot, or an image that contains dates, due dates, exams, submissions, fees, registrations or events — even if they don't explicitly ask. Also use it when the user asks "what's due", "my deadlines", or says something is done.

## 1. Extract
- Read the full message. For images, read all visible text first.
- For each deadline, extract: title (short, specific), type (exam | assignment | fee | registration | event | other), due date and time, source (who/where it came from, if visible), and one line of key details (room, portal, amount, format).
- All times are in the user's timezone from USER.md (Asia/Kolkata, IST). Resolve relative dates ("tomorrow", "next Monday") against today's date.
- If no time is given: use 23:59 for submissions/fees/registrations, 09:00 for exams/events, and mark it "(time assumed)".
- If no year is given, use the next upcoming occurrence.
- Ignore dates that are not deadlines (e.g. the date a notice was posted).

## 2. Store
- Keep all deadlines in `deadlines.md` in the workspace. Create it if missing, with the heading `# Deadlines`.
- One line per deadline, exactly this format:
  `- [ ] YYYY-MM-DD HH:MM IST | <title> | <type> | <details> | src: <source> | id: <short-kebab-id>`
- Before adding, check for duplicates (same title and date). Update the existing line instead of adding a new one.
- Keep lines sorted by date.

## 3. Schedule reminders
- For each new deadline, schedule two one-time automations delivered to this chat:
  - 24 hours before: "⏰ Tomorrow: <title> — due <day, time>. <details>"
  - 2 hours before: "🚨 Due in 2 hours: <title>. <details>"
- Name the jobs `dl-<id>-24h` and `dl-<id>-2h`.
- Skip any reminder whose time is already in the past. If the deadline is less than 2 hours away, send an immediate heads-up instead.
- If the deadline itself has already passed, save it as `- [!]` (missed) and do not schedule reminders.

## 4. Reply
Reply briefly, in this shape:
"Caught N deadline(s):
- <title> — <Day, DD Mon, HH:MM> (<type>) [time assumed]
Reminders set 24h and 2h before each. Say 'done <title>' when finished."
Do not repeat the whole notice back.

## 5. Other requests
- "what's due" / "my deadlines": list unfinished deadlines for the next 7 days from deadlines.md, soonest first, with days remaining.
- "done <title>": mark the matching line `- [x]`, delete its `dl-<id>-24h` and `dl-<id>-2h` automations, and confirm.

## Privacy
Deadlines and notice contents stay in the local workspace. Never send them to any external service other than the model.