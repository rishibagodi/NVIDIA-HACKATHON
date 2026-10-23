from openai import OpenAI
import os, base64, sys

c = OpenAI(base_url="https://api.tokenfactory.nebius.com/v1/", api_key=os.environ["NEBIUS_API_KEY"])
models = [m.id for m in c.models.list().data if "nemotron" in m.id.lower()]
print("Nemotron models on Token Factory:", *models, sep="\n  ")

img = base64.b64encode(open(sys.argv[1], "rb").read()).decode()
for m in models:
    try:
        r = c.chat.completions.create(model=m, max_tokens=200,
            messages=[{"role": "user", "content": [
                {"type": "text", "text": "List every deadline in this image with its date and time."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}}]}],
            extra_body={"chat_template_kwargs": {"enable_thinking": False}})
        print(f"\n✅ {m}:\n{r.choices[0].message.content}")
    except Exception as e:
        print(f"\n❌ {m}: {str(e)[:150]}")