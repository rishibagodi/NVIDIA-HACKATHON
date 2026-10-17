# Feedback Log: Nebius Token Factory & NVIDIA Tools

## 2026-10-17

### Nebius Token Factory
- Card details are mandatory before you can generate an API key, even after joining the Builder Program. This is a barrier for students, especially in India, where many cards don't support international billing.
- The Builder Program form gives no clear indication of when or how the credits get applied.

### build.nvidia.com
- Clicking "Generate API Key" on the model page created keys silently without clearly showing the value. I ended up with 3 unknown active keys and had to use the API Keys page instead.

### Nemotron 3.5 Super (via build.nvidia.com)
- Tool calling worked correctly on the first try (set_reminder with text and time extracted).
- Thinking is on by default: 266 tokens for "Say hi in 5 words".
- `chat_template_kwargs: {"enable_thinking": False}` cut this to 30 tokens (~9x).
- A `/no_think` system message did NOT disable thinking. That's inconsistent with older Nemotron behavior, and the docs should say clearly which method applies.

   ## 2026-10-18
   - Nemotron 3 Ultra on build.nvidia.com returned HTTP 503 repeatedly during NemoClaw onboarding.
   - Onboarding: pressing Enter on the messaging and policy-preset screens silently skips them. No confirmation like "nothing selected, continue?". I skipped Telegram and presets by accident.
   - Agent defaulted to UTC for reminders; no timezone prompt during onboarding.
   - Agent context is ~21k tokens after 2 messages (large built-in instructions), which matters for paid inference budgets.