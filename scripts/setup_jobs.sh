#!/usr/bin/env bash
# Run inside the Vigil sandbox. Usage: bash setup_jobs.sh <TELEGRAM_ID> [SMALL_MODEL]
set -euo pipefail
TO="$1"
MODEL="${2:-inference/nvidia/nemotron-3.5-lightning-30b-a3b}"

# Raise max output tokens (OpenClaw default 4096 truncates reasoning models like Nemotron 3.5)
openclaw config set "models.providers.inference.models[0].maxTokens" 16384 --strict-json

# Disable the 30-min heartbeat (saves ~1.2M tokens/day)
openclaw system heartbeat disable

# Daily brief at 7:55 AM IST on the small model
openclaw cron add --name daily-brief --cron "55 7 * * *" --tz Asia/Kolkata --exact --agent main --model "$MODEL" \
  --message 'Run exactly: python3 /sandbox/.openclaw/workspace/skills/daily-brief/daily_brief.py 2>/dev/null . Reply with its standard output exactly as printed, then add one final line: "🎯 Do first: <most urgent item> — <one short reason>". If nothing is due, suggest one useful thing to get ahead on. No other text.' \
  --announce --channel telegram --to "$TO" --session isolated --thinking off --light-context