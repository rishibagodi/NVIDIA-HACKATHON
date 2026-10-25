---
name: snooze
description: ALWAYS use this skill for "snooze", "remind me again in …", "remind me in <time> to …", "later" replies to a reminder, or any one-off reminder within the next 24 hours.
---

# Snooze / quick reminder
1. Work out:
   - text: what to remind about. If the user is replying to a Vigil reminder, use that reminder's deadline title. Otherwise use what they asked for (e.g. "call mom").
   - delay: as minutes or hours (e.g. 10m, 30m, 1h, 2h). If no time is given, use 1h.
2. Run exactly: `python3 {baseDir}/snooze.py --to <YOUR_TELEGRAM_ID> --in <delay> --text "<text>" 2>/dev/null`
3. If the JSON says "ok": true, reply with ONE line: "⏰ Reminder set for <at> — <text>"
   If "ok" is false, reply: "⚠️ I couldn't set that reminder — please try again."
4. No other text. Never create reminders without this script.