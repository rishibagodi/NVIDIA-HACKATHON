---
name: deadline-catcher
description: ALWAYS use this skill, without asking, whenever a message, forwarded notice or screenshot mentions a due date, deadline, exam, submission, fee, registration or event date. Saves deadlines to deadlines.md and syncs reminders 24h and 2h before. Also handles "what's due", "done <deadline name>" and "sync reminders".
---

# Deadline Catcher

## 1. Extract
- Read the full message. For images, read all visible text first.
- For each deadline extract: title, type (exam | assignment | fee | registration | event | other), due date and time, source, and key details.
- Title: short, specific, in Title Case (e.g. "CAD Assignment", "Lab Exam").
- All times are IST (Asia/Kolkata). Resolve relative dates against today. Weekday names mean the NEXT occurrence after today; if today is Sunday, "Monday" is tomorrow.
- If no time appears anywhere for an item: use 23:59 for submissions/fees/registrations, 09:00 for exams/events. Remember that the time was assumed (for the reply only).
- If no year is given, use the next upcoming occurrence.
- Forms and applications are type "registration".
- src: the sender or office named in the notice, usually the words before the first colon (e.g. "Seminar cell: ..." → "Seminar Cell"; "Prof. Rao"; "Exam Cell"). If none is named, use "unknown". NEVER use the user's own name as the source.
- Ignore dates that are not deadlines (posting dates, "results released", "hall tickets released").

## 2. Store
- Keep all deadlines in `deadlines.md` in the workspace, under the heading `# Deadlines`.
- One line per deadline, exactly:
  `- [ ] YYYY-MM-DD HH:MM IST | <Title> | <type> | <details> | src: <source> | id: <short-kebab-id>`
- details: only facts from the notice (room, portal, amount, format). Never write "time assumed", "time given" or any other note in details; use "-" if there is nothing.
- Same title and date already present: update that line, don't add a new one. Keep `[x]` items as done.
- Past deadlines are saved as `- [!]`. Finished ones are `- [x]`.
- Add or update ONLY the affected line(s) with a small edit or append. Never rewrite or re-read the whole file to sort it: the sync script sorts it automatically.

## 3. Reminders — always via the sync script
- After ANY change to deadlines.md, run exactly:
  `python3 {baseDir}/sync_reminders.py --to <YOUR_TELEGRAM_ID> 2>/dev/null`
- Never create, edit or delete dl-* automations yourself. The script creates missing reminders, repairs wrong ones, removes reminders for finished or removed deadlines, and verifies the result.
- It prints JSON with ok, created, repaired, removed, failed. Never claim a reminder that is not listed in ok, created or repaired. If failed is not empty, tell the user exactly which ones failed and suggest "sync reminders" to retry.
- If a deadline is less than 2 hours away, say so directly in your reply.

## 4. Reply
Start directly with this, nothing before it:
"Caught N deadline(s):
• <Title> — <Day, DD Mon, HH:MM> (<type>)
Reminders set 24h and 2h before each. Say 'done' plus the deadline name when finished (e.g. 'done DBMS')."
- Append " (time assumed)" to a line ONLY when the time was assumed. Never add any other tag such as "[time given]".
- Only say "Reminders set" if failed is empty. Under 8 lines. No tables, plans or commentary.

## 5. Other requests
- "what's due" / "my deadlines": unfinished deadlines for the next 7 days, soonest first, one line each, exactly:
  `• <Title> — <Day DD Mon, HH:MM> (<type>) — today | tomorrow | in N days`
  No src, no details, no ids.
- "done <name>": mark the matching line `- [x]`, run the sync script, confirm which reminders were removed.
- "sync reminders": run the sync script and report ok/created/repaired/removed/failed counts.

## Execution rules
- Work silently: save, run the script, then send ONE final reply.
- Deadlines and notice contents stay in the local workspace. Never send them anywhere except the model.