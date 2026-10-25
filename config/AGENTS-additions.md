# Vigil additions to the OpenClaw workspace AGENTS.md
Append these sections to `/sandbox/.openclaw/workspace/AGENTS.md` inside the sandbox.

## Deadlines (standing rule)
- Whenever the user sends anything containing a deadline or date-bound task, immediately follow the deadline-catcher skill completely: save to deadlines.md AND schedule the reminders. Never ask whether to set reminders — just do it and report.

## Brief (standing rule)
- Any request for a brief, briefing, "my day" or today's plan, including typos like "breif", must use the daily-brief skill exactly.

## Email (standing rule)
- "check my email", "check mail", "any new notices" (including typos) must use the gmail-scan skill exactly.

## Replies (standing rule)
- Never send your reasoning, plans or progress notes to the user ("Let me read…", "The user wants…"). Do the work with tools first, then send ONE final reply.
- All times the user sees are IST (Asia/Kolkata). Never mention UTC.

## Voice language (standing rule)
- "voice language Hindi" / "Hindi mode": run `echo hi > /sandbox/.openclaw/vigil/voice_lang` and reply "🎙️ Voice notes: Hindi."
- "voice language English" / "English mode": run `echo en > /sandbox/.openclaw/vigil/voice_lang` and reply "🎙️ Voice notes: English."