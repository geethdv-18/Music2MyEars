from utils.llm_client import ask_json
from modules.feedback import get_learned_defaults, get_emotion_profile


def _range_clamp(ai_value, learned_range):
    """Nudge AI value toward learned range if outside it.

    If AI value is within range, keep it. If outside, blend 70% toward
    the nearest boundary (preserves AI's contextual judgment).
    """
    lo, hi = learned_range
    if lo <= ai_value <= hi:
        return ai_value
    # Outside range — nudge toward nearest boundary
    nearest = lo if ai_value < lo else hi
    return round(ai_value * 0.3 + nearest * 0.7)


def fuse_emotions(mood_list):
    """Merge mood signals into one ai_profile with 4 slider dimensions."""
    sources = [m.get("source", "unknown") for m in mood_list]

    mood_descriptions = "\n".join(
        f"- Source: {m.get('source')}, Moods: {m.get('moods', [m.get('mood')])}, Energy: {m.get('energy')}"
        for m in mood_list
    )

    prompt = f"""You are an emotion analyst for a music generation system.

Given these mood signals from user inputs:
{mood_descriptions}

Produce ONE unified emotional profile as JSON:
{{
  "emotions": ["<list of 1-3 detected emotions, most dominant first>"],
  "emotion": "<single most dominant emotion>",
  "energy": <0-100 integer>,
  "style": <0-100 integer, 0=minimal sparse, 100=cinematic epic>,
  "warmth": <0-100 integer, 0=deep dark moody, 100=bright sparkling>,
  "arc": <0-100 integer, 0=steady constant, 100=big dramatic build>
}}

Rules:
- Blend ALL detected emotions into the slider values, not just the dominant one
- "sad but hopeful" → moderate energy (hope lifts it), warm style, gentle build arc
- "angry and frustrated" → high energy, bright/harsh warmth, big build
- "peaceful and grateful" → low energy, warm, steady arc
- The slider values should reflect the MIX of emotions, not just the dominant one
- Base values on the actual emotional content, not random guesses

Return ONLY the JSON object."""

    result = ask_json(prompt)
    result["sources"] = sources

    # Apply learned knowledge — range-clamping instead of blind overwrite
    emotion = result.get("emotion", "")
    emo_profile = get_emotion_profile(emotion)

    if emo_profile:
        # Use range-clamping: keep AI value if in range, nudge if outside
        pref = emo_profile.get("preferred_params", {})
        for key in ["energy", "style", "warmth", "arc"]:
            range_key = f"{key}_range"
            if range_key in pref and key in result:
                result[key] = _range_clamp(result[key], pref[range_key])
    else:
        # Fallback: simple averaging with learned defaults
        learned = get_learned_defaults(emotion)
        if learned:
            for key in ["energy", "style", "warmth", "arc"]:
                if key in learned and key in result:
                    result[key] = round((result[key] + learned[key]) / 2)

    return result
