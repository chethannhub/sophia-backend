"""
Google Gemini LLM client — uses google-genai SDK directly.

Wraps the SDK in a LangChain RunnableLambda so existing LCEL chains
(prompt | llm | StrOutputParser()) keep working without any changes.

Three presets:
  get_llm()       → default  balanced quality/speed
  get_fast_llm()  → fast     low latency, high volume
  get_smart_llm() → smart    highest quality output
"""
from functools import lru_cache

import google.genai as genai
import google.genai.types as genai_types
from langchain_core.messages import AIMessage
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import RunnableLambda

from .config import GOOGLE_API_KEY, GEMINI_MODEL_ID, GEMINI_FAST_MODEL_ID, GEMINI_SMART_MODEL_ID

_client = genai.Client(api_key=GOOGLE_API_KEY)


def _make_llm(model_id: str, temperature: float, max_tokens: int) -> RunnableLambda:
    """Return a RunnableLambda that calls Gemini via google-genai SDK."""

    def _call(input_val):
        # Accept PromptValue (from LCEL prompt), str, or list[BaseMessage]
        if isinstance(input_val, PromptValue):
            text = input_val.to_string()
        elif isinstance(input_val, str):
            text = input_val
        elif isinstance(input_val, list):
            text = "\n".join(
                m.content if hasattr(m, "content") else str(m) for m in input_val
            )
        else:
            text = str(input_val)

        resp = _client.models.generate_content(
            model=model_id,
            contents=text,
            config=genai_types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )
        # resp.text is None when finish_reason is MAX_TOKENS (output was truncated)
        # Fall back to extracting partial text from candidates
        text_out = resp.text
        if text_out is None and resp.candidates:
            parts = resp.candidates[0].content.parts if resp.candidates[0].content else None
            if parts:
                text_out = "".join(p.text for p in parts if hasattr(p, "text") and p.text)
        return AIMessage(content=text_out or "")

    return RunnableLambda(_call)


@lru_cache(maxsize=8)
def get_llm(temperature: float = 0.7, max_tokens: int = 4096) -> RunnableLambda:
    """Default LLM — Gemini Flash. Use for: summarisation, chat, general tasks."""
    return _make_llm(GEMINI_MODEL_ID, temperature, max_tokens)


@lru_cache(maxsize=8)
def get_fast_llm(temperature: float = 0.5, max_tokens: int = 2048) -> RunnableLambda:
    """Fast LLM — Gemini Flash. Use for: high-volume, low-latency tasks."""
    return _make_llm(GEMINI_FAST_MODEL_ID, temperature, max_tokens)


@lru_cache(maxsize=8)
def get_smart_llm(temperature: float = 0.8, max_tokens: int = 8192) -> RunnableLambda:
    """Smart LLM — Gemini Flash. Use for: podcast dialogue generation, complex reasoning."""
    return _make_llm(GEMINI_SMART_MODEL_ID, temperature, max_tokens)
