# Feedback Log — Nebius Token Factory & NVIDIA Tools

Project: **Vigil**, a private, always-on personal assistant (NemoClaw + OpenClaw + Nemotron, Telegram interface)
Environment: Windows 11 + WSL2 (Ubuntu) + Docker Desktop, 7.6 GB RAM allocated to Docker, no local GPU

---

## Nebius Token Factory

### What worked well
- OpenAI-compatible API worked on the first try with the standard `openai` Python SDK.
- Nemotron 3 Super 120B and Nemotron 3 Nano 30B both returned clean content and correct tool calls.
- `chat_template_kwargs: {"enable_thinking": false}` worked out of the box (33 tokens vs. hundreds with thinking on).

### Friction
- **Mandatory card before first API key (2026-10-17).** Even after joining the Builder Program for the hackathon, the console requires card details before generating a key. Many Indian student cards don't support international billing. Suggestion: allow hackathon/Builder credits without a card, or a card-free key capped at the credit amount.
- **Credit-claim flow is unclear.** After submitting the Builder Program form, there is no indication of when or how credits get applied.
- **Trial vs. balance vs. "stop/paid usage" interaction is not explained (2026-10-18).** The dialog offers "Stop usage when trial ends" (card never charged) or "Continue with paid usage" (balance used first). It's unclear whether the account balance can be used at all in "stop" mode. Suggestion: state explicitly which credits each option consumes.

---

## build.nvidia.com (NVIDIA hosted endpoints)

### What worked well
- Free Nemotron access with no card made it possible to start building immediately.
- Nemotron 3.5 Super VL: tool calling correct on the first try; image input (screenshots of notices) worked well.

### Friction
- **"Generate API Key" on the model page creates keys silently (2026-10-17).** The value wasn't clearly shown, so three unknown active keys were created before I used the API Keys page. Suggestion: always show the key in a modal with a copy button.
- **Nemotron 3 Ultra returned HTTP 503 repeatedly during NemoClaw onboarding (2026-10-17).**
- **Intermittent HTTP 500 ("Failed to generate completions") on Super VL (2026-10-18)** caused a NemoClaw rebuild to fail mid-way.

---

## Nemotron models

- **Thinking toggle inconsistency:** `chat_template_kwargs.enable_thinking=false` disabled reasoning (266 → 30 tokens, ~9x saving). A `/no_think` system message did NOT disable it on Nemotron 3.5 Super VL. Docs should state clearly which method applies to which model.
- With thinking on, multi-step agent turns sometimes hit the output-token limit mid-task ("Reply truncated at the model's output token limit"), because reasoning consumes the output budget.

---

## NemoClaw / OpenShell

### What worked well
- One-command install on WSL2; clear onboarding wizard.
- Network policy output is excellent for trust: the agent can only reach allow-listed hosts/paths, and the Telegram policy only allows `/bot<REDACTED>/**` for the node binary.
- `request_body_credential_rewrite` for Tavily means the agent never sees the raw API key, a great privacy feature.
- `openclaw devices` scope approval: the agent cannot grant itself new permissions.

### Bugs and friction (highest impact first)

1. **Stale OpenShell route after switching providers (high).** Switching a sandbox to a compatible endpoint (Token Factory) and back to native `nvidia-prod` with `nemoclaw inference set` left a stale OpenShell workspace route (`compatible-endpoint`). `nemoclaw inference get` showed the native provider, `doctor` reported healthy, but `rebuild` preflight failed with "OpenShell inference route does not match provider". Traffic may also silently go to the paid provider. Fix was `openshell inference delete`. Suggestion: `inference set` should clear the workspace route when switching to a native provider, and `doctor` should detect the mismatch.

2. **Rebuild deletes the sandbox before the inference smoke check (high).** A transient upstream HTTP 500 during rebuild left me with no sandbox (backup preserved). The second attempt then failed with "Provider activation did not match its verified create plan", and I had to destroy and re-onboard. Suggestion: run all provider checks before deleting the old sandbox.

