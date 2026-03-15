"""
Audio generation pipeline.
Single responsibility: orchestrate conversation generation + Piper TTS
to produce a merged MP3 podcast file from selected article IDs.
"""
import datetime
import json
import os
import uuid
from pathlib import Path

from pydub import AudioSegment

from .tts_engine import get_tts_engine
from .config import AUDIO_DIR, AUDIO_TEXT_DIR, PODCAST_SPEAKERS
from . import create_con_text


# ── internal helpers ──────────────────────────────────────────────────────

def _wav_to_mp3(wav_path: str, mp3_path: str) -> str:
    """Convert a WAV file to MP3 (removes the original WAV)."""
    AudioSegment.from_wav(wav_path).export(mp3_path, format="mp3")
    os.remove(wav_path)
    if not os.path.exists(mp3_path) or os.path.getsize(mp3_path) == 0:
        raise RuntimeError(f"MP3 conversion produced empty file: {mp3_path}")
    return mp3_path


def _merge_audio_files(mp3_files: list, output_dir: str) -> str:
    """Concatenate sorted MP3 segments into a single output.mp3."""
    combined = AudioSegment.empty()
    for path in sorted(mp3_files):
        combined += AudioSegment.from_file(path)
    output_path = os.path.join(output_dir, "output.mp3")
    combined.export(output_path, format="mp3")
    return output_path


def _cleanup(files: list) -> None:
    for f in files:
        if os.path.exists(f):
            os.remove(f)


# ── public API ──────────────────────────────────────────────────────────────

def generate_audio(article_ids: list, output_folder: str = None) -> str:
    """Generate a podcast-style MP3 for the given article IDs.

    Pipeline:
      1. generate_conversation()  — Claude creates a dialogue JSON
      2. Piper TTS               — each turn → WAV → MP3
      3. pydub merge             — all segments → output.mp3
      4. Cache result            — skip re-generation on repeat calls

    Args:
        article_ids:    List of article IDs to include.
        output_folder:  Destination directory. Defaults to AUDIO_DIR.

    Returns:
        Absolute path to the merged output.mp3.
    """
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_TEXT_DIR.mkdir(parents=True, exist_ok=True)

    if output_folder is None:
        output_folder = str(AUDIO_DIR)

    history_path = Path(output_folder) / "history.json"
    if not history_path.exists():
        history_path.write_text(json.dumps({"history": []}))

    history = json.loads(history_path.read_text())
    for entry in history["history"]:
        cached_path = entry["path"]
        if entry["urls"] == article_ids and os.path.exists(cached_path) and os.path.getsize(cached_path) > 0:
            return cached_path

    # Step 1: Generate conversation JSON via LLM
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
    conversation_file = str(AUDIO_TEXT_DIR / f"{timestamp}.json")
    create_con_text.generate_conversation(article_ids, conversation_file)

    # Step 2: Synthesise each dialogue turn
    with open(conversation_file) as f:
        conversation_data = json.load(f)

    unique_id = str(uuid.uuid4())
    output_dir = os.path.join(output_folder, unique_id)
    os.makedirs(output_dir, exist_ok=True)

    # Create speaker engines: use voice_model if available, else fall back to voice_lang
    speaker_engines = {}
    for s in PODCAST_SPEAKERS:
        voice_key = s.get("voice_model", s["voice_lang"])
        speaker_engines[s["name"]] = get_tts_engine(voice_key)
        print(f"[TTS] Loaded speaker '{s['name']}' with voice model: {voice_key}")
    
    default_engine = get_tts_engine("en")
    print(f"[TTS] Default engine loaded: en")

    audio_files = []
    for i, turn in enumerate(conversation_data["conversation"]):
        speaker = turn["speaker"]
        text = turn["text"]
        engine = speaker_engines.get(speaker, default_engine)

        wav_path = os.path.join(output_dir, f"turn_{i:04d}.wav")
        mp3_path = os.path.join(output_dir, f"turn_{i:04d}.mp3")
        
        print(f"\n[TTS] Turn {i}: Speaker='{speaker}', Text length={len(text)} chars")
        print(f"[TTS] Using engine voice language: {engine.lang}")
        
        engine.synthesize_to_wav(text, wav_path)
        if not os.path.exists(wav_path) or os.path.getsize(wav_path) <= 44:
            print(f"[TTS] ⚠️  WARNING: TTS produced empty/corrupt WAV for turn {i}, skipping.")
            if os.path.exists(wav_path):
                os.remove(wav_path)
            continue
        
        wav_size = os.path.getsize(wav_path)
        print(f"[TTS] ✓ WAV created: {wav_size} bytes")
        
        _wav_to_mp3(wav_path, mp3_path)
        mp3_size = os.path.getsize(mp3_path)
        print(f"[TTS] ✓ MP3 created: {mp3_size} bytes")
        
        audio_files.append(mp3_path)

    # Step 3: Merge all segments
    print(f"\n[TTS] Merging {len(audio_files)} audio segments...")
    merged = _merge_audio_files(audio_files, output_dir)
    merged_size = os.path.getsize(merged)
    print(f"[TTS] ✓ Merged output: {merged} ({merged_size} bytes)")
    
    _cleanup(audio_files)
    print(f"[TTS] ✓ Cleaned up temporary files")

    # Step 4: Cache the result
    history["history"].append({"urls": article_ids, "path": merged})
    history_path.write_text(json.dumps(history, indent=2))
    print(f"[TTS] ✓ Cached result in history.json")

    return merged
    with open(output_folder + "/history.json", "r") as file:
        history = json.load(file)
    for i in history["history"]:
        if i["urls"] == urls:
            return i["path"]

    input_file = f"summarized/text/{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')}.json"
    create_con_text.get_context(urls ,input_file)
    tts = TextToSpeech()

    out = tts.process_conversation(input_file, output_folder)

    history["history"].append({"urls": urls , "path": out})
    with open(output_folder+"/history.json" , "w") as file:
        json.dump(history , file , indent=4)
    return out