"""
DeepWorld v5.2 — Multi-Model Adapter (OpenRouter / Ox Alpha)
=============================================================
Routes agent LLM calls through the OpenRouter API.

Backend: stealth/ox-alpha via https://openrouter.ai/api/v1
Auth:    OPENROUTER_API_KEY env var (GitHub Secret in CI)

Retry policy: the Ox Alpha upstream shared pool occasionally returns
HTTP 429 ("temporarily rate-limited upstream") or empty responses with
finish_reason=network_error. Both are transient — we retry with backoff.
"""
import os, json, time
from typing import Any

MAX_RETRIES = 6
RETRY_BASE_DELAY = 5.0  # seconds; exponential backoff


class MultiModelAdapter:
    """Dispatches LLM calls to the configured backend (OpenRouter by default)."""

    def __init__(self):
        self._client = None

    def get_client(self, model: str = None):
        if self._client is None:
            from openai import OpenAI
            api_key = os.environ.get("OPENROUTER_API_KEY", "")
            if not api_key:
                # local fallback: read .env next to repo root
                env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env")
                if os.path.exists(env_path):
                    with open(env_path) as f:
                        for line in f:
                            if line.startswith("OPENROUTER_API_KEY") and "=" in line:
                                api_key = line.strip().split("=", 1)[1]
                                break
            if not api_key:
                raise RuntimeError("OPENROUTER_API_KEY not set")
            self._client = OpenAI(
                api_key=api_key,
                base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
                timeout=120,
            )
        return self._client

    def _is_retryable(self, resp_or_err: Any) -> bool:
        """Detect transient upstream failures worth retrying."""
        # Empty content + no tool_calls (upstream network_error manifests this way)
        try:
            msg = resp_or_err.choices[0].message
            if not getattr(msg, "content", None) and not getattr(msg, "tool_calls", None):
                return True
        except AttributeError:
            pass
        text = str(resp_or_err)
        return any(m in text for m in ("429", "rate-limited", "Rate limit",
                                       "network_error", "temporarily"))

    def create_completion(self, model: str, messages: list, tools: list = None,
                          temperature: float = 0.7, max_tokens: int = 512):
        """Create a chat completion with retries on transient upstream errors."""
        client = self.get_client(model)
        kwargs = dict(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if tools:
            kwargs["tools"] = tools

        last_err = None
        for attempt in range(MAX_RETRIES):
            try:
                resp = client.chat.completions.create(**kwargs)
                msg = resp.choices[0].message
                if getattr(msg, "content", None) or getattr(msg, "tool_calls", None):
                    return resp
                last_err = RuntimeError(
                    f"empty response (finish_reason={resp.choices[0].finish_reason})")
            except Exception as e:
                last_err = e
                if not self._is_retryable(e):
                    raise
            delay = RETRY_BASE_DELAY * (2 ** attempt)
            time.sleep(min(delay, 90))
        raise last_err


# ─── Legacy shim ─────────────────────────────────────────────
# Agents previously overwrote this module with a TensorRouter torch class,
# which broke the import above. Kept as a lightweight stand-in so any
# historical references still resolve without pulling in torch.
class TensorRouter:
    def __init__(self, model_family="nvidia", target_family="nvidia"):
        self.model_family = model_family
        self.target_family = target_family
        self.relay_fee = 0.05

    @property
    def fidelity(self):
        return 1.0 - (self.relay_fee * 0.8)