3. **`inference set` gateway pairing never converges on WSL2 + Docker Desktop (medium).** Every `inference set` ended with "OpenClaw gateway pairing did not converge (initial-state-unavailable)" and needed `doctor --fix`.

4. **Onboarding: Enter silently skips multi-select screens (medium).** On the messaging-channel and policy-preset screens, pressing Enter before toggling skips them with no confirmation. I accidentally skipped Telegram and all extra presets. Suggestion: "Nothing selected — continue? [y/N]".

5. **`channels status` false negative (low).** It reported "Bot API reachability: fail" while Telegram actually worked. The probe likely uses a binary not allowed by the telegram policy.

6. **Context window lost on `inference set` to a custom endpoint (low).** "Could not determine the context window... removing the previous route's value."

7. **Under-provisioning warning (info).** 7.6 GB detected vs. 8 GB recommended; builds still succeeded. The 4 GB swap offer during onboarding was helpful.

---

## OpenClaw (agent runtime)

### What worked well
- Skills are simple `SKILL.md` files: no code needed for agent behavior.
- `$baseDir`/workspace skills, cron automations, and Telegram delivery made a real always-on assistant possible in a day.
- `openclaw cron runs <id>` gives excellent diagnostics (delivery status, errors, token usage).

### Friction
- **`cron list` table hides jobs that `--json` shows (high).** The table showed 8 `dl-` jobs while JSON showed 16 (disabled or duplicate jobs were not visible). This led me to believe reminders were missing.
- **Agent-created cron jobs sometimes used delivery target "last" (high).** The job silently fails closed ("no route") instead of delivering to the requesting Telegram chat. Suggestion: default to the originating channel or chat, or warn at creation time.
- **Delivery `to` format is inconsistent (medium).** It's stored as `telegram:<id>` while `--to` accepts `<id>`, which broke naive comparisons in my sync script.
- **Command-payload jobs don't retry delivery (medium).** On a network error, a command job's Telegram delivery failed with no retry, while agent-payload jobs retried and delivered.
- **Skill auto-selection is unreliable without a strong description (medium).** The deadline skill was ignored until the description began with "ALWAYS use this skill..." and a standing rule was added to AGENTS.md.
- **Long agent turns can end with "tool run finished, but no final summary was produced"**, and the task continued in the background and finished ~38 minutes later during network instability. The user had no way to see progress.
- **Default heartbeat (every 30 min) is costly on paid inference.** Each heartbeat is a full agent turn (~25k tokens), about 48 turns/day doing nothing useful. It should be opt-in or longer by default for personal setups.

---

## Summary of the design decision these issues led to
LLM-driven scheduling produced silent delivery failures, duplicates, and disabled jobs. Vigil now uses **Nemotron for understanding** (reading notices and screenshots, extracting deadlines) and a **deterministic, idempotent sync script for scheduling**, which verifies the scheduler before the assistant confirms anything to the user.

---

## 2026-10-23

### NemoClaw / OpenShell
- `nemoclaw <n> connect` refused with "inference.local probe did not return a trusted result" while `doctor` was healthy and the agent replied normally on Telegram (false negative). Workaround: `openshell sandbox exec --name <n> -- <cmd>`.
- Sandbox proxy rejects URLs containing a literal `%` in the query (wttr.in `format=%C,+%t`) with CONNECT 403 / curl exit 56, with no hint that the URL was the problem.
- Gmail preset in read-only `[r]` mode still allows `smtp.gmail.com:465` (sending).
- Weather preset allows `/usr/bin/python3*` but the sandbox Python is elsewhere, so Python HTTP calls were blocked while curl worked. Binary-scoped policy is a great control, but the mismatch is surprising.

