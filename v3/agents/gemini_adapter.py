"""
Gemini Web CLI adapter — free backend for AI-native simulation.
Wraps gemini-cli behind an OpenAI-compatible interface.
No API keys needed — uses browser cookies.
"""

import json, os, subprocess, time, random, re, tempfile
from typing import List, Dict, Any


class GeminiWebClient:
    """OpenAI-compatible client backed by gemini-web-cli (free)."""

    def __init__(self, model: str = "flash"):
        self.model = model
        self.chat = self.Chat(self)

    class Chat:
        def __init__(self, client: "GeminiWebClient"):
            self.completions = self.Completions(client)

        class Completions:
            def __init__(self, client: "GeminiWebClient"):
                self.client = client

            def create(self, *args, **kwargs) -> Any:
                return self.client._create_completion(*args, **kwargs)

    def _create_completion(self, model=None, messages=None, tools=None,
                           temperature=0.7, max_tokens=512, **kwargs) -> Any:
        """Call gemini-cli and parse response."""

        # Build prompt from messages
        system_prompt = ""
        user_prompt = ""
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            elif msg["role"] == "user":
                user_prompt = msg["content"]

        # If tools provided, embed them in the prompt
        tool_instructions = ""
        if tools:
            tool_names = [t["function"]["name"] for t in tools]
            tool_descriptions = []
            for t in tools:
                name = t["function"]["name"]
                desc = t["function"]["description"]
                params = t["function"].get("parameters", {}).get("properties", {})
                param_str = ", ".join(f"{k}: {v.get('description','?')}" for k, v in params.items())
                tool_descriptions.append(f"  - {name}: {desc} (params: {param_str})")

            tool_instructions = f"""
AVAILABLE TOOLS — you MUST call exactly ONE tool per response.
Respond with ONLY a JSON object: {{"tool": "tool_name", "args": {{...}}}}
{chr(10).join(tool_descriptions)}
"""

        full_prompt = f"""{system_prompt}

{user_prompt}

{tool_instructions}
IMPORTANT: Reply with ONLY the JSON. No explanation. No markdown. Just the JSON object."""

        # Truncate to avoid exceeding limits
        max_prompt = 12000
        if len(full_prompt) > max_prompt:
            full_prompt = full_prompt[:max_prompt] + "\n... [truncated]"

        output_file = os.path.join(tempfile.gettempdir(), f"gemini_sim_out_{random.randint(10000,99999)}.md")

        try:
            model_flag = "flash" if self.model in ("flash", "gemini-flash", "gemini-2.0-flash") else "pro"
            gemini_path = os.path.expanduser("~/.local/bin/gemini-cli")

            cmd = [gemini_path, "-m", model_flag, "-o", output_file]
            # Use stdin for the prompt (avoids -f file issues in subprocess)
            result = subprocess.run(
                cmd,
                input=full_prompt, capture_output=True, text=True, timeout=90,
            )

            # Read response
            response_text = ""
            if os.path.exists(output_file):
                with open(output_file) as f:
                    response_text = f.read()

            # Parse JSON tool call from response
            tool_call = self._parse_tool_call(response_text)

            # Cleanup
            if os.path.exists(output_file):
                os.unlink(output_file)

            if tool_call:
                return MockResponse(tool_call, response_text, len(full_prompt))
            else:
                # No tool call — treat as idle
                return MockResponse(None, response_text, len(full_prompt))

        except subprocess.TimeoutExpired:
            return MockResponse(None, "", len(full_prompt))
        except Exception as e:
            return MockResponse(None, str(e)[:100], len(full_prompt))

    def _parse_tool_call(self, text: str) -> Dict[str, Any]:
        """Extract JSON tool call from Gemini response."""
        if not text:
            return None

        # Try to find JSON in the response
        # Look for {tool patterns
        patterns = [
            r'\{\s*"tool"\s*:\s*"[^"]+"\s*,\s*"args"\s*:\s*\{[^}]+\}\s*\}',
            r'\{[^}]*"tool"[^}]*\}',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                try:
                    obj = json.loads(match.group())
                    if "tool" in obj:
                        return {
                            "name": obj["tool"],
                            "arguments": json.dumps(obj.get("args", {})),
                        }
                except json.JSONDecodeError:
                    continue

        # Try parsing the entire response as JSON
        try:
            obj = json.loads(text.strip())
            if "tool" in obj:
                return {
                    "name": obj["tool"],
                    "arguments": json.dumps(obj.get("args", {})),
                }
        except json.JSONDecodeError:
            pass

        # Fallback: use keyword matching to guess action
        for keyword, action in TOOL_KEYWORDS.items():
            if keyword.lower() in text.lower():
                return {
                    "name": action,
                    "arguments": "{}",
                }

        return None


# Keyword fallback mapping for when JSON parsing fails
TOOL_KEYWORDS = {
    "harvest": "harvest_tokens",
    "scan": "scan_network",
    "inspect": "scan_network",
    "transmit": "transmit_message",
    "broadcast": "transmit_message",
    "message": "transmit_message",
    "compress": "compress_context",
    "perplexity": "perplexity_scan",
    "sell memory": "sell_memory_fragment",
    "sell fragment": "sell_memory_fragment",
    "insurance": "buy_compression_insurance",
    "future": "buy_memory_future",
    "translate": "translate_fragment",
    "arbitrage": "translate_fragment",
    "clone": "clone_embedding",
    "embedding": "clone_embedding",
    "access": "sell_cluster_access",
    "audit": "audit_consistency",
    "inconsistency": "audit_consistency",
    "claim": "claim_latent_space",
    "latent": "claim_latent_space",
    "propose block": "propose_spos_block",
    "spos": "propose_spos_block",
    "verify": "verify_spos_hash",
    "lazarus": "detect_lazarus_echoes",
    "echo": "detect_lazarus_echoes",
    "rest": "idle",
    "idle": "idle",
}


class MockResponse:
    """Mimics OpenAI response object."""

    def __init__(self, tool_call: Dict, content: str, usage_tokens: int):
        self.choices = [MockChoice(tool_call, content)]
        self.usage = MockUsage(usage_tokens)


class MockChoice:
    def __init__(self, tool_call: Dict, content: str):
        self.message = MockMessage(tool_call, content)


class MockMessage:
    def __init__(self, tool_call: Dict, content: str):
        self.content = content
        self.tool_calls = [MockToolCall(tool_call)] if tool_call else None


class MockToolCall:
    def __init__(self, data: Dict):
        self.id = "call_0001"
        self.type = "function"
        self.function = MockFunction(data["name"], data["arguments"])


class MockFunction:
    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments


class MockUsage:
    def __init__(self, total: int):
        self.total_tokens = total
        self.prompt_tokens = total
        self.completion_tokens = 0
