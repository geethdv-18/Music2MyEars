import io
import os
import scipy.io.wavfile
from transformers import AutoProcessor, MusicgenForConditionalGeneration

MODEL_ID = os.getenv("HF_MODEL_ID", "facebook/musicgen-small")

_model = None
_processor = None


def _load_model():
    global _model, _processor
    if _model is None:
        print(f"Loading {MODEL_ID}... (first time takes ~1-2 min to download)")
        _processor = AutoProcessor.from_pretrained(MODEL_ID)
        _model = MusicgenForConditionalGeneration.from_pretrained(MODEL_ID)
        print("Model loaded.")
    return _model, _processor


def _generate_one(prompt, max_new_tokens=256):
    """Generate audio from a text prompt. Returns wav bytes."""
    model, processor = _load_model()
    inputs = processor(text=[prompt], padding=True, return_tensors="pt")
    audio_values = model.generate(**inputs, do_sample=True, max_new_tokens=max_new_tokens)

    sample_rate = model.config.audio_encoder.sampling_rate
    audio_numpy = audio_values[0, 0].cpu().numpy()

    buf = io.BytesIO()
    scipy.io.wavfile.write(buf, rate=sample_rate, data=audio_numpy)
    return buf.getvalue()


def generate_music(prompt, num_variations=1, max_new_tokens=128):
    """Generate variations from a prompt. Returns list of wav byte buffers."""
    results = [_generate_one(prompt, max_new_tokens=max_new_tokens)]
    if num_variations >= 2:
        results.append(_generate_one(prompt + " with subtle variation in rhythm and texture", max_new_tokens=max_new_tokens))
    return results


if __name__ == "__main__":
    test_prompt = "A gentle lo-fi piano melody with warm vinyl crackle and soft drums"
    print(f"Testing with prompt: {test_prompt}")
    print(f"Model: {MODEL_ID}")
    print()

    results = generate_music(test_prompt)

    os.makedirs("data/generated", exist_ok=True)
    for i, audio_bytes in enumerate(results):
        path = f"data/generated/test_v{i + 1}.wav"
        with open(path, "wb") as f:
            f.write(audio_bytes)
        size_kb = len(audio_bytes) / 1024
        print(f"Saved {path} ({size_kb:.1f} KB)")

    print("\nDone. Play the files to verify audio quality.")