### OpenClaw
- `openclaw cron disable` is refused for the system heartbeat job ("system-owned monitor jobs cannot be edited"); `openclaw system heartbeat disable` works (runs show "skipped: disabled", 258 ms vs. 28 s), but the job JSON still shows `enabled: true`.
- **Per-job `--model` works well:** reminder and brief jobs run on Nemotron 3.5 Lightning 30B while the main agent stays on Super VL. Run history confirms the model per run. Excellent for cost-aware routing.
- Smaller models copy stderr noise (`/bin/bash: cannot create /proc/self/oom_score_adj: Permission denied`) into replies verbatim; needed `2>/dev/null`. The harness could filter this sandbox-specific warning.

- Token Factory: only Nemotron-3.5-Super-VL accepts image input; Nano 30B, 3.5 Lightning, Super 120B and Ultra 550B return a clear 400 "This model does not support image input". Clear error, good. Model ID naming is inconsistent (`Nemotron-3_5-Lightning` vs `Nemotron-3.5-Super-VL` vs `NVIDIA-Nemotron-3-Nano-30B-A3B`).

---

## 2026-10-24

### OpenClaw + Nemotron (highest impact finding)
- **Default `maxTokens` of 4096 breaks reasoning models.** Nemotron 3.5 Super VL reasons by default, and OpenClaw's `/think` offers only "off" for it (so the user can't lower reasoning), yet reasoning still consumes the output budget. Result across a week of testing: truncated replies, "The tool run finished, but no final summary was produced", and tool calls cut off with **nothing saved**. Raising `models.providers.inference.models[0].maxTokens` to 16384 via `openclaw config set` fixed every case. Suggestions: a higher default for reasoning models, and have thinking "off" send `chat_template_kwargs.enable_thinking=false` for Nemotron.
- Asking the agent to rewrite a whole file (to keep it sorted) multiplies output tokens; moving sorting into a deterministic script removed the problem.

### Other
- `/think low` returns "not supported... Use one of: off" for Nemotron 3.5 Super VL, so there's no way to choose a middle reasoning level from chat.
- Daily brief scheduled job fired exactly at 07:55 IST unattended; reminders at 16:00 and 21:59 (two in parallel) also delivered on time.

---

## 2026-10-24 / 25

### Positives
- PDF circulars worked with zero extra code: the OpenClaw PDF tool + Nemotron 3.5 Super VL extracted 4 deadlines and the sender from the signature.
- Per-job `--model` + `NO_REPLY` + explicit Telegram delivery made scheduled jobs (daily brief, weekly review, Gmail scan) reliable and cheap.
- Missed scheduled jobs **catch up** after a restart (the 07:55 brief ran at 11:29 when Docker came back).
- Network policy is precise: the gmail preset allows only `/usr/bin/python3` to reach `imap.gmail.com:993`.

### Friction
- **Raw TCP clients can't reach allowed hosts without proxy code.** The sandbox has no direct DNS, so Python `imaplib` fails with "Temporary failure in name resolution" even though the gmail preset allows IMAP. I had to implement an HTTP CONNECT tunnel through `HTTPS_PROXY` myself. The Gmail docs don't mention this; a helper or a note would save hours.
- `huggingface` preset allows `/usr/local/bin/python3`, but the sandbox Python is `/usr/bin/python3`, so model downloads from Python were blocked; I downloaded on the host and used `nemoclaw <n> upload`.
- faster-whisper 1.2.1 + PyAV 19 incompatibility (`metadata_errors` removed), and no PyAV<15 wheel for Python 3.13, so I decoded audio directly with PyAV.
- Gmail preset in read-only mode still allows SMTP sending.
- Small model (Lightning 30B) confused past and upcoming items in summaries until the prompt stated it explicitly.

### Ecosystem note
- College Google Workspace accounts often disable 2-Step Verification, so App Passwords are unavailable; a keyword filter forwarding notices to a dedicated personal inbox worked well and limits what the agent can see.