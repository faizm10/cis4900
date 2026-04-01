"""
HTTP clients for OpenAI-compatible, Anthropic Claude, and Google Gemini APIs.
"""

from __future__ import annotations

import httpx

from app.config import settings


def _timeout() -> httpx.Timeout:
    return httpx.Timeout(settings.LLM_TIMEOUT_SEC)


def call_openai_chat(system: str, user: str) -> str:
    """OpenAI or OpenAI-compatible POST .../chat/completions."""
    if not settings.LLM_API_KEY:
        raise RuntimeError(
            "Tutor is disabled for provider openai: set LLM_API_KEY (or OPENAI_API_KEY)."
        )
    url = f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions"
    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": 500,
        "temperature": 0.5,
    }
    with httpx.Client(timeout=_timeout()) as client:
        r = client.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.LLM_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        r.raise_for_status()
        data = r.json()
    try:
        return str(data["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError("Unexpected response from OpenAI-compatible API") from e


def call_anthropic_messages(system: str, user: str) -> str:
    """Anthropic Messages API."""
    if not settings.ANTHROPIC_API_KEY:
        raise RuntimeError("Tutor is disabled for provider anthropic: set ANTHROPIC_API_KEY.")
    url = f"{settings.ANTHROPIC_API_URL.rstrip('/')}/v1/messages"
    payload = {
        "model": settings.ANTHROPIC_MODEL,
        "max_tokens": 1024,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    with httpx.Client(timeout=_timeout()) as client:
        r = client.post(
            url,
            headers={
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "anthropic-version": settings.ANTHROPIC_VERSION,
                "Content-Type": "application/json",
            },
            json=payload,
        )
        r.raise_for_status()
        data = r.json()
    try:
        blocks = data["content"]
        texts: list[str] = []
        for block in blocks:
            if isinstance(block, dict) and block.get("type") == "text":
                texts.append(str(block.get("text", "")))
        out = "\n".join(t for t in texts if t).strip()
        if not out:
            raise KeyError("no text content")
        return out
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError("Unexpected response from Anthropic API") from e


def call_gemini_generate(system: str, user: str) -> str:
    """Google Gemini generateContent (API key as query param)."""
    if not settings.GEMINI_API_KEY:
        raise RuntimeError("Tutor is disabled for provider gemini: set GEMINI_API_KEY.")
    model = settings.GEMINI_MODEL.strip()
    base = settings.GEMINI_API_BASE_URL.rstrip("/")
    url = f"{base}/v1beta/models/{model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"temperature": 0.5, "maxOutputTokens": 1024},
    }
    with httpx.Client(timeout=_timeout()) as client:
        r = client.post(
            url,
            params={"key": settings.GEMINI_API_KEY},
            headers={"Content-Type": "application/json"},
            json=payload,
        )
        r.raise_for_status()
        data = r.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
        texts = [p.get("text", "") for p in parts if isinstance(p, dict)]
        out = "\n".join(t for t in texts if t).strip()
        if not out:
            raise KeyError("empty text")
        return out
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError("Unexpected response from Gemini API") from e


def dispatch_llm(system: str, user: str) -> str:
    provider = (settings.LLM_PROVIDER or "anthropic").strip().lower()
    if provider == "openai":
        return call_openai_chat(system, user)
    if provider == "anthropic":
        return call_anthropic_messages(system, user)
    if provider == "gemini":
        return call_gemini_generate(system, user)
    raise RuntimeError(
        f"Unknown LLM_PROVIDER={provider!r}. Use: openai, anthropic, gemini."
    )
