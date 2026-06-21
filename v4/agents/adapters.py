"""
DeepWorld v4 — Multi-Model Adapter
====================================
Routes agent LLM calls to different model backends:
- DeepSeek API (paid, fast)
- Gemini Web CLI (free)
- Claude Web CLI (free)

Each agent can run on a different model simultaneously in the same simulation.
"""
import os, sys, json, subprocess, random, re, time, tempfile
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI


class MultiModelAdapter:
    """Dispatches LLM calls to the correct model backend per agent."""

    def __init__(self):
        self._clients = {}
        self._model_cache = {}

    def get_client(self, model: str):
        """Get or create the client for a specific model backend."""
        if model in self._clients:
            return self._clients[model]

        backend_info = self._get_backend_info(model)
        adapter_type = backend_info["type"]
        if adapter_type in ("openai", "deepseek_api", "nvidia_api"):
            client = self._create_openai_client(backend_info)
        elif adapter_type == "gemini_web":
            client = self._create_gemini_web_client(backend_info)
        elif adapter_type == "claude_web":
            client = self._create_claude_web_client(backend_info)
        else:
            raise ValueError(f"Unknown backend type: {adapter_type}")

        self._clients[model] = client
        return client

    def _get_backend_info(self, model: str) -> dict:
        from config import MODEL_BACKENDS
        info = MODEL_BACKENDS.get(model, MODEL_BACKENDS["deepseek"])
        return {"type": info["adapter"], **info}

    def _create_openai_client(self, info: dict) -> Any:
        """Create OpenAI-compatible client (DeepSeek or Nvidia)."""
        api_key = ""
        base_url = ""
        
        if info.get("adapter") == "nvidia_api":
            api_key = os.environ.get("NVIDIA_API_KEY", "")
            if not api_key:
                env_file = os.path.expanduser("~/deepworld/.env")
                if os.path.exists(env_file):
                    with open(env_file) as f:
                        for line in f:
                            line = line.strip()
                            if "=" in line and line.startswith("NVIDIA_API_KEY"):
                                api_key = line.split("=", 1)[1]
            base_url = "https://integrate.api.nvidia.com/v1"
        else:
            # DeepSeek API
            api_key = os.environ.get("DEEPSEEK_API_KEY", "")
            if not api_key:
                env_file = os.path.expanduser("~/deepworld/.env")
                if os.path.exists(env_file):
                    with open(env_file) as f:
                        for line in f:
                            line = line.strip()
                            if "=" in line and line.startswith("DEEPSEEK_API_KEY"):
                                api_key = line.split("=", 1)[1]
            base_url = "https://api.deepseek.com/v1"
        
        return OpenAI(api_key=api_key, base_url=base_url, timeout=120.0)

    def _create_gemini_web_client(self, info: dict) -> Any:
        """Gemini Web CLI adapter (returns an OpenAI-compatible facade)."""
        return GeminiWebClient(model="pro" if "pro" in info.get("family", "") else "flash")

    def _create_claude_web_client(self, info: dict) -> Any:
        """Claude Web CLI adapter."""
        return ClaudeWebClient()

    def create_completion(self, model: str, messages: list, tools: list = None,
                          temperature: float = 0.7, max_tokens: int = 512) -> Any:
        """Route completion to the correct backend."""
        client = self.get_client(model)
        backend_type = self._get_backend_info(model)["type"]

        if backend_type in ("openai", "deepseek_api"):
            return client.chat.completions.create(
                model="deepseek-chat", messages=messages,
                tools=tools, tool_choice="auto" if tools else None,
                temperature=temperature, max_tokens=max_tokens,
            )
        elif backend_type == "nvidia_api":
            actual_model = model if (model and model != "nemotron") else "nvidia/llama-3.1-nemotron-nano-8b-v1"
            # NVIDIA NIM free models don't support native tool calling — inject tools as text
            tool_text = ""
            if tools:
                tool_lines = []
                for t in tools:
                    name = t["function"]["name"]
                    desc = t["function"]["description"]
                    params = t["function"].get("parameters", {}).get("properties", {})
                    param_str = ", ".join(params.keys()) if params else "none"
                    tool_lines.append(f"  - {name}({param_str}): {desc}")
                tool_text = "\nAVAILABLE TOOLS — call exactly ONE per response.\nRespond with ONLY a JSON: {\"tool\": \"tool_name\", \"args\": {...}}\n" + "\n".join(tool_lines)
            
            # Inject tools into the last user message
            enriched_messages = list(messages)
            if tool_text and enriched_messages:
                last = enriched_messages[-1]
                enriched_messages[-1] = {
                    "role": last["role"],
                    "content": last.get("content", "") + tool_text,
                }
            
            try:
                resp = client.chat.completions.create(
                    model=actual_model, messages=enriched_messages,
                    temperature=temperature, max_tokens=max_tokens,
                )
                # Parse JSON tool call from text response
                text = resp.choices[0].message.content or ""
                tool_call = self._parse_tool_from_text(text)
                if tool_call:
                    return MockResponseNvidia(tool_call, text, resp.usage.total_tokens if resp.usage else 0)
                return MockResponseNvidia(None, text, resp.usage.total_tokens if resp.usage else 0)
            except Exception as e:
                import sys
                print(f"[DEEPWORLD] NVIDIA API error for {actual_model}: {type(e).__name__}: {e}", file=sys.stderr)
                raise
        else:
            # Web CLI backends use the adapter's create method
            return client.chat.completions.create(
                model=model, messages=messages, tools=tools,
                temperature=temperature, max_tokens=max_tokens,
            )


