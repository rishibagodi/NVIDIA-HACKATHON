from openai import OpenAI
import os

c = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=os.environ["NVIDIA_API_KEY"])
model = "nvidia/nemotron-3.5-super-vl-120b-a12b"

# Test 1: find which "thinking off" method works
variants = {
    "enable_thinking": dict(extra_body={"chat_template_kwargs": {"enable_thinking": False}}),
    "thinking": dict(extra_body={"chat_template_kwargs": {"thinking": False}}),
    "no_think": dict(),
}
for name, kw in variants.items():
    msgs = [{"role": "user", "content": "Say hi in 5 words"}]
    if name == "no_think":
        msgs.insert(0, {"role": "system", "content": "/no_think"})
    r = c.chat.completions.create(model=model, messages=msgs, **kw)
    m = r.choices[0].message
    print(name, "| reasoning:", bool(getattr(m, "reasoning_content", None)), "| tokens:", r.usage.total_tokens)

# Test 2: tool calling
tools = [{"type": "function", "function": {
    "name": "set_reminder",
    "description": "Set a reminder for the user",
    "parameters": {"type": "object",
                   "properties": {"text": {"type": "string"}, "time": {"type": "string"}},
                   "required": ["text", "time"]}}}]

r = c.chat.completions.create(model=model, tools=tools,
                              messages=[{"role": "user", "content": "Remind me to submit DBMS assignment at 9pm"}])
print("tool call:", r.choices[0].message.tool_calls)