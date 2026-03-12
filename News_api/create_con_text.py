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

from .llm_client import get_smart_llm
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
    """Extract the first JSON object from an LLM response string."""
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON object found in LLM response")
    return text[start:end]


def generate_conversation(article_ids: list, output_file: str) -> str:
    """Generate a podcast-style conversation JSON for the given articles.

    Args:
        article_ids:  List of article IDs to include.
        output_file:  Destination path for the output JSON.

    Returns:
        The output_file path.
    """
    news_file = _get_most_recent_news_file()
    with open(news_file) as f:
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
    conversation = json.loads(_extract_json(raw))

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(conversation, f, indent=2)
    return output_file