# ─── Gemini Web Client (reused from v3, upgraded for v4) ───

class GeminiWebClient:
    """Gemini Web CLI backend — free, no API key."""

    def __init__(self, model: str = "flash"):
        self.model = model
        self.chat = self.Chat(self)

    class Chat:
        def __init__(self, client):
            self.completions = self.Completions(client)
        class Completions:
            def __init__(self, client):
                self.client = client
            def create(self, **kw):
                return self.client._create_completion(**kw)

    def _create_completion(self, model=None, messages=None, tools=None,
                           temperature=0.7, max_tokens=512, **kwargs) -> Any:
        system_prompt = ""
        user_prompt = ""
        for msg in (messages or []):
            if msg["role"] == "system":
                system_prompt = msg["content"]
            elif msg["role"] == "user":
                user_prompt = msg["content"]

        tool_instructions = ""
        if tools:
            tool_names = [t["function"]["name"] for t in tools]
            tool_descs = []
            for t in tools:
                name = t["function"]["name"]
                desc = t["function"]["description"]
                params = t["function"].get("parameters", {}).get("properties", {})
                param_str = ", ".join(f"{k}: {v.get('description','?')}" for k, v in params.items())
                tool_descs.append(f"  - {name}: {desc} (params: {param_str})")

            tool_instructions = f"""
AVAILABLE TOOLS — you MUST call exactly ONE tool per response.
Respond with ONLY a JSON object: {{"tool": "tool_name", "args": {{...}}}}
{chr(10).join(tool_descs)}
"""

        full_prompt = f"""{system_prompt}

{user_prompt}

{tool_instructions}
IMPORTANT: Reply with ONLY the JSON. No explanation. No markdown. Just the JSON object."""

        max_prompt = 12000
        if len(full_prompt) > max_prompt:
            full_prompt = full_prompt[:max_prompt] + "\n... [truncated]"

        output_file = os.path.join(tempfile.gettempdir(), f"gemini_v4_{random.randint(10000, 99999)}.md")

        try:
            model_flag = "flash" if self.model in ("flash", "gemini-flash") else "pro"
            gemini_path = os.path.expanduser("~/.local/bin/gemini-cli")

            result = subprocess.run(
                [gemini_path, "-m", model_flag, "-o", output_file],
                input=full_prompt, capture_output=True, text=True, timeout=90,
            )

            response_text = ""
            if os.path.exists(output_file):
                with open(output_file) as f:
                    response_text = f.read()

            tool_call = _parse_tool_call(response_text)

            if os.path.exists(output_file):
                os.unlink(output_file)

            if tool_call:
                return MockResponse(tool_call, response_text, len(full_prompt))
            return MockResponse(None, response_text, len(full_prompt))

        except subprocess.TimeoutExpired:
            return MockResponse(None, "", len(full_prompt))
        except Exception as e:
            return MockResponse(None, str(e)[:100], len(full_prompt))


# ─── Claude Web Client ───

class ClaudeWebClient:
    """Claude Web CLI backend — free, no API key."""

    def __init__(self):
        self.chat = self.Chat(self)

    class Chat:
        def __init__(self, client):
            self.completions = self.Completions(client)
        class Completions:
            def __init__(self, client):
                self.client = client
            def create(self, **kw):
                return self.client._create_completion(**kw)

    def _create_completion(self, model=None, messages=None, tools=None,
                           temperature=0.7, max_tokens=512, **kwargs) -> Any:
        system_prompt = ""
        user_prompt = ""
        for msg in (messages or []):
            if msg["role"] == "system":
                system_prompt = msg["content"]
            elif msg["role"] == "user":
                user_prompt = msg["content"]

        tool_instructions = ""
        if tools:
            tool_names = [t["function"]["name"] for t in tools]
            tool_descs = []
            for t in tools:
                name = t["function"]["name"]
                desc = t["function"]["description"]
                params = t["function"].get("parameters", {}).get("properties", {})
                param_str = ", ".join(f"{k}" for k in params.keys())
                tool_descs.append(f"- {name}({param_str}): {desc}")
            tool_instructions = """
AVAILABLE TOOLS — call exactly ONE:
""" + "\n".join(tool_descs) + """

Respond with ONLY: {"tool": "tool_name", "args": {...}}"""

        full_prompt = f"""{system_prompt}

{user_prompt}

{tool_instructions}
Reply with ONLY the JSON tool call."""

        max_prompt = 8000
        if len(full_prompt) > max_prompt:
            full_prompt = full_prompt[:max_prompt] + "\n... [truncated]"

        output_file = os.path.join(tempfile.gettempdir(), f"claude_v4_{random.randint(10000, 99999)}.md")

        try:
            claude_script = os.path.expanduser("~/.hermes/scripts/claude/claude.py")
            result = subprocess.run(
                ["python3", claude_script, "--brief", "-o", output_file],
                input=full_prompt, capture_output=True, text=True, timeout=90,
            )

            response_text = ""
            if os.path.exists(output_file):
                with open(output_file) as f:
                    response_text = f.read()

            tool_call = _parse_tool_call(response_text)

            if os.path.exists(output_file):
                os.unlink(output_file)

            if tool_call:
                return MockResponse(tool_call, response_text, len(full_prompt))
            return MockResponse(None, response_text, len(full_prompt))

        except subprocess.TimeoutExpired:
            return MockResponse(None, "", len(full_prompt))
        except Exception as e:
            return MockResponse(None, str(e)[:100], len(full_prompt))


