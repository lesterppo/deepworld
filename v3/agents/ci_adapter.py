"""
CI adapter — headless agent backend for GitHub Actions.
Reads API keys from environment only (no browser, no .env file).
Supports: DEEPSEEK_API_KEY, GOOGLE_API_KEY (Gemini free tier).
"""

import json, os, subprocess, random, re, tempfile, time
from typing import Any


class CIAdapter:
    """Headless backend for GitHub Actions. Supports DeepSeek and Gemini."""

    def __init__(self):
        self.backend = self._detect_backend()

    def _detect_backend(self) -> str:
        # 1. Gemini Web cookies (free, preferred)
        if os.environ.get("GEMINI_SID"):
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
        if self.backend == "gemini-web":
            return self._gemini_web_call(messages, tools, temperature, max_tokens)
        elif self.backend == "gemini-api":
            return self._gemini_api_call(messages, tools, temperature, max_tokens)
        else:
            return self._deepseek_call(messages, tools, temperature, max_tokens)

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

        # Build prompt from messages
        system = ""
        user = ""
        for msg in messages:
            if msg["role"] == "system": system = msg["content"]
            elif msg["role"] == "user": user = msg["content"]

        # Tools as text
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
        except Exception as e:
            return MockResponse(None, str(e)[:200], len(prompt))

    def _gemini_web_call(self, messages, tools, temperature, max_tokens):
        """Use Gemini Web with GEMINI_SID cookie (free, no API key)."""
        from gemini_webapi import GeminiClient

        # Build prompt
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
            client = GeminiClient(os.environ["GEMINI_SID"], os.environ.get("GEMINI_TS", ""))
            response = client.generate_content(prompt)
            text = response.text

            tool_call = self._parse_json(text)
            return MockResponse(tool_call, text, len(prompt))
        except Exception as e:
            return MockResponse(None, str(e)[:200], len(prompt))

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
