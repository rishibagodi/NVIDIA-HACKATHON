from openai import OpenAI
import os

c = OpenAI(base_url="https://api.tokenfactory.nebius.com/v1/", api_key=os.environ["NEBIUS_API_KEY"])

tools = [{"type": "function", "function": {
    "name": "set_reminder", "description": "Set a reminder for the user",
    "parameters": {"type": "object",
                   "properties": {"text": {"type": "string"}, "time": {"type": "string"}},
                   "required": ["text", "time"]}}}]

for model in ["nvidia/nemotron-3-super-120b-a12b", "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"]:
    print(f"\n=== {model} ===")
    try:
        r = c.chat.completions.create(model=model,
            messages=[{"role": "user", "content": "Say hi in 5 words"}],
            extra_body={"chat_template_kwargs": {"enable_thinking": False}})
        m = r.choices[0].message
        print("content:", m.content)
        print("reasoning:", bool(getattr(m, "reasoning_content", None)), "| tokens:", r.usage.total_tokens)

        r = c.chat.completions.create(model=model, tools=tools,
            messages=[{"role": "user", "content": "Remind me to submit DBMS assignment at 9pm"}])
        print("tool call:", r.choices[0].message.tool_calls)
    except Exception as e:
        print("ERROR:", e)