#!/usr/bin/env python3
"""Vigil: sync reminder automations with deadlines.md.
Idempotent: creates missing reminders, repairs wrong/disabled ones, removes stale and duplicate ones, then verifies."""
import argparse, json, re, subprocess
from collections import defaultdict
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))
LINE = re.compile(r"^- \[([ x!])\] (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) IST \| (.+?) \| (.+?) \| (.*?) \| src: (.*?) \| id: ([a-z0-9-]+)\s*$")
OFFSETS = {"24h": (timedelta(hours=24), "⏰ Tomorrow"), "2h": (timedelta(hours=2), "🚨 Due in 2 hours")}

ap = argparse.ArgumentParser()
ap.add_argument("--to", required=True, help="Telegram chat id to deliver reminders to")
ap.add_argument("--file", default="/sandbox/.openclaw/workspace/deadlines.md")
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

def cron(*a):
    r = subprocess.run(["openclaw", "cron", *a], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError((r.stderr or r.stdout).strip()[-300:])
    return r.stdout

def chat_id(job):
    return str((job.get("delivery") or {}).get("to", "")).split(":")[-1]

def list_jobs():
    out = cron("list", "--json")
    starts = [i for i in (out.find("{"), out.find("[")) if i >= 0]
    data = json.JSONDecoder().raw_decode(out[min(starts):])[0] if starts else []
    if isinstance(data, dict):
        data = data.get("jobs") or data.get("entries") or data.get("items") or []
    found = defaultdict(list)
    for j in data:
        if str(j.get("name", "")).startswith("dl-"):
            found[j["name"]].append(j)
    return found

def act(*a):
    if not args.dry_run:
        cron(*a)

def rm(name, job, label):
    try:
        act("rm", job["id"]); report["removed"].append(f"{name} ({label})")
    except Exception as e:
        report["failed"].append(f"{name}: rm {e}")

now = datetime.now(IST)
want = {}
for line in open(args.file, encoding="utf-8"):
    m = LINE.match(line.strip())
    if not m or m[1] != " ":
        continue
    due = datetime.strptime(m[2], "%Y-%m-%d %H:%M").replace(tzinfo=IST)
    title, details, did = m[3], m[5].strip(), m[7]
    for tag, (off, head) in OFFSETS.items():
        at = due - off
        if at > now + timedelta(minutes=1):
            want[f"dl-{did}-{tag}"] = (at, f"{head}: {title} — due {due:%a %d %b, %H:%M} IST. {details}".strip())

report = {"ok": [], "created": [], "repaired": [], "removed": [], "failed": []}
existing = list_jobs()

for name, jobs in existing.items():
    if name not in want:
        for j in jobs:
            rm(name, j, "stale")
    else:
        for j in jobs[1:]:
            rm(name, j, "duplicate")

for name, (at, text) in want.items():
    job = (existing.get(name) or [None])[0]
    if job:
        d = job.get("delivery") or {}
        cur = datetime.fromisoformat(str((job.get("schedule") or {}).get("at", "1970-01-01T00:00:00+00:00")).replace("Z", "+00:00"))
        if d.get("channel") == "telegram" and chat_id(job) == args.to and job.get("enabled", True) and abs((cur - at).total_seconds()) < 90:
            report["ok"].append(name); continue
        try:
            act("rm", job["id"])
        except Exception as e:
            report["failed"].append(f"{name}: rm {e}"); continue
    try:
        act("add", "--name", name, "--at", at.isoformat(), "--agent", "main",
            "--message", f"Reply with exactly this text and nothing else: {text}",
            "--announce", "--channel", "telegram", "--to", args.to,
            "--session", "isolated", "--thinking", "off", "--light-context", "--delete-after-run")
        report["repaired" if job else "created"].append(f"{name} @ {at:%a %d %b %H:%M} IST")
    except Exception as e:
        report["failed"].append(f"{name}: add {e}")

if not args.dry_run:
    live = list_jobs()
    for name in want:
        jobs = [j for j in live.get(name, []) if j.get("enabled", True) and chat_id(j) == args.to]
        if len(jobs) != 1 and not any(f.startswith(name + ":") for f in report["failed"]):
            report["failed"].append(f"{name}: expected 1 enabled job, found {len(jobs)}")

print(json.dumps(report, indent=1, ensure_ascii=False))