from utils.llm_client import ask_json


def explain_music(text_input, ai_profile, final_profile, overrides, music_prompt):
    """Generate a human-readable explanation of how input became music.

    Returns dict with:
    - narrative: 2-3 sentence explanation
    - timeline: list of {step, description, emotion} for Plotly chart
    """
    sources = ", ".join(ai_profile.get("sources", ["text"]))
    emotion = ai_profile.get("emotion", "neutral")
    override_str = ", ".join(overrides) if overrides else "none"

    prompt = f"""You are explaining to a user how their input was turned into music.

Input sources: {sources}
Detected emotion: {emotion}
AI profile: energy={ai_profile.get('energy')}, style={ai_profile.get('style')}, warmth={ai_profile.get('warmth')}, arc={ai_profile.get('arc')}
User overrides: {override_str}
Final profile: energy={final_profile.get('energy')}, style={final_profile.get('style')}, warmth={final_profile.get('warmth')}, arc={final_profile.get('arc')}
Music prompt: "{music_prompt[:200]}"

Return ONLY a JSON object with:
- narrative: 2-3 sentences explaining how the input emotion shaped the music. Mention the emotion, any overrides, and the resulting feel. Be warm and conversational.
- timeline: a list of exactly 5 objects, each with:
  - step: short label (e.g. "Input Analysis", "Emotion Detection", "Profile Tuning", "Prompt Creation", "Music Generation")
  - description: one sentence about what happened at this step
  - emotion: the dominant emotion at this stage (one word)

Return ONLY valid JSON, no other text."""

    return ask_json(prompt)