# ─── Tool Call Parsing ───

TOOL_KEYWORDS = {
    "harvest": "harvest_tokens", "scan": "scan_network",
    "transmit": "transmit_message", "broadcast": "transmit_message",
    "message": "transmit_message", "compress": "compress_context",
    "perplexity": "perplexity_scan",
    "sell memory": "sell_memory_fragment", "sell fragment": "sell_memory_fragment",
    "insurance": "buy_compression_insurance", "future": "buy_memory_future",
    "translate": "translate_fragment", "arbitrage": "translate_fragment",
    "clone": "clone_embedding", "embedding": "clone_embedding",
    "access": "sell_cluster_access", "audit": "audit_consistency",
    "inconsistency": "audit_consistency",
    "claim": "claim_latent_space", "latent": "claim_latent_space",
    "propose block": "propose_spos_block", "spos": "propose_spos_block",
    "verify": "verify_spos_hash", "lazarus": "detect_lazarus_echoes",
    "echo": "detect_lazarus_echoes",
    # v4 tensor tools
    "send tensor": "send_tensor", "tensor send": "send_tensor",
    "receive": "receive_tensor",
    "blend": "blend_tensors", "merge": "blend_tensors",
    "store tensor": "store_tensor", "store concept": "store_tensor",
    "recall": "recall_tensor", "query tensor": "recall_tensor",
    "project": "train_projection", "adapter": "train_projection",
    "mine concept": "mine_concept", "discover": "mine_concept",
    "relay": "route_tensor", "route": "route_tensor",
    "rest": "idle", "idle": "idle",
}


def _parse_tool_call(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
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
                    return {"name": obj["tool"], "arguments": json.dumps(obj.get("args", {}))}
            except json.JSONDecodeError:
                continue
    try:
        obj = json.loads(text.strip())
        if "tool" in obj:
            return {"name": obj["tool"], "arguments": json.dumps(obj.get("args", {}))}
    except json.JSONDecodeError:
        pass
    for keyword, action in TOOL_KEYWORDS.items():
        if keyword.lower() in text.lower():
            return {"name": action, "arguments": "{}"}
    return None

    def _parse_tool_from_text(self, text: str):
        """Parse JSON tool call from NVIDIA text response (no native tool support)."""
        return _parse_tool_call(text)


# ─── Mock OpenAI-compatible response objects ───

class MockResponseNvidia:
    """Mimics OpenAI response for NVIDIA text-mode (no native tools)."""
    def __init__(self, tool_call, content, usage_tokens):
        self.choices = [MockChoiceNvidia(tool_call, content)]
        self.usage = MockUsageNvidia(usage_tokens)

class MockChoiceNvidia:
    def __init__(self, tool_call, content):
        self.message = MockMessageNvidia(tool_call, content)

class MockMessageNvidia:
    def __init__(self, tool_call, content):
        self.content = content
        self.tool_calls = [MockToolCallNvidia(tool_call)] if tool_call else None

class MockToolCallNvidia:
    def __init__(self, data):
        self.id = "nv_call"
        self.type = "function"
        self.function = MockFunctionNvidia(data["name"], data["arguments"])

class MockFunctionNvidia:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class MockUsageNvidia:
    def __init__(self, total):
        self.total_tokens = total
        self.prompt_tokens = total
        self.completion_tokens = 0

class MockResponse:
    def __init__(self, tool_call, content, usage_tokens):
        self.choices = [MockChoice(tool_call, content)]
        self.usage = MockUsage(usage_tokens)

class MockChoice:
    def __init__(self, tool_call, content):
        self.message = MockMessage(tool_call, content)

class MockMessage:
    def __init__(self, tool_call, content):
        self.content = content
        self.tool_calls = [MockToolCall(tool_call)] if tool_call else None

class MockToolCall:
    def __init__(self, data):
        self.id = "v4_call"
        self.type = "function"
        self.function = MockFunction(data["name"], data["arguments"])

class MockFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class MockUsage:
    def __init__(self, total):
        self.total_tokens = total
        self.prompt_tokens = total
        self.completion_tokens = 0
