# backend/app/llm_adapter.py
import os
import httpx
from typing import Optional

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

async def call_llm(prompt: str, model: str = "gpt-4o-mini") -> str:
    """
    Simple adapter — uses OpenAI HTTP API format if key present.
    If no key, returns a deterministic fallback prompt reply.
    """
    if not OPENAI_API_KEY:
        # fallback: echo with a template encouraging canonicalization
        return f"[LLM-FALLBACK]\nI would convert the user request into a symbolic expression. Suggested canonical expression: `{prompt}`"
    # Minimal OpenAI API call (user should supply key and correct endpoint)
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role":"user","content": prompt}],
        "temperature": 0.0,
        "max_tokens": 1024
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
