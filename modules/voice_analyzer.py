import tempfile
import whisper
from utils.llm_client import ask_json

_whisper_model = None


def _get_whisper():
    global _whisper_model
    if _whisper_model is None:
        _whisper_model = whisper.load_model("base")
    return _whisper_model


def transcribe_audio(audio_bytes):
    """Transcribe audio bytes with Whisper. Returns the transcript string."""
    model = _get_whisper()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    result = model.transcribe(tmp_path)
    return result.get("text", "").strip()


def analyze_voice(audio_bytes):
    """Transcribe audio with Whisper, then analyze mood via Gemini. Returns mood dict."""
    transcript = transcribe_audio(audio_bytes)

    if not transcript:
        return {
            "transcript": "",
            "mood": "neutral",
            "energy": 0.5,
            "source": "voice",
        }

    prompt = f"""Analyze the following spoken transcript for its emotional content.
Return ONLY a JSON object with these keys:
- mood: one word describing the dominant mood
- energy: float 0.0 to 1.0 (0=very calm, 1=very intense)

Transcript: "{transcript}"

Return ONLY valid JSON, no other text."""

    mood = ask_json(prompt)
    mood["transcript"] = transcript
    mood["source"] = "voice"
    return mood
