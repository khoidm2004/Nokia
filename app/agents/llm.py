from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

# llama-3.3-70b-versatile was retired from Groq (404 model_not_found,
# confirmed live on 2026-10-27) - gpt-oss-120b is the strongest model
# left on this key, so it now does the two reasoning-heavy agents, and
# gpt-oss-20b keeps the original big/small tiering for the bounded
# critic retry loop.
EXTRACTOR_MODEL = "openai/gpt-oss-120b"
RELATIONSHIP_MODEL = "openai/gpt-oss-120b"
CRITIC_MODEL = "openai/gpt-oss-20b"


class StructuredOutputError(RuntimeError):
    """The model answered without making the forced tool call."""


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8").strip()


def _client():
    """Build the Groq client lazily. Importing this module must never need a key."""
    import groq  # local import keeps module import cheap

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Export it before running the pipeline:\n"
            "    export GROQ_API_KEY=gsk_..."
        )
    return groq.Groq(api_key=api_key)


def call_tool(
    *,
    model: str,
    system_prompt: str,
    user_content: str,
    tool_name: str,
    tool_description: str,
    parameters_schema: dict[str, Any],
    temperature: float = 0.0,
    max_completion_tokens: int = 6000,
) -> dict[str, Any]:
    """Make one Groq chat call with a single forced tool and return its parsed
    arguments as a dict. Raises StructuredOutputError if no tool call came back."""
    client = _client()
    tools = [{
        "type": "function",
        "function": {
            "name": tool_name,
            "description": tool_description,
            "parameters": parameters_schema,
        },
    }]
    tool_choice = {"type": "function", "function": {"name": tool_name}}
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
    ]

    last_exc: Exception | None = None
    for attempt in range(2):  # one retry on transient failures only
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                max_completion_tokens=max_completion_tokens,
            )
            message = resp.choices[0].message
            tool_calls = getattr(message, "tool_calls", None)
            if not tool_calls:
                raise StructuredOutputError(
                    f"Model {model} returned no tool call for '{tool_name}'."
                )
            return json.loads(tool_calls[0].function.arguments)
        except StructuredOutputError:
            raise
        except Exception as exc:  # network / rate limit / 5xx
            last_exc = exc
            if attempt == 0:
                time.sleep(2)
                continue
            raise RuntimeError(f"Groq call to {model} failed: {exc}") from exc
    raise RuntimeError(f"Groq call to {model} failed: {last_exc}")
