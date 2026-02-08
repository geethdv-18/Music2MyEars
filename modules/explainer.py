from utils.llm_client import ask_json
from modules.feedback import get_learned_rules, get_emotion_profile


def explain_music(text_input, ai_profile, final_profile, overrides, music_prompt):
    """Generate a human-readable explanation of how input became music.

    Returns dict with:
    - narrative: 2-3 sentence explanation
    - key_descriptors: list of 3-4 short strings extracted from the music prompt
    """
    sources = ", ".join(ai_profile.get("sources", ["text"]))
    emotion = ai_profile.get("emotion", "neutral")
    override_str = ", ".join(overrides) if overrides else "none"

    # Build learning context
    rules = get_learned_rules()
    reflection_count = rules.get("reflection_count", 0)
    emotions_learned = list(rules.get("emotion_profiles", {}).keys())
    emo_profile = get_emotion_profile(emotion)

    learning_context = ""
    if reflection_count > 0:
        learning_context = f"""
Learning status:
- The system has completed {reflection_count} reflection cycle(s), learning from past sessions.
- Emotions with specific knowledge: {', '.join(emotions_learned) if emotions_learned else 'none yet'}"""
        if emo_profile:
            principles = emo_profile.get("prompt_principles", [])
            if principles:
                learning_context += f"\n- For \"{emotion}\", the system has learned: {'; '.join(principles[:2])}"

    prompt = f"""You are explaining to a user how their input was turned into music.

Input sources: {sources}
Detected emotion: {emotion}
AI profile: energy={ai_profile.get('energy')}, style={ai_profile.get('style')}, warmth={ai_profile.get('warmth')}, arc={ai_profile.get('arc')}
User overrides: {override_str}
Final profile: energy={final_profile.get('energy')}, style={final_profile.get('style')}, warmth={final_profile.get('warmth')}, arc={final_profile.get('arc')}
Music prompt: "{music_prompt[:200]}"
{learning_context}
Return ONLY a JSON object with:
- narrative: 2-3 sentences explaining how the input emotion shaped the music. Mention the emotion, any overrides, and the resulting feel. Be warm and conversational.{' If the system has learned from past sessions, briefly mention how past feedback influenced this generation.' if reflection_count > 0 else ''}
- key_descriptors: a list of 3-4 short strings (2-3 words each) extracted from the music prompt that describe the most important musical qualities (e.g. "acoustic piano", "120 BPM", "bright tone", "slow build")

Return ONLY valid JSON, no other text."""

    return ask_json(prompt)
