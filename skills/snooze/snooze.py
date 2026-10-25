#!/usr/bin/env python3
"""Vigil snooze / quick reminder: one-off reminder in N minutes or hours. Delivered explicitly to Telegram on the
small model with READ-ONLY tools (so the reminder run can't re-snooze itself), idempotent and verified."""
import argparse, hashlib, json, re, subprocess
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))
PREFIX = "Output exactly this single line and nothing else (no time, no UTC, no extra lines): "
ap = argparse.ArgumentParser()
ap.add_argument("--to", required=True, help="Telegram chat id")
ap.add_argument("--in", dest="delay", default="1h", help="e.g. 10m, 30m, 1h, 2h")
ap.add_argument("--text", required=True, help="what to remind about")
ap.add_argument("--model", default="inference/nvidia/Nemotron-3_5-Lightning")
args = ap.parse_args()

def jobs():
    out = subprocess.run(["openclaw", "cron", "list", "--json"], capture_output=True, text=True).stdout
    return json.JSONDecoder().raw_decode(out[out.find("{"):])[0].get("jobs", [])

m = re.fullmatch(r"\s*(\d+)\s*(m|min|mins|minutes?|h|hr|hrs|hours?)\s*", args.delay.lower())
if not m:
    raise SystemExit(json.dumps({"ok": False, "error": f"bad duration: {args.delay}"}))
mins = int(m[1]) * (60 if m[2].startswith("h") else 1)
at = (datetime.now(IST) + timedelta(minutes=mins)).replace(second=0, microsecond=0)
name = f"snooze-{at:%m%d-%H%M}-{hashlib.md5(args.text.lower().encode()).hexdigest()[:6]}"

if not any(j.get("name") == name for j in jobs()):
    subprocess.run(["openclaw", "cron", "add", "--name", name, "--at", at.isoformat(), "--agent", "main",
                    "--message", f"{PREFIX}⏰ Reminder: {args.text}",
                    "--model", args.model, "--announce", "--channel", "telegram", "--to", args.to,
                    "--session", "isolated", "--tools", "read", "--thinking", "off", "--light-context", "--delete-after-run"],
                   capture_output=True, text=True, check=True)

live = [j for j in jobs() if j.get("name") == name and str((j.get("delivery") or {}).get("to", "")).split(":")[-1] == args.to]
print(json.dumps({"ok": len(live) == 1, "name": name, "at": f"{at:%a %d %b, %H:%M} IST", "text": args.text}, ensure_ascii=False))