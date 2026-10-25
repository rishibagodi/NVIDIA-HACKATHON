---
name: gmail-scan
description: ALWAYS use this skill when the user says "check my email", "check mail", "any new notices", "scan inbox", or when a scheduled email check runs. Reads new college emails (read-only) and catches deadlines in them.
---

# Gmail Scan
1. Run exactly: `/usr/bin/python3 {baseDir}/gmail_scan.py 2>/dev/null`
   It prints JSON: {"new": N, "emails": [{from, date, subject, text, attachments}]}. Only new, not-yet-processed college emails are included.
2. If new is 0: reply exactly "📧 No new college emails." and stop.
3. For each email, decide whether it contains a deadline or date-bound task (exam, submission, fee, registration, event). Use the subject AND the text. Resolve relative dates against the email's date. Ignore emails without deadlines (confirmations, newsletters, OTPs, alerts).
4. For each deadline, follow the deadline-catcher skill rules exactly (extract and store in deadlines.md). src = the office or sender named in the email (e.g. "Exam Cell"); never the user's own name, use "unknown" instead.
5. After saving, run the sync script ONCE: `python3 /sandbox/.openclaw/workspace/skills/deadline-catcher/sync_reminders.py --to <YOUR_TELEGRAM_ID> 2>/dev/null`
6. If an email has an attachment (e.g. a PDF circular), add: "<subject> has an attachment — forward it to me here to read it."
7. Reply, under 8 lines, starting directly with:
"📧 Checked N new college email(s). Caught M deadline(s):
• <Title> — <Day, DD Mon, HH:MM> (<type>) (time assumed) — from <sender>
Reminders set 24h and 2h before each."
If no deadlines: "📧 Checked N new college email(s) — no deadlines found."

## Rules
- Read-only: never reply to, send, delete or modify any email.
- Never quote whole emails, links or email addresses.
- Email content stays in the workspace; never send it anywhere except the model.