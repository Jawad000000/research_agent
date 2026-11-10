import os
import time

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY"),
    timeout=30,
)

candidates = [
    "nvidia/nemotron-3.5-lightning-30b-a3b",
    "nvidia/nemotron-nano-3-30b-a3b",
    "nvidia/nemotron-3-ultra-550b-a55b",
    "deepseek-ai/deepseek-v4.1-flash",
    "moonshotai/kimi-k2.6",
    "z-ai/glm-5.3-flash",
    "minimaxai/minimax-m3.1-flash",
    "mistralai/mistral-large-4-1t-a52b",
    "google/gemma-4-31b-it",
    "openai/gpt-oss-20b",
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Get the current time",
            "parameters": {"type": "object", "properties": {}},
        },
    }
]

for mid in candidates:
    start = time.perf_counter()
    try:
        r = client.chat.completions.create(
            model=mid,
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=20,
        )
        text = (r.choices[0].message.content or "")[:20]
        secs = time.perf_counter() - start

        # does it accept tools?
        try:
            client.chat.completions.create(
                model=mid,
                messages=[{"role": "user", "content": "What time is it?"}],
                tools=tools,
                max_tokens=50,
            )
            tool_ok = "tools OK"
        except Exception:
            tool_ok = "no tools"

        print(f"WORKS {mid} ({secs:.1f}s, {tool_ok}) -> {text!r}")
    except Exception as e:
        print(f"FAILS {mid} -> {str(e).splitlines()[0][:80]}")
