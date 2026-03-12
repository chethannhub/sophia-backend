"""
Translation layer using AWS Translate.

Single responsibility: translate text between languages.
This module is a thin wrapper so the frontend can request content in any
supported language without changes to other modules.

Credentials: auto-loaded from ~/.aws/credentials via boto3.
"""
import boto3

from .config import AWS_REGION

_client = None

SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese (Simplified)",
    "ja": "Japanese",
    "ar": "Arabic",
}


def _get_client():
    global _client
    if _client is None:
        _client = boto3.client("translate", region_name=AWS_REGION)
    return _client


def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> str:
    """Translate text to target_lang using AWS Translate.

    Args:
        text:        Input text to translate.
        target_lang: BCP-47 language code of the desired output (e.g. "hi", "es").
        source_lang: BCP-47 source language code, or "auto" for auto-detection.

    Returns:
        Translated text string.

    Notes:
        If source and target are both English the original text is returned
        immediately without an API call.
    """
    if target_lang == "en" and source_lang in ("en", "auto"):
        return text

    response = _get_client().translate_text(
        Text=text,
        SourceLanguageCode=source_lang,
        TargetLanguageCode=target_lang,
    )
    return response["TranslatedText"]


def get_supported_languages() -> dict[str, str]:
    """Return a copy of the supported language code → name mapping."""
    return SUPPORTED_LANGUAGES.copy()
