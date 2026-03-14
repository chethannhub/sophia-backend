"""
Cross-platform Piper TTS engine.

Backends:
  macOS / Linux : Python piper-tts backend  (PiperVoice.load)   [line 21]
  Windows       : piper.exe subprocess fallback

Default sample rate: 22050                                        [line 37]

Voices loaded from config (config.py:30):
  en → piper/en_US-amy-medium.onnx
  hi → piper/hi_IN-priyamvada-medium.onnx
  te → piper/te_IN-maya-medium.onnx
"""
import os
import platform
import subprocess
import sys
import wave
from pathlib import Path

from .config import PIPER_VOICES, PIPER_SAMPLE_RATE


class PiperTTSEngine:
    """Synthesise text to WAV using the Piper TTS engine.

    Usage:
        engine = PiperTTSEngine(lang="en")
        engine.synthesize_to_wav("Hello world", "/tmp/out.wav")
    """

    DEFAULT_SAMPLE_RATE: int = PIPER_SAMPLE_RATE  # 22050 Hz            [line 37]

    def __init__(self, lang: str = "en") -> None:
        self.lang = lang
        self.voice_path: str = PIPER_VOICES.get(lang, PIPER_VOICES["en"])
        self._voice = None
        self._backend: str = self._detect_backend()
        if self._backend == "python":
            self._load_python_voice()

    # ── private ──────────────────────────────────────────────────────────────

    def _detect_backend(self) -> str:
        """Select backend: Python piper-tts on macOS/Linux, subprocess on Windows."""
        if platform.system() == "Windows":              # line 21 fallback
            return "subprocess"
        try:
            import piper  # noqa: F401 — probe import only
            return "python"                              # line 21 primary
        except ImportError:
            return "subprocess"

    def _load_python_voice(self) -> None:
        from piper import PiperVoice
        self._voice = PiperVoice.load(self.voice_path)

    def _synthesize_python(self, text: str, output_wav: str) -> None:
        with wave.open(output_wav, "w") as wav_file:
            self._voice.synthesize_wav(text, wav_file)

    def _synthesize_subprocess(self, text: str, output_wav: str) -> None:
        command = [sys.executable, "-m", "piper"]
        result = subprocess.run(
            [*command, "--model", self.voice_path, "--output_file", output_wav],
            input=text,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Piper subprocess error (exit {result.returncode}): "
                f"{result.stderr}"
            )

    # ── public ───────────────────────────────────────────────────────────────

    def synthesize_to_wav(self, text: str, output_wav: str) -> str:
        """Synthesise text and write a WAV file at output_wav.

        Args:
            text:       Text to speak.
            output_wav: Destination WAV file path.

        Returns:
            The output_wav path (for chaining).
        """
        Path(output_wav).parent.mkdir(parents=True, exist_ok=True)
        if self._backend == "python":
            self._synthesize_python(text, output_wav)
        else:
            self._synthesize_subprocess(text, output_wav)
        return output_wav


def get_tts_engine(lang: str = "en") -> PiperTTSEngine:
    """Factory: return a PiperTTSEngine for the given language code."""
    return PiperTTSEngine(lang=lang)
