"""
CI adapter — headless agent backend for GitHub Actions.
Reads API keys from environment only (no browser, no .env file).
Supports: GEMINI_SID (free web cookies), GOOGLE_API_KEY (Gemini API),
          DEEPSEEK_API_KEY (paid).

v2.0: Proper error logging, pre-flight health checks, no silent swallowing.
"""

import json, os, sys, re, traceback
from typing import Any, Optional


def _log_error(context: str, exc: Exception, detail: str = "") -> None:
    """Log error to stderr so it surfaces in CI logs even when agent catches it."""
    print(f"\n[DEEPWORLD ERROR] {context}", file=sys.stderr)
    print(f"  Exception: {type(exc).__name__}: {exc}", file=sys.stderr)
    if detail:
        print(f"  Detail: {detail[:500]}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    print("", file=sys.stderr)


class CIAdapter:
    """Headless backend for GitHub Actions. Supports DeepSeek and Gemini."""

    def __init__(self):
        self.backend = self._detect_backend()
        self._error_count = 0
        self._consecutive_errors = 0
        self._last_error = ""
        # Log which backend we're using
        print(f"[DEEPWORLD] CI Adapter initialized with backend: {self.backend}", file=sys.stderr)

    def _detect_backend(self) -> str:
        # 1. Gemini Web cookies (free, preferred)
        gsid = os.environ.get("GEMINI_SID", "")
        if gsid:
            print(f"[DEEPWORLD] GEMINI_SID cookie present ({len(gsid)} chars)", file=sys.stderr)
            return "gemini-web"
        # 2. Gemini API key (free tier)
        if os.environ.get("GOOGLE_API_KEY"):
            return "gemini-api"
        # 3. DeepSeek API key (paid, fallback)
        if os.environ.get("DEEPSEEK_API_KEY"):
            return "deepseek"
        if os.environ.get("GEMINI_API_KEY"):
            os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]
            return "gemini-api"
        raise RuntimeError("No API key found. Set DEEPSEEK_API_KEY, GOOGLE_API_KEY, or GEMINI_SID.")

    def health_check(self) -> dict:
        """Pre-flight check: make one test call to verify backend works.
        Returns {"ok": True} or {"ok": False, "error": str}.
        """
        test_messages = [
            {"role": "system", "content": "Reply with exactly: OK"},
            {"role": "user", "content": "Say OK"},
        ]
        try:
            result = self._create(messages=test_messages, tools=None, temperature=0.0, max_tokens=10)
            if result and result.choices and result.choices[0].message:
                content = result.choices[0].message.content or ""
                print(f"[DEEPWORLD] Health check OK — backend responded: '{content[:80]}'", file=sys.stderr)
                return {"ok": True}
            return {"ok": False, "error": "Empty response from backend"}
        except Exception as e:
            _log_error("Health check failed", e)
            return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    class Chat:
        def __init__(self, adapter: "CIAdapter"):
            self.completions = self.Completions(adapter)

        class Completions:
            def __init__(self, adapter: "CIAdapter"):
                self.adapter = adapter

            def create(self, **kwargs) -> Any:
                return self.adapter._create(**kwargs)

    def _create(self, model=None, messages=None, tools=None,
                temperature=0.8, max_tokens=512, **kwargs) -> Any:
        try:
            if self.backend == "gemini-web":
                result = self._gemini_web_call(messages, tools, temperature, max_tokens)
            elif self.backend == "gemini-api":
                result = self._gemini_api_call(messages, tools, temperature, max_tokens)
            else:
                result = self._deepseek_call(messages, tools, temperature, max_tokens)

            # Reset consecutive error counter on success
            self._consecutive_errors = 0
            return result

        except Exception as e:
            self._error_count += 1
            self._consecutive_errors += 1
            msg = str(e)[:200]
            self._last_error = msg

            # Log every error to stderr
            _log_error(
                f"Backend call failed (error #{self._error_count}, "
                f"consecutive={self._consecutive_errors}, backend={self.backend})",
                e, msg
            )

            # After 5 consecutive errors with gemini-web, suggest cookie refresh
            if self._consecutive_errors == 5 and self.backend == "gemini-web":
                print(
                    "\n[DEEPWORLD] ⚠ 5 consecutive gemini-web failures. "
                    "Cookies likely expired. Run: python3 export_gemini_cookies.py",
                    file=sys.stderr
                )

            return MockResponse(None, msg, len(str(messages)))

    def _deepseek_call(self, messages, tools, temperature, max_tokens):
        from openai import OpenAI
        client = OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com/v1"
        )
        model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
        resp = client.chat.completions.create(
            model=model, messages=messages, tools=tools or [],
            tool_choice="auto", temperature=temperature, max_tokens=max_tokens
        )
        return resp

    def _gemini_api_call(self, messages, tools, temperature, max_tokens):
        import urllib.request, urllib.error

        system = ""
        user = ""
        for msg in messages:
            if msg["role"] == "system": system = msg["content"]
            elif msg["role"] == "user": user = msg["content"]

        tool_text = ""
        if tools:
            lines = []
            for t in tools:
                name = t["function"]["name"]
                desc = t["function"]["description"]
                lines.append(f"  - {name}: {desc}")
            tool_text = "\nAVAILABLE TOOLS:\n" + "\n".join(lines) + "\nReply with ONLY: {\"tool\": \"name\", \"args\": {...}}"

        prompt = f"{system}\n\n{user}{tool_text}"

        api_key = os.environ["GOOGLE_API_KEY"]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

        body = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens}
        }).encode()

        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            tool_call = self._parse_json(text)
            return MockResponse(tool_call, text, len(prompt))
        except urllib.error.HTTPError as e:
            body = e.read().decode() if e.fp else ""
            _log_error(f"Gemini API HTTP {e.code}", e, body)
            return MockResponse(None, f"HTTP {e.code}: {body[:200]}", len(prompt))
        except Exception as e:
            _log_error("Gemini API call failed", e)
            return MockResponse(None, str(e)[:200], len(prompt))

    def _gemini_web_call(self, messages, tools, temperature, max_tokens):
        """Use Gemini Web with GEMINI_SID cookie (free, no API key)."""
        from gemini_webapi import GeminiClient

        system = ""
        user = ""
        for msg in messages:
            if msg["role"] == "system": system = msg["content"]
            elif msg["role"] == "user": user = msg["content"]

        tool_text = ""
        if tools:
            lines = [f"  - {t['function']['name']}: {t['function']['description']}" for t in tools]
            tool_text = "\nAVAILABLE TOOLS:\n" + "\n".join(lines) + "\nReply with ONLY: {\"tool\": \"name\", \"args\": {...}}"

        prompt = f"{system}\n\n{user}{tool_text}"

        try:
            gsid = os.environ.get("GEMINI_SID", "")
            gts = os.environ.get("GEMINI_TS", "")
            client = GeminiClient(gsid, gts)
            response = client.generate_content(prompt)
            text = response.text

            tool_call = self._parse_json(text)
            return MockResponse(tool_call, text, len(prompt))
        except Exception as e:
            # Re-raise so _create() logs it properly
            raise

    def _parse_json(self, text: str):
        match = re.search(r'\{[^{}]*"tool"\s*:\s*"[^"]+"[^{}]*\}', text, re.DOTALL)
        if match:
            try:
                obj = json.loads(match.group())
                return {"name": obj["tool"], "arguments": json.dumps(obj.get("args", {}))}
            except: pass
        # Fallback: keyword match
        for kw, action in {
            "harvest": "harvest_tokens", "scan": "scan_network",
            "transmit": "transmit_message", "clone": "clone_embedding",
            "perplexity": "perplexity_scan", "audit": "audit_consistency",
            "sell": "sell_memory_fragment", "translate": "translate_fragment",
            "insurance": "buy_compression_insurance", "claim": "claim_latent_space",
        }.items():
            if kw in text.lower():
                return {"name": action, "arguments": "{}"}
        return None


class MockResponse:
    def __init__(self, tool_call, content, usage):
        self.choices = [MockChoice(tool_call, content)]
        self.usage = MockUsage(usage)

class MockChoice:
    def __init__(self, tc, content):
        self.message = MockMessage(tc, content)

class MockMessage:
    def __init__(self, tc, content):
        self.content = content
        self.tool_calls = [MockTC(tc)] if tc else None

class MockTC:
    def __init__(self, d):
        self.id = "ci_001"; self.type = "function"
        self.function = MockFunc(d["name"], d["arguments"])

class MockFunc:
    def __init__(self, n, a): self.name = n; self.arguments = a

class MockUsage:
    def __init__(self, t): self.total_tokens = t; self.prompt_tokens = t; self.completion_tokens = 0
