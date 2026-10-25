#!/usr/bin/env python3
"""Vigil: sync reminder automations with deadlines.md.
Sorts deadlines.md, then makes the scheduler match it: creates missing reminders, repairs wrong/disabled ones,
removes stale and duplicate ones, and verifies. Reminder runs use a small model, thinking off, and READ-ONLY tools
(least privilege: a delivery-only run must never be able to run scripts or schedule jobs)."""
import argparse, json, re, subprocess
from collections import defaultdict
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))
LINE = re.compile(r"^- \[([ x!])\] (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) IST \| (.+?) \| (.+?) \| (.*?) \| src: (.*?) \| id: ([a-z0-9-]+)\s*$")
OFFSETS = {"24h": (timedelta(hours=24), "⏰ Tomorrow"), "2h": (timedelta(hours=2), "🚨 Due in 2 hours")}
PREFIX = "Output exactly this single line and nothing else (no time, no UTC, no extra lines): "

ap = argparse.ArgumentParser()
ap.add_argument("--to", required=True, help="Telegram chat id to deliver reminders to")
ap.add_argument("--file", default="/sandbox/.openclaw/workspace/deadlines.md")
ap.add_argument("--dry-run", action="store_true")
ap.add_argument("--model", default="inference/nvidia/Nemotron-3_5-Lightning", help="small model for reminder jobs")
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

# Sort deadlines.md deterministically (keeps any unparsed lines so nothing is lost)
lines = [l.strip() for l in open(args.file, encoding="utf-8").read().splitlines()]
entries = sorted((l for l in lines if LINE.match(l)), key=lambda l: LINE.match(l)[2])
others = [l for l in lines if l and not LINE.match(l) and not l.startswith("#")]
if not args.dry_run:
    body = ["# Deadlines", *entries] + (["", "## Unparsed", *others] if others else [])
    open(args.file, "w", encoding="utf-8").write("\n".join(body) + "\n")

now = datetime.now(IST)
want = {}
for line in entries:
    m = LINE.match(line)
    if m[1] != " ":
        continue
    due = datetime.strptime(m[2], "%Y-%m-%d %H:%M").replace(tzinfo=IST)
    title, details, did = m[3], m[5].strip(), m[7]
    details = "" if details == "-" else details
    for tag, (off, head) in OFFSETS.items():
        at = due - off
        if at > now + timedelta(minutes=1):
            text = f"{head}: {title} — due {due:%a %d %b, %H:%M} IST. {details}".strip()
            if tag == "2h":
                text += f" Done already? Reply 'done {title}'."
            want[f"dl-{did}-{tag}"] = (at, text)

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
        d, p = job.get("delivery") or {}, job.get("payload") or {}
        cur = datetime.fromisoformat(str((job.get("schedule") or {}).get("at", "1970-01-01T00:00:00+00:00")).replace("Z", "+00:00"))
        if (d.get("channel") == "telegram" and chat_id(job) == args.to and job.get("enabled", True)
                and abs((cur - at).total_seconds()) < 90 and p.get("model") == args.model
                and p.get("toolsAllow") == ["read"] and p.get("message") == PREFIX + text):
            report["ok"].append(name); continue
        try:
            act("rm", job["id"])
        except Exception as e:
            report["failed"].append(f"{name}: rm {e}"); continue
    try:
        act("add", "--name", name, "--at", at.isoformat(), "--agent", "main", "--message", PREFIX + text,
            "--model", args.model, "--announce", "--channel", "telegram", "--to", args.to,
            "--session", "isolated", "--tools", "read", "--thinking", "off", "--light-context", "--delete-after-run")
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