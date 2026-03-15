"""
Centralised configuration for News_api.
All tuneable knobs live here — no magic strings scattered elsewhere.
"""
import os
from pathlib import Path

# Project root (parent of this package directory)
BASE_DIR = Path(__file__).parent.parent

# ─── Google Gemini ───────────────────────────────────────────────────────────
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

# Model used for summarisation and chat
GEMINI_MODEL_ID: str = os.getenv(
    "GEMINI_MODEL_ID",
    "gemini-2.5-flash",
)

# Fast model for quick / high-volume calls
GEMINI_FAST_MODEL_ID: str = os.getenv(
    "GEMINI_FAST_MODEL_ID",
    "gemini-2.5-flash",
)

# High-quality model for podcast dialogue generation
GEMINI_SMART_MODEL_ID: str = os.getenv(
    "GEMINI_SMART_MODEL_ID",
    "gemini-2.5-flash",
)

# ─── Local Embeddings (sentence-transformers) ────────────────────────────────
EMBEDDING_MODEL_NAME: str = "BAAI/bge-base-en-v1.5"

# ─── Piper TTS ───────────────────────────────────────────────────────────────
PIPER_SAMPLE_RATE: int = 22050
PIPER_VOICES: dict[str, str] = {
    "en": str(BASE_DIR / "piper" / "en_US-amy-medium.onnx"),
    "en_US-amy-medium": str(BASE_DIR / "piper" / "en_US-amy-medium.onnx"),  # Female
    "en_US-lessac-medium": str(BASE_DIR / "piper" / "en_US-lessac-medium.onnx"),  # Male
    "hi": str(BASE_DIR / "piper" / "hi_IN-priyamvada-medium.onnx"),
    "te": str(BASE_DIR / "piper" / "te_IN-maya-medium.onnx"),
}

# ─── Storage Paths ───────────────────────────────────────────────────────────
TEXT_DIR = BASE_DIR / "text"
SUMMARIZATION_DIR = TEXT_DIR / "summarization"
DB_DIR = BASE_DIR / "db"
CHATS_DIR = BASE_DIR / "chats"
AUDIO_DIR = BASE_DIR / "summarized" / "audio"
AUDIO_TEXT_DIR = BASE_DIR / "summarized" / "text"

# ─── Podcast Speakers ────────────────────────────────────────────────────────
PODCAST_SPEAKERS: list[dict] = [
    {
        "name": "Andrew Krepthy",
        "description": (
            "Senior AI expert from Stanford University; "
            "worked at Tesla, OpenAI, and currently at Google"
        ),
        "voice_lang": "en",
        "voice_model": "en_US-lessac-medium",  # Male voice
    },
    {
        "name": "Smithi",
        "description": (
            "Researcher at Google DeepMind; "
            "tech enthusiast who loves discussing the latest in AI and technology"
        ),
        "voice_lang": "en",
        "voice_model": "en_US-amy-medium",  # Female voice
    },
]
