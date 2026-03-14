"""
Podcast conversation generator.
Single responsibility: use AWS Bedrock (Claude) to produce a structured JSON
dialogue from article content, ready for TTS synthesis.
"""
import glob
import json
import os
from pathlib import Path

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .llm_client import get_fast_llm, get_smart_llm
from .config import TEXT_DIR, PODCAST_SPEAKERS

_CONVERSATION_PROMPT = PromptTemplate(
    input_variables=[
        "context",
        "speaker_1", "speaker_1_desc",
        "speaker_2", "speaker_2_desc",
    ],
    template="""Generate a professional, technically rich podcast conversation between two experts.

Speakers:
- {speaker_1}: {speaker_1_desc}
- {speaker_2}: {speaker_2_desc}

Rules:
1. Minimum 25 dialogue turns total.
2. Cover ALL major topics present in the context.
3. Demonstrate deep technical knowledge and genuine insight.
4. Include real-world implications, challenges, and future directions.
5. Return ONLY valid JSON — no markdown fences, no extra text.

Context:
{context}

JSON format:
{{
    "conversation": [
        {{"speaker": "{speaker_1}", "text": "..."}},
        {{"speaker": "{speaker_2}", "text": "..."}},
        ...
    ],
    "sources": [
        {{"title": "...", "url": "...", "date": "..."}}
    ]
}}""",
)


def _get_most_recent_news_file() -> str:
    """Return the path of the most recently modified news JSON in TEXT_DIR."""
    files = [f for f in glob.glob(str(TEXT_DIR / "*")) if os.path.isfile(f)]
    if not files:
        raise FileNotFoundError(f"No news files found in {TEXT_DIR}")
    return max(files, key=os.path.getmtime)


def _extract_json(text: str) -> str:
    """Extract the first valid JSON object from an LLM response string."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].lstrip()

    decoder = json.JSONDecoder()
    for index, char in enumerate(cleaned):
        if char != "{":
            continue
        try:
            _, end = decoder.raw_decode(cleaned[index:])
            return cleaned[index:index + end]
        except json.JSONDecodeError:
            continue

    raise ValueError("No valid JSON object found in LLM response")


def _repair_conversation_json(raw: str) -> str:
    repair_prompt = PromptTemplate(
        input_variables=["raw"],
        template="""Convert the following content into valid JSON only.

Requirements:
1. Return exactly one JSON object.
2. Preserve the original meaning and speaker turns.
3. Use this schema exactly:
   {
     \"conversation\": [{\"speaker\": \"...\", \"text\": \"...\"}],
     \"sources\": [{\"title\": \"...\", \"url\": \"...\", \"date\": \"...\"}]
   }
4. Escape any quotes inside string values.
5. Do not add markdown fences or commentary.

Content:
{raw}
""",
    )
    chain = repair_prompt | get_fast_llm(temperature=0.1, max_tokens=8192) | StrOutputParser()
    repaired = chain.invoke({"raw": raw})
    return _extract_json(repaired)


def _parse_conversation_payload(raw: str) -> dict:
    try:
        return json.loads(_extract_json(raw))
    except (ValueError, json.JSONDecodeError):
        repaired = _repair_conversation_json(raw)
        payload = json.loads(repaired)
        if not isinstance(payload.get("conversation"), list):
            raise ValueError("Conversation payload missing 'conversation' list")
        return payload


def generate_conversation(article_ids: list, output_file: str) -> str:
    """Generate a podcast-style conversation JSON for the given articles.

    Args:
        article_ids:  List of article IDs to include.
        output_file:  Destination path for the output JSON.

    Returns:
        The output_file path.
    """
    news_file = _get_most_recent_news_file()
    with open(news_file, encoding="utf-8") as f:
        data = json.load(f)

    context_parts = [
        article.get("content", "")
        for article in data.get("Articles", [])
        if article["id"] in article_ids
    ]
    context = "\n\n".join(context_parts)

    s1, s2 = PODCAST_SPEAKERS[0], PODCAST_SPEAKERS[1]
    chain = _CONVERSATION_PROMPT | get_smart_llm(temperature=0.8, max_tokens=8192) | StrOutputParser()
    raw = chain.invoke({
        "context": context,
        "speaker_1": s1["name"],
        "speaker_1_desc": s1["description"],
        "speaker_2": s2["name"],
        "speaker_2_desc": s2["description"],
    })
    conversation = _parse_conversation_payload(raw)

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(conversation, f, indent=2, ensure_ascii=False)
    return output_file


