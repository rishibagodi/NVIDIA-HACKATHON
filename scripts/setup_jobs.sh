#!/usr/bin/env bash
# Run INSIDE the Vigil sandbox after:
#  - onboarding on Nebius Token Factory (main model nvidia/Nemotron-3.5-Super-VL),
#  - uploading skills/ and tools/ into /sandbox/.openclaw/workspace/,
#  - uploading Whisper models into /sandbox/.openclaw/vigil/models/ (whisper-base.en, whisper-small).
# Usage: bash setup_jobs.sh <TELEGRAM_ID> [SMALL_MODEL]
set -euo pipefail
TO="$1"
SMALL="${2:-inference/nvidia/Nemotron-3_5-Lightning}"
W=/sandbox/.openclaw/workspace

# 0. Put your Telegram ID into the skills
sed -i "s/<YOUR_TELEGRAM_ID>/$TO/g" "$W"/skills/*/SKILL.md

# 1. Model limits (a custom-endpoint model entry starts with none; OpenClaw's default 4096 truncates Nemotron)
openclaw config set "models.providers.inference.models[0].maxTokens" 16384 --strict-json
openclaw config set "models.providers.inference.models[0].contextWindow" 131072 --strict-json

# 2. Disable the 30-min heartbeat permanently (saves ~1.2M tokens/day).
#    The runtime switch alone does NOT survive gateway restarts, so also set it in config:
#    every 0m = off; target none + directPolicy block = never messages; small model = cheap if it ever runs.
openclaw system heartbeat disable
openclaw config set agents.defaults.heartbeat '{"every":"0m","target":"none","directPolicy":"block","model":"'"$SMALL"'","lightContext":true}' --strict-json

# 3. Local voice-note transcription (faster-whisper on CPU; audio never leaves the sandbox; default English)
/usr/bin/python3 -m pip install --user --break-system-packages faster-whisper
echo en > /sandbox/.openclaw/vigil/voice_lang
openclaw config set tools.media.models "[{\"type\":\"cli\",\"command\":\"/usr/bin/python3\",\"args\":[\"$W/tools/transcribe.py\",\"{{AttachmentPath}}\"],\"timeoutSeconds\":90,\"capabilities\":[\"audio\"]}]" --strict-json
openclaw config set tools.media.audio '{"enabled":true,"echoTranscript":true,"echoFormat":"📝 \"{transcript}\""}' --strict-json

# 4. Daily brief, 7:55 AM IST, small model
openclaw cron add --name daily-brief --cron "55 7 * * *" --tz Asia/Kolkata --exact --agent main --model "$SMALL" \
  --message "Run exactly: python3 $W/skills/daily-brief/daily_brief.py 2>/dev/null . Reply with its standard output exactly as printed, then add one final line: \"🎯 Do first: <action> — <one short reason>\". Pick the most urgent item; if nothing is due today but a heavy day is listed, suggest starting one of the items on that day early. No other text." \
  --announce --channel telegram --to "$TO" --session isolated --thinking off --light-context

# 5. Weekly review, Sundays 7 PM IST, small model
openclaw cron add --name weekly-review --cron "0 19 * * 0" --tz Asia/Kolkata --exact --agent main --model "$SMALL" \
  --message "Run exactly: python3 $W/skills/weekly-review/weekly_review.py 2>/dev/null . Reply with its standard output exactly as printed, then add one final line: \"💡 Next week: <one concrete suggestion> — <short reason>\". The suggestion must be about UPCOMING deadlines only (e.g. start early for the busiest day). Items under \"Not marked done\" are already past: never suggest completing them. No other text." \
  --announce --channel telegram --to "$TO" --session isolated --thinking off --light-context

# 6. Gmail scan, 7:30 AM and 6:30 PM IST (main model; silent when nothing new)
if [ -f /sandbox/.openclaw/vigil/gmail.json ]; then
  openclaw cron add --name gmail-scan --cron "30 7,18 * * *" --tz Asia/Kolkata --exact --agent main \
    --message "Use the gmail-scan skill to check for new college emails. If there are no new emails, or none of them contain deadlines, reply exactly NO_REPLY and nothing else." \
    --announce --channel telegram --to "$TO" --session isolated
else
  echo "Skipping gmail-scan: create /sandbox/.openclaw/vigil/gmail.json first (see README)."
fi

echo "Done. Finally, append config/AGENTS-additions.md to $W/AGENTS.md"